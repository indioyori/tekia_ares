# tekia_ares
Sistema Integrado: aplicación web FastAPI con BD SQLite, FAISS, spaCy, y análisis cruzado (La Grieta). Todos los servicios están marcados ✅ en el estado interno. ARES TEKTRON v4.0 / 100tifiko: herramienta CLI sin BD ni UI. Tiene el filtro epistémico más sofisticado (3 capas vs 1 de TEKIA).

---Enseguida es el objetivo que buscamos. los archivos que agregué al repositorio son los que tengo, para que revises y veas cuales sirven, cuales no y cuales faltan-----


OBJETIVO DEL QUE NO DEBES SALIRTE:
FASE DE TRIPLE FILTRADO
Capa 1 — Estado de los datos
El corpus de documentos del proyecto contiene DOS sistemas distintos que abordan el mismo objetivo:

TEKIA Sistema Integrado: aplicación web FastAPI con BD SQLite, FAISS, spaCy, y análisis cruzado (La Grieta). Todos los servicios están marcados ✅ en el estado interno.
ARES TEKTRON v4.0 / 100tifiko: herramienta CLI sin BD ni UI. Tiene el filtro epistémico más sofisticado (3 capas vs 1 de TEKIA).

El bug de datos confirmado: bias_vocab/hegemonic_terms.txt tiene todos los términos en UNA línea separados por comas. El código usa .read_text().lower().split() (split por espacio). El token "inversión," nunca iguala a "inversión" → clasificación siempre devuelve 0 vs 0 → todo es "situated" → La Grieta nunca tiene documentos HEG para cruzar.
Capa 2 — Algoritmo de búsqueda y clasificación
La clasificación en TEKIA usa dos mecanismos en serie: (1) HEG_DOMAINS (12-19 dominios hardcoded) y (2) vocabulary scoring. El problema es que el fallback al vocabulario está roto por el bug de datos, y HEG_DOMAINS cubre solo medios nacionales grandes, no los regionales que aparecen en búsquedas locales de temas yoreme/yaqui.
El filtro de epistemico.py en 100tifiko es superior: usa 3 capas ordenadas (whitelist de fuente → score de términos territoriales/conflicto/epistémicos ponderados → densidad de realidad con fechas+cifras+actores). Este filtro es determinista, interpretable y auditable sin LLM.
Capa 3 — Estado del código
Bugs confirmados por lectura directa del código:

bias_vocab mal formateado → parser roto (2 min de fix)
notes.py importa rag_integration pero el archivo es integration.py → ImportError
alert_service.py usa Document.date → AttributeError (el campo es date_downloaded)
Safari cacha script.js viejo → botones [+HEG]/[+SIT] no renderizados

ÁRBOL DE DECISIONES
Hipótesis 1 (eliminada): El stack es incorrecto para el hardware. → Falsa. 2.7 GB de uso total en 8 GB. FastAPI + FAISS-CPU + MiniLM-L12 es el stack canónico para RAG soberano sin GPU. No hay alternativa más eficiente con las mismas capacidades.
Hipótesis 2 (eliminada): Los sistemas deben fusionarse en uno nuevo. → Falsa. TEKIA ya tiene la arquitectura completa. 100tifiko aporta el filtro epistémico y los módulos geográficos. La fusión es de capas, no de repositorios.
Hipótesis 3 (confirmada): El sistema está completo en arquitectura pero detenido por bugs de datos y de importación. La clasificación HEG/SIT debe migrar al filtro de epistemico.py. → Verdadera. Confirmado por lectura de fuentes.
</analizis_critico>


Estamos ejecutando este sistema, síguelo al pie de la letra, no te desvíes. 
Arquitectura Correcta — Veredicto Definitivo
Stack: correcto, no modificar
El stack del TEKIA_PLAN_IMPLEMENTACION.md es el correcto para iMac 2017 Intel 8GB macOS Ventura. No existe alternativa más adecuada dentro de las restricciones de hardware y soberanía. Puntos críticos verificados:
El modelo paraphrase-multilingual-MiniLM-L12-v2 es obligatorio (no all-MiniLM-L6-v2 que es inglés-céntrico). IndexFlatIP con dim=384 es correcto. FTS5 MATCH con mapping JSON para sincronía FAISS↔SQLite es la decisión correcta y ya está bien implementada.
Los dos sistemas no compiten — se complementan en capas distintas
100tifiko es un motor de cosecha epistémica con salida a archivos. TEKIA es el sistema de análisis, cuaderno y búsqueda vectorial con UI. La relación correcta entre ellos:
El filtro epistemico.py (3 capas: whitelist de fuente + score de términos ponderados + densidad de realidad) debe reemplazar la clasificación por HEG_DOMAINS dentro de rag.py de TEKIA. Es más robusto, modular, y ya está probado. Los módulos geográficos (noroeste_mx.py, latinoamerica.py) se convierten en configuración de "lente epistémica" seleccionable en la UI de TEKIA.
Los dossiers que genera 100tifiko se importan a TEKIA como documentos ya clasificados — el campo source_type toma directamente la clasificación del cosechador.
Los tres gaps reales (lo que falta construir)
Gap 1 — Upload manual de PDFs y análisis de documento individual. El endpoint POST /api/rag/documents/ existe en el backend pero no hay formulario multipart/form-data en la UI. Y GrietaService.generar() falla cuando doc_ids_heg o doc_ids_sit están vacíos — necesita un modo de análisis individual que muestre todos los indicadores disponibles y reserve el cruce para cuando haya contraparte.
Gap 2 — Sección "Documentos ya trabajados". No existe ni ruta /documentos ni template documentos.html. Es una vista de biblioteca: documentos ordenados por tema, con filtros, con acceso directo al análisis y a las notas vinculadas.
Gap 3 — Exportación a DOCX. El botón PDF en las notas está en la UI pero sin implementación verificada. Word (.docx) no está implementado. La librería python-docx (500 KB, sin dependencias pesadas) es suficiente.
Los cuatro bugs que detienen el sistema hoy
Se resuelven en este orden exacto antes de construir nada nuevo:
Bug #1 (2 minutos): En rag_service.py o donde se lean los vocabularios, reemplazar .read_text().lower().split() por lectura línea a línea. Y reformatear los archivos hegemonic_terms.txt y situated_terms.txt a un término por línea. Este único fix desbloquea la clasificación HEG/SIT y la Grieta.
Bug #2 (1 línea): En app/routers/notes.py, cambiar from ..services.rag_integration import RAGIntegration → from ..services.integration import RAGIntegration.
Bug #3 (1 línea): En alert_service.py, cambiar Document.date → Document.date_downloaded.
Bug #4 (1 línea): En app/templates/base.html, agregar ?v=4 a los scripts estáticos para romper el caché de Safari: <script src="/static/script.js?v=4"></script>.
La única mejora de retrieval justificada sin costo de RAM
BM25 híbrido via rank_bm25 (ya instalado como dependencia de otras librerías). Combinar FAISS (semántico) + BM25 (léxico) en search_service.py mejora significativamente la precisión del retrieval — especialmente para términos específicos como nombres propios yoreme/yaqui que el embedding puede no capturar bien. Costo: ~0 MB de RAM adicional, ~30 líneas de código.

Plan de acción — en orden de ejecución
El plan del TEKIA_PLAN_IMPLEMENTACION.md es el correcto como documento de control. Se añaden estas correcciones y adiciones al inicio de la secuencia:
Sesión 0-A (antes de cualquier módulo): Corregir los 4 bugs. Verificar que La Grieta genera correctamente con documentos de ambos tipos. Sin esto, los módulos 1-6 no tienen base firme.
Sesión 0-B: Integrar epistemico.py como clasificador primario en rag.py — reemplaza HEG_DOMAINS. Los módulos geográficos son configuración, no código duplicado.
Módulos 1-5: Seguir exactamente el plan existente. No modificar lo que ya funciona.
Módulo 6-A (adicional): GrietaService en modo individual — manejar doc_ids_heg = [] o doc_ids_sit = [] mostrando análisis disponibles sin el cruce.
Módulo 6-B (adicional): Formulario de upload manual de PDFs en la UI + endpoint multipart/form-data.
Módulo 7 (adicional): Página /documentos — biblioteca de documentos ya trabajados, organizada por tema.
Módulo 8 (adicional): Exportación DOCX en notas con python-docx.
El sistema no necesita rediseño. Necesita 4 correcciones de una línea, 1 corrección de datos de 2 minutos, y 3 módulos adicionales que ya tienen especificación clara en los documentos existentes.
