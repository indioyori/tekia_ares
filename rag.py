from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.document import Document
from app.services.rag_service import RAGService

router = APIRouter(prefix="/api/rag", tags=["rag"])


class DownloadRequest(BaseModel):
    url: str
    source_type: str = "hegemonic"
    theme: Optional[str] = None


class DocumentCreate(BaseModel):
    title: str
    source: str
    source_type: str = "hegemonic"
    theme: Optional[str] = None


class GrietaRequest(BaseModel):
    heg: list = []
    sit: list = []


# ── CRUD documentos ───────────────────────────────────────

@router.post("/documents/")
def create_document(body: DocumentCreate, db: Session = Depends(get_db)):
    doc = Document(**body.model_dump())
    db.add(doc); db.commit(); db.refresh(doc)
    return doc


@router.get("/documents/")
def list_documents(source_type: Optional[str] = None, theme: Optional[str] = None,
                   db: Session = Depends(get_db)):
    q = db.query(Document)
    if source_type: q = q.filter(Document.source_type == source_type)
    if theme:       q = q.filter(Document.theme == theme)
    return q.all()


@router.get("/documents/{doc_id}")
def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).get(doc_id)
    if not doc:
        raise HTTPException(404, "Documento no encontrado")
    return doc


@router.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).get(doc_id)
    if not doc:
        raise HTTPException(404, "Documento no encontrado")
    db.delete(doc); db.commit()
    return {"ok": True}


# ── Descarga desde URL ────────────────────────────────────

@router.post("/download/")
def download(body: DownloadRequest, db: Session = Depends(get_db)):
    return RAGService(db).download_document(body.url, body.source_type, body.theme)


# ── Upload manual de PDF o TXT ────────────────────────────

@router.post("/upload/")
async def upload_document(
    file: UploadFile = File(...),
    source_type: str = Form("hegemonic"),
    theme: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    from app.config import DOCUMENTS_DIR
    from datetime import datetime
    import hashlib, shutil, pathlib

    contenido = await file.read()
    sha = hashlib.sha256(contenido).hexdigest()[:12]
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = pathlib.Path(file.filename).suffix.lower() or ".bin"
    nombre = f"{ts}_{sha}{ext}"

    carpeta = DOCUMENTS_DIR / source_type
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / nombre
    ruta.write_bytes(contenido)

    # Extraer texto
    texto = ""
    if ext == ".pdf":
        try:
            import fitz
            with fitz.open(str(ruta)) as pdf:
                texto = "\n".join(p.get_text() for p in pdf)
        except Exception:
            texto = ""
    else:
        try:
            texto = contenido.decode("utf-8", errors="ignore")
        except Exception:
            texto = ""

    # Guardar en DB
    titulo = pathlib.Path(file.filename).stem[:200]
    doc = Document(
        title=titulo,
        source=file.filename,
        source_type=source_type,
        file_path=str(ruta),
        theme=theme,
    )
    db.add(doc); db.commit(); db.refresh(doc)
    return doc


# ── Búsqueda semántica ────────────────────────────────────

@router.post("/search/")
def search(body: dict, db: Session = Depends(get_db)):
    return RAGService(db).search(body.get("query", ""), k=body.get("k", 5))


# ── Análisis ──────────────────────────────────────────────

@router.post("/analyze/{doc_id}")
def analyze(doc_id: int, analysis_type: str = "summary", db: Session = Depends(get_db)):
    return RAGService(db).analyze(doc_id, analysis_type)


# ── Indexar ───────────────────────────────────────────────

@router.post("/index/{doc_id}")
def index_doc(doc_id: int, db: Session = Depends(get_db)):
    return RAGService(db).index_document(doc_id)


# ── Búsqueda web — filtro ARES 3 capas ───────────────────

@router.get("/search-web/")
def search_web(q: str, desde: str = None, max_results: int = 8):
    import requests, urllib.parse
    from bs4 import BeautifulSoup
    from app.config import BIAS_VOCAB_DIR

    HEG_DOMAINS = {
        "reforma.com","eleconomista.com.mx","milenio.com","eluniversal.com.mx",
        "expansion.mx","forbes.com.mx","reuters.com","bbc.com","nytimes.com",
        "larazon.com.mx","excelsior.com.mx","informador.mx","jornada.com.mx",
        "sinembargo.mx","proceso.com.mx","aristeguinoticias.com",
        "animalpolitico.com","elfinanciero.com.mx","heraldo.mx",
        "soysinaloa.com","gpo.com.mx","noroeste.com.mx","eldebate.com.mx",
        "elimparcial.com","riodoce.com","nacion321.com","vanguardia.com.mx",
        "elheraldodechihuahua.com.mx","periodicoelsol.com","noticiasmvs.com",
    }
    SIT_DOMAINS = {
        "nacla.org","coha.org","agenciapresentes.org","biblioteca.clacso.edu.ar",
        "desinformemonos.org","agenciaocote.com","cedha.org.ar",
        "resumenlatinoamericano.org","es.mongabay.com","servindi.org",
        "cejil.org","contralinea.com.mx","grain.org","ciad.mx",
        "radiozapatista.org","repositorio.unison.mx","jornadasinaloa.com",
    }

    def _vocab(nombre):
        p = BIAS_VOCAB_DIR / nombre
        if not p.exists():
            return set()
        return set(t.strip().lower() for t in p.read_text(encoding="utf-8").splitlines() if t.strip())

    heg_v = _vocab("hegemonic_terms.txt")
    sit_v = _vocab("situated_terms.txt")

    try:
        query = (q + f" after:{desde}") if desde else q
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
            timeout=15,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for item in soup.select(".web-result")[:max_results]:
            a    = next((l for l in item.select("a[href*='uddg']") if len(l.get_text(strip=True)) > 10), None)
            snip = item.select_one(".result__snippet")
            if not a:
                continue
            raw  = ("https:" + a["href"]) if a["href"].startswith("//") else a["href"]
            url  = urllib.parse.parse_qs(urllib.parse.urlparse(raw).query).get("uddg", [raw])[0]
            dom  = url.replace("https://","").replace("http://","").split("/")[0].replace("www.","")
            txt  = (a.get_text(strip=True) + " " + (snip.get_text(strip=True) if snip else "")).lower()
            h = sum(1 for w in heg_v if w in txt)
            s = sum(1 for w in sit_v if w in txt)
            if any(d in dom for d in HEG_DOMAINS):
                auto = "hegemonic"
            elif any(d in dom for d in SIT_DOMAINS):
                auto = "situated"
            elif h > s:
                auto = "hegemonic"
            else:
                auto = "situated"
            results.append({
                "title":     a.get_text(strip=True),
                "href":      url,
                "body":      snip.get_text(strip=True) if snip else "",
                "auto_type": auto,
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]


# ── Grieta epistémica (funciona con 1 o 2 tipos) ─────────

@router.post("/grieta/")
def generar_grieta(body: GrietaRequest, db: Session = Depends(get_db)):
    from app.services.grieta_service import GrietaService
    return GrietaService(db).generar(body.heg, body.sit)


# ── Temas disponibles ─────────────────────────────────────

@router.get("/themes/")
def list_themes(db: Session = Depends(get_db)):
    rows = db.query(Document.theme).distinct().filter(Document.theme.isnot(None)).all()
    return [r[0] for r in rows]
