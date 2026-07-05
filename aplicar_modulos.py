#!/usr/bin/env python3
"""
aplicar_modulos.py — Aplica rag.py, documentos.html y rutas a main.py/base.html
Ejecutar desde: ~/tekia/Primera y segunda prueba/
"""
import shutil, ast
from pathlib import Path

BASE = Path(__file__).parent
OK, FAIL = [], []

def ok(msg): print(f"  ✓  {msg}"); OK.append(msg)
def fail(msg, detalle=""): print(f"  ✗  {msg}  {detalle}"); FAIL.append(msg)

# ── 1. Copiar rag.py ──────────────────────────────────────
rag_nuevo = BASE / "rag.py"
rag_dest  = BASE / "app/routers/rag.py"
if not rag_nuevo.exists():
    fail("rag.py", "no encontrado junto a este script")
else:
    shutil.copy(rag_dest, rag_dest.with_suffix(".py.bak"))
    try:
        ast.parse(rag_nuevo.read_text())
        shutil.copy(rag_nuevo, rag_dest)
        ok("app/routers/rag.py — copiado con filtro ARES")
    except SyntaxError as e:
        fail("rag.py sintaxis", str(e))

# ── 2. Copiar documentos.html ─────────────────────────────
docs_nuevo = BASE / "documentos.html"
docs_dest  = BASE / "app/templates/documentos.html"
if not docs_nuevo.exists():
    fail("documentos.html", "no encontrado junto a este script")
else:
    shutil.copy(docs_nuevo, docs_dest)
    ok("app/templates/documentos.html — creado")

# ── 3. Agregar ruta /documentos en main.py ────────────────
main_py = BASE / "app/main.py"
if main_py.exists():
    codigo = main_py.read_text(encoding="utf-8")
    shutil.copy(main_py, main_py.with_suffix(".py.bak"))

    # Agregar ruta solo si no existe
    if '"/documentos"' not in codigo and "documentos" not in codigo:
        # Buscar la última ruta @app.get para insertar después
        ruta_nueva = '''
@app.get("/documentos")
def biblioteca(request: Request):
    return templates.TemplateResponse("documentos.html", {"request": request})
'''
        # Insertar después de /notes si existe, o al final antes del if __name__
        if '@app.get("/notes")' in codigo:
            codigo = codigo.replace(
                '@app.get("/notes")',
                ruta_nueva + '\n@app.get("/notes")',
                1
            )
        else:
            codigo += ruta_nueva
        main_py.write_text(codigo, encoding="utf-8")
        ok("app/main.py — ruta /documentos agregada")
    else:
        ok("app/main.py — ruta /documentos ya existe")
else:
    fail("app/main.py", "no encontrado")

# ── 4. Agregar link Documentos en base.html ───────────────
base_html = BASE / "app/templates/base.html"
if base_html.exists():
    html = base_html.read_text(encoding="utf-8")
    shutil.copy(base_html, base_html.with_suffix(".html.bak"))

    if '/documentos' not in html:
        link = '''    <a href="/documentos" class="nav-link {% block nav_docs %}{% endblock %}">
      <svg viewBox="0 0 16 16" fill="currentColor"><path d="M2 1h8l4 4v10H2V1zm7 0v4h4M5 7h6M5 9h6M5 11h4"/></svg>
      Documentos
    </a>'''
        # Insertar después del link de Cuaderno
        html = html.replace(
            'href="/notes" class="nav-link',
            'href="/notes" class="nav-link',
            1
        )
        # Insertar el nuevo link después del bloque de /notes
        target = 'href="/notes"'
        pos = html.find(target)
        if pos != -1:
            # Encontrar el cierre </a> de ese link
            cierre = html.find('</a>', pos)
            if cierre != -1:
                html = html[:cierre+4] + '\n' + link + html[cierre+4:]
                base_html.write_text(html, encoding="utf-8")
                ok("app/templates/base.html — link Documentos agregado al sidebar")
            else:
                fail("base.html", "no encontré </a> del link /notes")
        else:
            fail("base.html", "no encontré href=/notes")
    else:
        ok("app/templates/base.html — link Documentos ya existe")
else:
    fail("app/templates/base.html", "no encontrado")

# ── Resumen ───────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"  OK: {len(OK)}  |  Fallidos: {len(FAIL)}")
if FAIL:
    for f in FAIL:
        print(f"    · {f}")
print(f"{'='*50}")
if not FAIL:
    print("""
  Reinicia el servidor:
    OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES uvicorn app.main:app --port 8100

  Verifica en Safari (Cmd+Shift+R):
    http://127.0.0.1:8100/documentos
""")
