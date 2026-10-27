# DataCleanr · Escritorio

Versión de escritorio de DataCleanr: Python + PySide6 + OpenPyXL + RapidFuzz.

Hace lo mismo que la versión web, sin límites de tamaño del navegador: pasa los mismos casos de prueba de [`shared/test-cases/`](../shared/README.md) y lee los mismos perfiles de limpieza.

Qué hace la herramienta y su filosofía están en el [README principal](../README_es.md).

## Descargar

| Sistema | Archivo |
|---|---|
| macOS (Apple Silicon) | [DataCleanr-macOS.dmg](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-macOS.dmg) |
| Windows (x64) | [DataCleanr-Windows.zip](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-Windows.zip) |
| Windows (ARM64) | [DataCleanr-Windows-ARM64.zip](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-Windows-ARM64.zip) |
| Linux (x64) | [DataCleanr-Linux.tar.gz](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-Linux.tar.gz) |
| Linux (ARM64, Ubuntu 24.04 o más nueva) | [DataCleanr-Linux-ARM64.tar.gz](https://github.com/RaulEstevezA/DataCleanr/releases/latest/download/DataCleanr-Linux-ARM64.tar.gz) |

Todas las versiones están en [Releases](https://github.com/RaulEstevezA/DataCleanr/releases).

> [!NOTE]
> Probada en **macOS** y **Windows x64**, donde funciona perfectamente. Las versiones de Windows ARM64 y Linux se compilan y pasan los tests y una prueba de arranque automática, pero nadie las ha usado todavía en un equipo real. Si encuentras algún problema, escríbeme a [contact.raulesteveza@gmail.com](mailto:contact.raulesteveza@gmail.com).

- **macOS:** abre el `.dmg` y arrastra DataCleanr a Aplicaciones.
- **Windows:** descomprime el `.zip` y ejecuta `DataCleanr.exe` dentro de la carpeta `DataCleanr`.
- **Linux:** descomprime con `tar -xzf DataCleanr-Linux.tar.gz` (o `DataCleanr-Linux-ARM64.tar.gz`) y ejecuta `DataCleanr/DataCleanr`. En algunas distribuciones hace falta instalar `libxcb-cursor0`. La versión ARM64 necesita una distribución de 2024 o más nueva (glibc 2.39, como Ubuntu 24.04).

### Abrirla la primera vez

La aplicación no está firmada (firmarla requiere cuentas de pago de Apple y Microsoft), así que el sistema avisa la primera vez que se abre:

- **macOS** dice que no ha podido verificar que la app esté libre de software malicioso. Pulsa **Hecho**, ve a **Ajustes del Sistema → Privacidad y seguridad**, baja hasta **Seguridad** y pulsa **Abrir igualmente**. Solo hay que hacerlo una vez.
- **Windows** muestra "Windows protegió su PC". Pulsa **Más información** y después **Ejecutar de todas formas**.

El código es el de este repositorio y los archivos los compila GitHub Actions ([workflow](../.github/workflows/release-desktop.yml)).

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

## Crear el ejecutable

```bash
pip install -e ".[build]"
pyinstaller packaging/datacleanr.spec
```

El resultado queda en `dist/`: `DataCleanr.app` en macOS y una carpeta `DataCleanr` con el ejecutable en Windows y Linux. PyInstaller no compila para otros sistemas: cada uno se crea en su propio sistema operativo.

## Estructura

```
datacleanr/
  core/          Lógica sin interfaz: cada módulo equivale a uno de web/src/core/
  io/            Lectura y escritura de CSV, Excel, JSON y XML
  ui/            Interfaz con PySide6
packaging/       Configuración de PyInstaller e iconos de la aplicación
tests/           Tests con pytest, leyendo los casos de shared/test-cases/
pyproject.toml   Dependencias y configuración
```

[Volver al README principal](../README_es.md)
