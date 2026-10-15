# Gestor de juegos para RetroBat

Aplicación de escritorio para abrir un `gamelist.xml`, consultar los datos de sus juegos y mover archivos ROM a una carpeta de respaldo llamada `back`. Permite borrar juegos más rápido que desde el interfaz de Retrobat, muy útil para hacer limpieza de romsets con múltiples versiones de juegos o juegos no deseados. 
Es posible que funcione también con otros entornos de emulación que usen el mismo esquema de xml. Probado también con Knulli.  
Creado con la asistencia de GitHub Copilot.
## Funciones

- Muestra el nombre, la descripción, el idioma, la región y la imagen asociada al juego seleccionado. Para la mayor parte de la información hace falta haber escrapeado primero los juegos.
- Permite recorrer la lista con los botones **Anterior** y **Siguiente**.
- Ofrece interfaz en español e inglés. El idioma inicial se elige según el idioma del sistema.
- Si se mira el directorio fbneo, intenta sacar información extra de arcade.xml. Si no existe, se lo puede bajar automáticamente de https://data.spludlow.co.uk/fbneo/arcade.xml. Con esta información extra muestra si un juego es clon de otro y lo marca en rojo en la lista.
- Antes de mover una ROM, comprueba que la ruta esté indicada y que el archivo exista. La confirmación se puede desactivar desde la casilla correspondiente.
- Crea `back` junto al `gamelist.xml` abierto, independientemente del directorio desde el que se inicie la aplicación.
- Si en `back` ya existe un archivo con el mismo nombre, añade un sufijo numérico para evitar sobrescribirlo.
-¡Haz backup de tu directorio de ROMs antes de usar este software!
- Se recomienda tras acabar de borrar los juegos deseados ir a las opciones de desarrollador de Retrobat y elegir "Limpiar listas de juegos y borrar medios no utilizados" para que elimine los juegos del gamelist.xml y también las imágenes, manuales o videos de juegos borrados.


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
- `<developer>`: desarrolladora del juego.
- `<publisher>`: distribuidora del juego.
- `<image>`: ruta de la imagen, opcional.
- `<desc>`: descripción.
- `<lang>`: idioma.
- `<region>`: región.

Las rutas relativas de `<path>` e `<image>` se resuelven desde la carpeta donde está el XML. Por ejemplo:

Solo aparecen en la lista los juegos cuyo `<path>` apunta a un archivo existente.

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

El botón **Borrar archivo** no elimina la ROM: la mueve a `back`. El programa no modifica ni elimina la entrada correspondiente del XML, eso lo hará Retrobat.

---

# RetroBat Game Manager

A desktop application for opening a `gamelist.xml`, checking the data of its games, and moving ROM files to a backup folder named `back`. It allows you to remove games faster than from the RetroBat interface, which is especially useful for cleaning ROM sets with multiple versions of the same game or unwanted titles.
It may also work with other emulation systems that use the same XML schema. It has also been tested with Knulli.
Created with GitHub Copilot.

## Features

- Shows the selected game's name, description, language, region, and associated image. Most of this information requires scraping the games first.
- Lets you browse the list using the **Previous** and **Next** buttons.
- Offers a Spanish and English interface. The initial language is chosen based on the system language.
- Includes a language switch in the top menu.
- When opening a `gamelist.xml` from the `fbneo` directory, the app looks for `arcade.xml`. If it is missing, the app asks whether to download it from https://data.spludlow.co.uk/fbneo/arcade.xml. When available, this extra information is used to identify clone games and mark them in red in the list.
- Before moving a ROM, it checks that the path is set and that the file exists. The confirmation step can be disabled from the corresponding checkbox.
- Creates `back` next to the opened `gamelist.xml`, regardless of the directory from which the application is launched.
- If `back` already contains a file with the same name, it adds a numeric suffix to avoid overwriting it.
-Please backup your ROM directory before using this software!
- After finishing deleting the games you want, it is recommended to go to RetroBat's developer options and choose **Clean game lists and delete unused media** so it removes the games from `gamelist.xml` and also the images, manuals, or videos of deleted games.

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

- `<name>`: displayed name. If missing, it tries to get it from the file name indicated by `<path>`.
- `<path>`: path to the ROM file.
- `<developer>`: game developer.
- `<publisher>`: game publisher.
- `<image>`: path to the image (optional).
- `<desc>`: description.
- `<lang>`: language.
- `<region>`: region.

Relative `<path>` and `<image>` paths are resolved from the folder where the XML is located. For example:

Only games whose `<path>` points to an existing file are shown in the list.

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

## What the delete button does

The **Delete file** button does not delete the ROM: it moves it to `back`. The program does not modify or remove the corresponding entry in the XML; RetroBat will do that.
