# Gestor de juegos para RetroBat

Aplicación de escritorio para abrir un `gamelist.xml`, consultar los datos de sus juegos y mover archivos ROM a una carpeta de respaldo llamada `back`.

## Funciones

- Muestra el nombre, la descripción, el idioma, la región y la imagen asociada al juego seleccionado.
- Permite recorrer la lista con los botones **Anterior** y **Siguiente**.
- Ofrece interfaz en español e inglés. El idioma inicial se elige según el idioma del sistema.
- Antes de mover una ROM, comprueba que la ruta esté indicada y que el archivo exista. La confirmación se puede desactivar desde la casilla correspondiente.
- Crea `back` junto al `gamelist.xml` abierto, independientemente del directorio desde el que se inicie la aplicación.
- Si en `back` ya existe un archivo con el mismo nombre, añade un sufijo numérico para evitar sobrescribirlo.
- Tras borrar los juegos que quieras, recarga la lista de juegos en Retrobat para que actualice el gamelist.xml. Se recomienda al final ir a las opciones de desarrollador de Retrobat y elegir "Limpiar listas de jjuegos y borrar medios no utilizados" para que elimine imágenes, manuales o videos de juegos borrados.


## Requisitos

- Python 3.10 o posterior.
- PySide6, instalado mediante `requirements.txt`.

## Instalación y ejecución

En PowerShell, desde el directorio del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py app.py
```

Si no quieres crear un entorno virtual, instala las dependencias con `py -m pip install -r requirements.txt` y ejecuta `py app.py`.

Al iniciar, selecciona **Archivo > Abrir XML...** y elige el `gamelist.xml` que quieres consultar.

## Formato de la lista

El programa busca elementos `<game>` directamente dentro del elemento raíz del XML. Para cada juego, lee estos campos:

- `<name>`: nombre mostrado. Si falta, intenta obtenerlo del nombre del archivo indicado por `<path>`.
- `<path>`: ruta del archivo ROM.
- `<image>`: ruta de la imagen, opcional.
- `<desc>`: descripción.
- `<lang>`: idioma.
- `<region>`: región.

Las rutas relativas de `<path>` e `<image>` se resuelven desde la carpeta donde está el XML. Por ejemplo:

```xml
<gameList>
  <game>
    <name>Ejemplo</name>
    <path>./roms/ejemplo.zip</path>
    <image>./images/ejemplo.png</image>
    <desc>Descripción del juego</desc>
    <lang>es</lang>
    <region>EU</region>
  </game>
</gameList>
```

## Qué hace el botón de borrado

El botón **Borrar archivo** no elimina la ROM: la mueve a `back`. El programa no modifica ni elimina la entrada correspondiente del XML. Por eso, si vuelves a abrir la lista, el juego seguirá apareciendo, aunque su ROM ya no estará en la ruta original.

---

# RetroBat Game Manager

A desktop application for opening a `gamelist.xml`, viewing game information, and moving ROM files to a backup folder named `back`.

## Features

- Shows the selected game's name, description, language, region, and associated image.
- Lets you browse the list using the **Previous** and **Next** buttons.
- Provides a Spanish and English interface. The initial language is selected based on the system language: Spanish for Spanish-language Windows, English otherwise.
- Before moving a ROM, checks that its path is specified and that the file exists. You can disable the confirmation prompt using the checkbox.
- Creates `back` next to the opened `gamelist.xml`, regardless of the directory from which the application is launched.
- If `back` already contains a file with the same name, adds a numeric suffix to avoid overwriting it.
- After moving the games you want, reload the game list in RetroBat to update `gamelist.xml`. It is also recommended to open RetroBat's developer options and select **Clean game lists and delete unused media** to remove images, manuals, or videos for removed games.

## Requirements

- Python 3.10 or later.
- PySide6, installed through `requirements.txt`.

## Installation and running

In PowerShell, from the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py app.py
```

If you do not want to create a virtual environment, install the dependencies with `py -m pip install -r requirements.txt` and run `py app.py`.

When the application starts, select **File > Open XML...** and choose the `gamelist.xml` you want to view.

## List format

The program looks for `<game>` elements directly inside the XML root element. For each game, it reads these fields:

- `<name>`: displayed name. If missing, the program tries to use the file name from `<path>`.
- `<path>`: path to the ROM file.
- `<image>`: path to the image (optional).
- `<desc>`: description.
- `<lang>`: language.
- `<region>`: region.

Relative `<path>` and `<image>` paths are resolved from the directory containing the XML. For example:

```xml
<gameList>
  <game>
    <name>Example</name>
    <path>./roms/example.zip</path>
    <image>./images/example.png</image>
    <desc>Game description</desc>
    <lang>en</lang>
    <region>EU</region>
  </game>
</gameList>
```

## What the move button does

The **Move to back** button does not delete the ROM; it moves it to `back`. The program does not modify or remove the corresponding XML entry. Therefore, if you open the list again, the game will still appear even though its ROM is no longer at the original path.
