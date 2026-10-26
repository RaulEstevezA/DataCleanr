# DataCleanr

[Volver](README.md) · [English](README_en.md)

Herramienta web que se ejecuta en el navegador para limpiar, normalizar y deduplicar datos CSV/Excel sin enviar archivos a ningún servidor.

> **Tus datos se procesan localmente.** Ningún archivo se envía a ningún servidor.

## ¿Qué hace?

DataCleanr ayuda a limpiar, normalizar y unificar datos sucios o inconsistentes antes de cargarlos en una base de datos u otro sistema:

- Espacios sobrantes, mayúsculas/minúsculas inconsistentes
- Valores equivalentes escritos de distinta forma (`TRANSGRAU`, `Trans Grau SL`, `Transgrau S.L.`)
- Fechas, teléfonos y números con formatos distintos
- Valores vacíos, duplicados y posibles duplicados

**Filosofía:** nunca se modifica nada sin que el usuario lo vea. Cada cambio se muestra como `valor original → valor propuesto` y el usuario decide si lo acepta. Los datos originales se conservan hasta la exportación.

## Estructura del repositorio

```text
DataCleanr/
├── web/       # Versión web (React + TypeScript + Vite) — GitHub Pages
├── desktop/   # Versión escritorio (Python + PySide6 + Pandas)
└── docs/      # Documentación y notas de diseño
```

- [Versión web](web/README_es.md)
- [Versión escritorio](desktop/README_es.md)

## Estado

En desarrollo inicial. La primera versión se centra en la web: carga de CSV y transformaciones básicas de texto.

## Licencia

[MIT](LICENSE)
