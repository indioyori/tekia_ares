# TEKIA + ARES TEKTRON — Mapa de archivos

## Dos sistemas en dos directorios separados

```
~/
├── tekia/                          ← TEKIA Sistema Integrado (FastAPI)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── document.py
│   │   │   ├── note.py
│   │   │   ├── tag.py
│   │   │   └── alert.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── rag_service.py
│   │   │   ├── grieta_service.py
│   │   │   ├── note_service.py
│   │   │   ├── alert_service.py
│   │   │   ├── crypto_service.py
│   │   │   ├── search_service.py
│   │   │   └── integration.py          ← OJO: NO "rag_integration.py"
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── rag.py
│   │   │   ├── notes.py
│   │   │   └── alerts.py
│   │   ├── static/
│   │   │   ├── styles.css
│   │   │   ├── script.js
│   │   │   └── marked.js               ← local, sin CDN
│   │   └── templates/
│   │       ├── base.html
│   │       ├── index.html
│   │       ├── rag.html
│   │       └── notes.html
│   ├── data/
│   │   ├── documents/
│   │   │   ├── hegemonic/              ← documentos hegemónicos descargados
│   │   │   └── situated/               ← documentos situados descargados
│   │   ├── embeddings/
│   │   │   ├── documents.faiss
│   │   │   └── documents_mapping.json
│   │   └── tekia.db
│   ├── models/
│   │   └── paraphrase-multilingual-MiniLM-L12-v2/
│   ├── keys/
│   │   └── secret.key                  ← NUNCA en git
│   ├── bias_vocab/
│   │   ├── hegemonic_terms.txt         ← 80 términos, UN TÉRMINO POR LÍNEA ← FIX CRÍTICO
│   │   └── situated_terms.txt          ← 80 términos, UN TÉRMINO POR LÍNEA ← FIX CRÍTICO
│   ├── fix_tekia_bugs.py               ← copiar aquí y ejecutar
│   ├── requirements.txt
│   ├── setup.sh
│   └── .gitignore
│
└── Workspace/
    └── Proyecto_Algoritmo/             ← ARES TEKTRON v4.0 (CLI)
        ├── 100tifiko.py                ← motor principal
        ├── patcher.py                  ← parches automáticos
        ├── registro_cosecha.log        ← log de sesiones
        ├── filtros/
        │   ├── __init__.py
        │   └── epistemico.py           ← filtro 3 capas
        ├── modulos/
        │   ├── __init__.py
        │   ├── noroeste_mx.py
        │   └── latinoamerica.py
        ├── cosechadores/
        │   ├── cosechador_ragflow.py
        │   └── cosechador_appropedia.py
        └── datos_crudos/               ← output del cosechador
```

---

## Archivos del proyecto Claude → dónde van en el Mac

| Archivo en proyecto Claude              | Destino en Mac                                    |
|-----------------------------------------|---------------------------------------------------|
| `tekia_source_completo.md`              | `~/tekia/docs/` (referencia, no es código)        |
| `TEKIA_PLAN_IMPLEMENTACION.md`          | `~/tekia/docs/` (control de sesiones)             |
| `tekia_arquitectura_detallada_fallas.html` | `~/tekia/docs/`                               |
| `100tifiko.py`                          | `~/Workspace/Proyecto_Algoritmo/`                 |
| `patcher.py`                            | `~/Workspace/Proyecto_Algoritmo/`                 |
| `epistemico.py`                         | `~/Workspace/Proyecto_Algoritmo/filtros/`         |
| `noroeste_mx.py`                        | `~/Workspace/Proyecto_Algoritmo/modulos/`         |
| `latinoamerica.py`                      | `~/Workspace/Proyecto_Algoritmo/modulos/`         |
| `cosechador_ragflow.py`                 | `~/Workspace/Proyecto_Algoritmo/cosechadores/`    |
| `cosechador_appropedia.py`              | `~/Workspace/Proyecto_Algoritmo/cosechadores/`    |
| `registro_cosecha.log`                  | `~/Workspace/Proyecto_Algoritmo/`                 |
| `fix_tekia_bugs.py` (este paquete)      | `~/tekia/`  ← EJECUTAR AQUÍ                       |
| `hegemonic_terms.txt` (este paquete)    | `~/tekia/bias_vocab/`                             |
| `situated_terms.txt` (este paquete)     | `~/tekia/bias_vocab/`                             |

---

## Comando para organizar ARES TEKTRON desde Terminal

```bash
cd ~/Workspace/Proyecto_Algoritmo

# Crear estructura si no existe
mkdir -p filtros modulos cosechadores

# Crear __init__.py si faltan
touch filtros/__init__.py modulos/__init__.py cosechadores/__init__.py

# Verificar
ls filtros/    # debe ver: __init__.py  epistemico.py
ls modulos/    # debe ver: __init__.py  noroeste_mx.py  latinoamerica.py

# Test rápido
python3 100tifiko.py listar
```

---

## Comando para verificar TEKIA después del fix

```bash
cd ~/tekia

# 1. Ejecutar correcciones
python3 fix_tekia_bugs.py

# 2. Verificar vocabulario
python3 -c "
from pathlib import Path
heg = list(Path('bias_vocab/hegemonic_terms.txt').open())
sit = list(Path('bias_vocab/situated_terms.txt').open())
print(f'HEG: {len(heg)} términos — primeros 3: {[l.strip() for l in heg[:3]]}')
print(f'SIT: {len(sit)} términos — primeros 3: {[l.strip() for l in sit[:3]]}')
"

# 3. Reiniciar servidor (Cmd+C primero si ya corre)
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES uvicorn app.main:app --port 8100

# 4. En Safari — forzar recarga: Cmd+Shift+R
# http://127.0.0.1:8100
```

---

## Archivos que DEBEN existir pero pueden faltar en ~/tekia/

Si algún archivo de servicio no existe aún, construirlo en orden del plan:

```
Módulo 0 → app/main.py, app/config.py, app/database.py, setup.sh
Módulo 1 → app/models/*.py
Módulo 2 → app/services/crypto_service.py
Módulo 3 → app/services/rag_service.py + bias_vocab/*.txt  ← YA CORREGIDOS
Módulo 4 → app/services/note_service.py
Módulo 5 → app/services/alert_service.py                   ← YA CORREGIDO
Módulo 6 → app/services/search_service.py
Módulo 7 → app/services/integration.py                     ← OJO: NO rag_integration.py
Módulo 8 → app/routers/rag.py, notes.py, alerts.py
Módulo 9 → app/templates/*.html, static/*.js, static/*.css
```

Para verificar qué módulos están presentes:
```bash
cd ~/tekia
find app/ -name "*.py" | sort
find app/templates/ -name "*.html" | sort
```
