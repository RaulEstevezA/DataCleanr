# DataCleanr

Herramienta para limpiar, normalizar y deduplicar datos CSV, Excel, JSON y XML **sin enviar los archivos a ningún servidor**.

**Pruébala online:** [raulesteveza.github.io/tools/DataCleanr](https://raulesteveza.github.io/tools/DataCleanr/)

<p align="center">
  <a href="https://raulesteveza.github.io/tools/DataCleanr/">
    <img src="docs/images/web_app.png" alt="Versión web de DataCleanr unificando distintas formas de escribir un mismo nombre" width="720">
  </a>
</p>

## Para qué sirve

Los datos que llegan de hojas de cálculo, formularios o exportaciones de otros sistemas suelen venir sucios: espacios de más, mayúsculas mezcladas, teléfonos y fechas escritos de mil formas, filas repetidas y valores que significan lo mismo pero se escriben distinto:

```text
Raúl Estévez
RAUL ESTEVEZ
raul estévez
Estévez, Raúl
```

DataCleanr ayuda a detectar y corregir estos problemas antes de cargar los datos en una base de datos o en otro sistema.

## Filosofía

- **Nada cambia sin que el usuario lo vea.** Cada transformación muestra primero una vista previa `valor original → valor propuesto`, y cada cambio se puede aceptar o rechazar fila a fila.
- **Lo dudoso no se adivina.** Si un valor es ambiguo (`03/04/2024`, `1.234`) o no se puede convertir sin perder información (`007`, un teléfono con extensión), se deja tal cual y se avisa para revisarlo a mano.
- **El original se conserva** hasta la exportación, y todo se puede deshacer.
- **Los datos no salen del equipo.** No hay servidor: todo el procesamiento ocurre en local.

## Qué hace

### Importar

| Formato | Detalles |
|---|---|
| **CSV** | Detecta el separador (`,` `;` tabulador) y la codificación (UTF-8, UTF-16, Windows-1252 de Excel en español) |
| **Excel (.xlsx)** | Selector de hoja. Fechas, números y verdadero/falso se convierten a texto sin ambigüedad |
| **JSON** | Listas de objetos o de listas, objetos anidados (`contacto.email`). Los números se conservan exactos |
| **XML** | Detecta qué elemento es cada fila. Atributos como `@id`, elementos anidados como `direccion.ciudad` |

### Limpiar una columna

| Transformación | Ejemplo |
|---|---|
| Quitar espacios de los extremos | `"  Raúl Estévez "` → `"Raúl Estévez"` |
| Quitar espacios repetidos | `"laura   NAVARRO"` → `"laura NAVARRO"` |
| Minúsculas, MAYÚSCULAS, Primera En Mayúscula | `"jean-luc PÉREZ"` → `"Jean-Luc Pérez"` |
| Reemplazo personalizado | `"Estévez, Raúl"` → `"Raúl Estévez"`, con sugerencias de los valores de la columna |
| Normalizar teléfonos | `"600 123 456"` → `"+34600123456"` (E.164, internacional o nacional) |
| Normalizar fechas | `"13/07/2024"` → `"2024-07-13"`, eligiendo el orden de entrada y cómo leer los años de dos cifras |
| Normalizar importes | `"4.072,67"`, `"12063.99 €"` → `"4072.67"`, detectando solo los casos sin ambigüedad |
| Unificar valores parecidos | Agrupa `Raúl Estévez`, `RAUL ESTEVEZ`, `raul estévez`… y el usuario elige o escribe el valor final |

### Filas

- **Duplicados exactos**, comparando todas las columnas o solo las elegidas.
- **Posibles duplicados**: filas casi iguales (`Juan Pérez` / `juan perez` / `Juan Peres`), puntuadas por parecido. El usuario confirma cada grupo.
- **Combinar filas**: al eliminar duplicados, la fila conservada se completa con los datos que le faltaban de las eliminadas, sin sobrescribir nada.

### Historial y perfiles

- **Deshacer y rehacer** cualquier paso (también con `Ctrl/Cmd+Z`) y volver a cualquier punto del historial.
- **Perfiles de limpieza**: los pasos se guardan como un archivo JSON y se pueden aplicar a otro archivo, por ejemplo el del mes siguiente. Antes de aplicar se ve cuántos cambios hará cada paso.

### Exportar

- **CSV** en UTF-8, eligiendo el separador.
- **Excel (.xlsx)**, eligiendo para cada columna si se guarda como texto, número, fecha o verdadero/falso. Lo que no se puede convertir sin perder información (`007`, `1234,56`) se guarda como texto.

## Versiones

| | Web | Escritorio |
|---|---|---|
| Tecnología | React + TypeScript + Vite | Python + PySide6 + OpenPyXL + RapidFuzz |
| Dónde se ejecuta | En el navegador | Aplicación instalable (Windows, macOS, Linux) |
| Estado | Publicada: [raulesteveza.github.io/tools/DataCleanr](https://raulesteveza.github.io/tools/DataCleanr/) | [Descargar](./desktop/README_es.md#descargar) (probada en macOS) |
| Documentación | [web/README_es.md](./web/README_es.md) | [desktop/README_es.md](./desktop/README_es.md) |

## Comportamiento compartido

Las dos versiones se escriben por separado (TypeScript y Python), pero **se comportan igual**: la carpeta [`shared/`](./shared/README.md) contiene casos de prueba en JSON (y archivos de ejemplo) que definen qué debe hacer cada función. Los tests de la web y los del escritorio leen los mismos archivos, así que si una versión se comporta distinto, sus tests fallan.

El formato de los perfiles de limpieza también es común: un perfil guardado en la web se puede usar en el escritorio y al revés.

## Estructura del repositorio

```
web/                 Versión web (React + TypeScript + Vite)
  src/core/          Lógica sin interfaz: transformaciones, normalización, duplicados, perfiles...
  src/components/    Interfaz React
desktop/             Versión de escritorio (Python + PySide6)
shared/              Comportamiento común a ambas versiones
  test-cases/        Casos de prueba en JSON y archivos de ejemplo
docs/                Roadmap e imágenes
```

## Sugerencias

Ideas de mejora, errores o algún formato que te gustaría que DataCleanr admitiera: escríbeme a [contact.raulesteveza@gmail.com](mailto:contact.raulesteveza@gmail.com).

## Desarrollador

**Raul Estevez**

- [Web personal](https://raulesteveza.github.io/)
- [LinkedIn](https://www.linkedin.com/in/raulesteveza/)

## Licencia

[MIT](./LICENSE)

[Volver al README principal](./README.md)
