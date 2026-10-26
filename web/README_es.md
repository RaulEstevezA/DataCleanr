# DataCleanr · Web

Versión web de DataCleanr. Todo el procesamiento ocurre en el navegador: los archivos no se suben a ningún servidor.

**Pruébala online:** [raulesteveza.github.io/tools/DataCleanr](https://raulesteveza.github.io/tools/DataCleanr/)

Qué hace la herramienta y su filosofía están en el [README principal](../README_es.md). Aquí se explica cómo está construida y cómo ejecutarla.

## Tecnologías

| | Para qué |
|---|---|
| [React 19](https://react.dev) + [TypeScript](https://www.typescriptlang.org) | Interfaz y lenguaje |
| [Vite](https://vite.dev) | Servidor de desarrollo y compilación |
| [Papa Parse](https://www.papaparse.com) | Leer y escribir CSV |
| [read-excel-file](https://www.npmjs.com/package/read-excel-file) / [write-excel-file](https://www.npmjs.com/package/write-excel-file) | Leer y escribir Excel (.xlsx) |
| [libphonenumber-js](https://www.npmjs.com/package/libphonenumber-js) | Validar y formatear teléfonos (versión JS de la librería de Google) |
| [Vitest](https://vitest.dev) + [jsdom](https://github.com/jsdom/jsdom) | Tests |
| [oxlint](https://oxc.rs) | Análisis estático |

JSON y XML se leen con las funciones del propio navegador, sin librerías.

Para Excel no se usa `xlsx` (SheetJS): la versión publicada en npm está anticuada y tiene vulnerabilidades conocidas.

## Ejecutar en local

Requisitos: Node.js 20.19+ o 22.12+.

```bash
cd web
npm install
npm run dev          # servidor de desarrollo en http://localhost:5173
npm test             # tests unitarios (Vitest)
npm run test:watch   # tests en modo observación
npm run lint         # análisis con oxlint
npm run build        # comprobación de tipos y compilación en dist/
npm run preview      # sirve la compilación en http://localhost:4173/tools/DataCleanr/
```

Para probar con datos sucios se puede crear una carpeta `local-data/` en cualquier parte del repositorio: está en el `.gitignore`, así que su contenido no se sube nunca.

## Estructura

```
src/
  core/          Lógica sin interfaz ni React (cada módulo con su test)
    csv.ts, xlsx.ts, json.ts, xml.ts, encoding.ts    Importar
    export.ts, xlsxSheet.ts                          Exportar
    transforms.ts, replace.ts                        Transformaciones de texto
    phone.ts, date.ts, amount.ts                     Normalización
    similar.ts                                       Valores parecidos (fuzzy matching)
    duplicates.ts                                    Duplicados exactos y posibles, combinar filas
    changes.ts, dataset.ts                           Vista previa y aplicación de cambios
    history.ts, operation.ts                         Deshacer / rehacer
    profile.ts                                       Perfiles de limpieza
  components/    Interfaz React (un componente por panel, con su CSS)
  i18n/          Textos en inglés y castellano
  hooks/         useStoredState: recuerda opciones en el navegador
  utils/         Descargas y carga diferida de las librerías de Excel
```

`core/` no depende de React: es la parte que se prueba con los casos compartidos y la que tiene su equivalente en `desktop/datacleanr/core/`.

## Tests

```bash
npm test
```

Cerca de 300 tests. La mayoría leen sus casos de [`shared/test-cases/`](../shared/README.md), los mismos que usará la versión de escritorio. Incluyen archivos de ejemplo reales (un `.xlsx` generado con OpenPyXL) y una prueba de ida y vuelta que escribe un Excel y lo vuelve a leer.

Las similitudes del fuzzy matching se calculan igual que `fuzz.ratio` de RapidFuzz, y los valores esperados de los casos se han obtenido con la propia librería.

## Privacidad

- No hay servidor ni llamadas a APIs: los archivos se leen con las funciones del navegador y los resultados se descargan desde memoria.
- No hay analítica ni cookies. Lo único que se guarda, en el `localStorage` del navegador, son preferencias: idioma, formato de teléfonos, fechas, etc.
- Las librerías grandes (reglas de teléfonos y Excel) se cargan solo cuando se usan, desde la misma web.

## Límites actuales

| | Límite | Motivo |
|---|---|---|
| Vista previa de cambios | 200 filas visibles (el resto se aplica igual) | No bloquear el navegador |
| Unificar valores parecidos | 3.000 valores distintos por columna | La comparación crece con el cuadrado de los valores |
| Posibles duplicados | 5.000 filas | Comparación entre filas |
| Excel | Solo `.xlsx` (no el antiguo `.xls`) | Igual que OpenPyXL en la versión de escritorio |

Los archivos más grandes son el caso de uso de la versión de escritorio.

[Volver al README principal](../README_es.md)
