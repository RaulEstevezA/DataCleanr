# Roadmap

No se publicará nada hasta que estén terminadas tanto la versión web como la de escritorio.

Las funciones comunes a ambas versiones se especifican en `shared/test-cases/` (ver [shared/README.md](../shared/README.md)).

## v0.1 — Web básica
- [x] Proyecto React + TypeScript + Vite
- [x] Cargar CSV
- [x] Mostrar datos en tabla y columnas detectadas
- [x] Seleccionar columna
- [x] Transformaciones: trim, minúsculas, mayúsculas, Title Case, colapsar espacios
- [x] Vista previa `original → propuesto` antes de aplicar
- [x] Exportar CSV limpio
- [ ] Despliegue en el portfolio (`raulesteveza.github.io/tools/DataCleanr/`)

## Más adelante
- Importar Excel y JSON
- [x] Unificar valores parecidos en una columna (fuzzy matching)
- [x] Filas duplicadas exactas
- Posibles filas duplicadas (fuzzy entre varias columnas)
- [x] Normalización de teléfonos
- [x] Normalización de fechas
- [x] Normalización de importes
- Perfiles/reglas de limpieza
- Historial de transformaciones, undo/redo
- Versión desktop en Python
- Instaladores desktop (Windows/macOS/Linux) publicados en GitHub Releases, con enlace de descarga desde la versión web
