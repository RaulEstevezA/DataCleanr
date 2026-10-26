# DataCleanr · Escritorio

Versión de escritorio de DataCleanr: Python + PySide6 + Pandas + OpenPyXL + RapidFuzz.

> [!NOTE]
> **En desarrollo.** Se construirá después de la versión web, con el mismo comportamiento: implementará los casos de prueba de [`shared/test-cases/`](../shared/README.md) y leerá los mismos perfiles de limpieza.

Qué hace la herramienta y su filosofía están en el [README principal](../README_es.md).

## Ejecutar en local

Requisitos: Python 3.11 o superior.

```bash
cd desktop
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m pytest                   # tests (casos compartidos de shared/test-cases/)
ruff check .                       # análisis estático
python -m datacleanr               # ejecutar la aplicación
```

## Estructura

```
datacleanr/
  core/          Lógica sin interfaz: cada módulo equivale a uno de web/src/core/
  io/            Lectura y escritura de CSV, Excel, JSON y XML
tests/           Tests con pytest, leyendo los casos de shared/test-cases/
pyproject.toml   Dependencias y configuración
```

[Volver al README principal](../README_es.md)
