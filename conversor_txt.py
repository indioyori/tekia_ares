import hashlib, re
from pathlib import Path

CORPUS = Path("/Users/indioyori/Vault/01_activo/TEKTRON/corpus/Corpus_Tektron")
CF = ["cf_chl_opt", "challenges.cloudflare.com", "Enable JavaScript"]

MAPEO = [
    ("00_Core","00_Core"),
    ("01_Epistemolog\u00edas","01_epistemologias"),
    ("02_el_territorio","02_ia_territorio"),
    ("03_legal_territorial","03_legal_territorial"),
    ("04_Extractivismo","04_Extractivismo"),
    ("05_Energ\u00eda","05_energia"),
    ("06_geopolitica_tecnologica","06_geopolitica_tecnologica"),
    ("07_ciberseguridad","07_ciberseguridad"),
    ("08_Tecnologia_Supervivencia","08_Tecnologia_Supervivencia"),
    ("09_Soberania_Alimentaria","09_Soberania_Alimentaria"),
]

def leer_txt(f):
    if f.stat().st_size < 1024: return ""
    for enc in ["utf-8","latin-1"]:
        try: return f.read_text(encoding=enc)
        except: continue
    return ""

def basura(t): return not t or len(t.strip()) < 300 or any(m in t for m in CF)

ok = skip = 0
for src, dst in MAPEO:
    for tipo in ("HEGEMONICO","SITUADO"):
        dir_tipo = CORPUS / src / tipo
        if not dir_tipo.exists(): continue
        dir_md = CORPUS / dst / "markdown"
        dir_md.mkdir(parents=True, exist_ok=True)
        for f in sorted(dir_tipo.glob("*.txt")):
            if f.stat().st_size < 5120: skip += 1; continue
            texto = leer_txt(f)
            if basura(texto): print(f"  SKIP_CF {src}/{tipo}/{f.name}"); skip += 1; continue
            sha = hashlib.sha256(texto.encode()).hexdigest()[:16]
            stem = re.sub(r'(_dup\d+)+$','',f.stem); stem = re.sub(r'[^\w\-]','_',stem)[:60]
            out = dir_md / f"{sha}_{stem}.md"
            if out.exists(): print(f"  EXIST {f.name}"); skip += 1; continue
            out.write_text(
                f"---\nsha256: {sha}\nfuente: {f.name}\ntipo_epistemico: {tipo}\n---\n{texto}",
                encoding="utf-8")
            print(f"  OK {tipo}/{f.name}"); ok += 1

print(f"\n=== TXTs OK={ok} | SKIP={skip} ===")
