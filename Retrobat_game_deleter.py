#!/usr/bin/env python3
# Creado por: Ximo León
#Este programa es software libre; puedes redistribuirlo y/o modificarlo bajo los términos de la Licencia Pública General de GNU según se publica por la Free Software Foundation, ya sea la versión 3 de la Licencia, o (a tu elección) cualquier versión posterior.
#Este programa se distribuye con la esperanza de que sea útil, pero SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de COMERCIALIZACIÓN o IDONEIDAD PARA UN PROPÓSITO PARTICULAR. Consulta la Licencia Pública General de GNU para más detalles.
#Este programa sirve para borrar roms de una lista de juegos en formato gamelist.xml, moviéndolas a un subdirectorio "back" junto al XML. 
#Está pensado para ser usado en los directorios de Roms de Retrobat.
#Versión 1.0.0, 11-10-2026

import shutil
import sys
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import QLocale, QThread, Qt, Signal
from PySide6.QtGui import QAction, QActionGroup, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

# Traducciones de todos los textos de interfaz, indexadas por idioma y por clave.
TEXTS = {
    "es": {
        "window_title": "Gestor de juegos",
        "file_menu": "Archivo",
        "language_menu": "Idioma",
        "open_xml": "Abrir XML...",
        "exit": "Salir",
        "spanish": "Español",
        "english": "English",
        "previous": "Anterior",
        "next": "Siguiente",
        "loading_xml": "Cargando datos del XML...",
        "initial_prompt": "Abre un archivo gamelist.xml",
        "file_caption": "Archivo:",
        "developer_caption": "Desarrolladora:",
        "publisher_caption": "Distribuidora:",
        "language_caption": "Idioma:",
        "region_caption": "Región:",
        "description_placeholder": "Sin descripción",
        "no_image": "Sin imagen",
        "image_unavailable": "Imagen no disponible",
        "confirm_before_remove": "Confirmar antes de borrar",
        "remove_file": "Borrar",
        "open_dialog": "Abrir lista de juegos",
        "xml_filter": "Archivos XML (*.xml);;Todos los archivos (*)",
        "open_error": "No se pudo abrir el XML",
        "empty_xml": "El XML no contiene juegos",
        "missing_path_title": "Ruta no disponible",
        "missing_path": "Este juego no tiene un campo <path>.",
        "not_found_title": "Archivo no encontrado",
        "not_found": "No se encontró el archivo:\n{path}",
        "confirm_title": "Confirmar borrado",
        "confirm_remove": "¿Borrar este archivo?\n{path}",
        "move_error_title": "No se pudo borrar el archivo",
        "empty_list": "No quedan juegos en la lista",
    },
    "en": {
        "window_title": "Game Manager",
        "file_menu": "File",
        "language_menu": "Language",
        "open_xml": "Open XML...",
        "exit": "Exit",
        "spanish": "Español",
        "english": "English",
        "previous": "Previous",
        "next": "Next",
        "loading_xml": "Loading XML data...",
        "initial_prompt": "Open a gamelist.xml file",
        "file_caption": "File:",
        "developer_caption": "Developer:",
        "publisher_caption": "Publisher:",
        "language_caption": "Language:",
        "region_caption": "Region:",
        "description_placeholder": "No description",
        "no_image": "No image",
        "image_unavailable": "Image unavailable",
        "confirm_before_remove": "Confirm before deleting",
        "remove_file": "Delete",
        "open_dialog": "Open game list",
        "xml_filter": "XML files (*.xml);;All files (*)",
        "open_error": "Could not open XML",
        "empty_xml": "The XML contains no games",
        "missing_path_title": "Path unavailable",
        "missing_path": "This game has no <path> field.",
        "not_found_title": "File not found",
        "not_found": "File not found:\n{path}",
        "confirm_title": "Confirm delete",
        "confirm_remove": "Delete this file?\n{path}",
        "move_error_title": "Could not move file to back",
        "empty_list": "No games left in the list",
    },
}


@dataclass
class GameEntry:
    # Representa los datos visibles del juego y las rutas asociadas.
    name: str
    description: str
    language: str
    region: str
    image_path: Path | None
    rom_path: Path | None
    developer: str = ""
    publisher: str = ""


def read_field(game: ET.Element, tag: str) -> str:
    # Los campos opcionales ausentes o vacíos se normalizan como cadena vacía.
    element = game.find(tag)
    return element.text.strip() if element is not None and element.text else ""


def load_games(
    xml_path: Path,
    progress_callback: Callable[[int], None] | None = None,
) -> list[GameEntry]:
    # El XML es la base para resolver las rutas relativas de ROM e imagen.
    games = []
    total_bytes = xml_path.stat().st_size
    bytes_read = 0
    previous_progress = -1
    depth = 0
    parser = ET.XMLPullParser(events=("start", "end"))

    with xml_path.open("rb") as xml_file:
        while chunk := xml_file.read(64 * 1024):
            parser.feed(chunk)
            bytes_read += len(chunk)

            for event, element in parser.read_events():
                if event == "start":
                    depth += 1
                    continue

                if depth == 2 and element.tag == "game":
                    raw_image = read_field(element, "image")
                    raw_rom = read_field(element, "path")
                    games.append(
                        GameEntry(
                            name=read_field(element, "name")
                            or Path(raw_rom).stem
                            or "Sin nombre",
                            description=read_field(element, "desc"),
                            language=read_field(element, "lang"),
                            region=read_field(element, "region"),
                            image_path=(xml_path.parent / raw_image).resolve()
                            if raw_image
                            else None,
                            rom_path=(xml_path.parent / raw_rom).resolve()
                            if raw_rom
                            else None,
                            developer=read_field(element, "developer"),
                            publisher=read_field(element, "publisher"),
                        )
                    )
                    element.clear()

                depth -= 1

            if progress_callback is not None and total_bytes:
                progress = min(99, bytes_read * 100 // total_bytes)
                if progress != previous_progress:
                    progress_callback(progress)
                    previous_progress = progress

    parser.close()

    # Ordenar sin distinguir mayúsculas hace predecible la navegación.
    games = sorted(games, key=lambda game: game.name.casefold())
    if progress_callback is not None:
        progress_callback(100)
    return games


class GameLoadThread(QThread):
    loaded = Signal(object)
    failed = Signal(str)
    progress = Signal(int)

    def __init__(self, xml_path: Path) -> None:
        super().__init__()
        self.xml_path = xml_path

    def run(self) -> None:
        try:
            self.loaded.emit(load_games(self.xml_path, self.progress.emit))
        except (ET.ParseError, OSError) as error:
            self.failed.emit(str(error))


class GameListWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.language = (
            # Solo los sistemas en español arrancan en español; el resto usa inglés.
            "es" if QLocale.system().language() == QLocale.Language.Spanish else "en"
        )
        self.empty_state = "initial_prompt"
        self.setWindowTitle(self.t("window_title"))
        self.resize(1100, 700)
        self.xml_path: Path | None = None
        self.loading_xml_path: Path | None = None
        self.load_thread: GameLoadThread | None = None
        self.games: list[GameEntry] = []
        self.current_image: Path | None = None

        self.open_action = QAction(self.t("open_xml"), self)
        self.open_action.triggered.connect(self.open_xml)
        self.exit_action = QAction(self.t("exit"), self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu = self.menuBar().addMenu(self.t("file_menu"))
        self.file_menu.addAction(self.open_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.language_menu = self.menuBar().addMenu(self.t("language_menu"))
        self.language_actions: dict[str, QAction] = {}
        # El grupo mantiene una única opción marcada; selected conserva el idioma
        # correspondiente a cada acción cuando la señal se ejecuta más tarde.
        language_group = QActionGroup(self)
        language_group.setExclusive(True)
        for language, key in (("es", "spanish"), ("en", "english")):
            action = QAction(self.t(key), self)
            action.setCheckable(True)
            action.setChecked(language == self.language)
            action.triggered.connect(
                lambda checked=False, selected=language: self.set_language(selected)
                if checked
                else None
            )
            language_group.addAction(action)
            self.language_menu.addAction(action)
            self.language_actions[language] = action

        # La lista ocupa el panel izquierdo y los detalles del juego el derecho.
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.game_list = QListWidget()
        self.game_list.currentRowChanged.connect(self.show_game)
        left_layout.addWidget(self.game_list)
        self.loading_label = QLabel(self.t("loading_xml"))
        self.loading_label.hide()
        left_layout.addWidget(self.loading_label)
        self.loading_progress = QProgressBar()
        self.loading_progress.setRange(0, 100)
        self.loading_progress.setFormat("%p%")
        self.loading_progress.hide()
        left_layout.addWidget(self.loading_progress)

        navigation = QHBoxLayout()
        self.previous_button = QPushButton(self.t("previous"))
        self.previous_button.clicked.connect(lambda: self.select_game(-1))
        self.next_button = QPushButton(self.t("next"))
        self.next_button.clicked.connect(lambda: self.select_game(1))
        navigation.addWidget(self.previous_button)
        navigation.addWidget(self.next_button)
        left_layout.addLayout(navigation)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.game_title = QLabel(self.t("initial_prompt"))
        self.game_title.setStyleSheet("font-size: 20px; font-weight: 600;")
        right_layout.addWidget(self.game_title)

        metadata = QFormLayout()
        self.file_caption = QLabel(self.t("file_caption"))
        self.developer_caption = QLabel(self.t("developer_caption"))
        self.publisher_caption = QLabel(self.t("publisher_caption"))
        self.language_caption = QLabel(self.t("language_caption"))
        self.region_caption = QLabel(self.t("region_caption"))
        self.file_label = QLabel("—")
        self.file_label.setWordWrap(True)
        self.developer_label = QLabel("—")
        self.developer_label.setWordWrap(True)
        self.publisher_label = QLabel("—")
        self.publisher_label.setWordWrap(True)
        self.language_label = QLabel("—")
        self.region_label = QLabel("—")
        metadata.addRow(self.file_caption, self.file_label)
        metadata.addRow(self.developer_caption, self.developer_label)
        metadata.addRow(self.publisher_caption, self.publisher_label)
        metadata.addRow(self.language_caption, self.language_label)
        metadata.addRow(self.region_caption, self.region_label)
        right_layout.addLayout(metadata)

        self.description = QPlainTextEdit()
        self.description.setReadOnly(True)
        self.description.setPlaceholderText(self.t("description_placeholder"))
        right_layout.addWidget(self.description, 1)

        self.image_label = QLabel(self.t("no_image"))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(220)
        self.image_label.setStyleSheet("background: #20242a; color: #c6cbd2;")
        right_layout.addWidget(self.image_label, 1)

        actions = QHBoxLayout()
        self.confirm_checkbox = QCheckBox(self.t("confirm_before_remove"))
        self.confirm_checkbox.setChecked(True)
        self.delete_button = QPushButton(self.t("remove_file"))
        self.delete_button.clicked.connect(self.delete_game)
        actions.addWidget(self.confirm_checkbox)
        actions.addStretch()
        actions.addWidget(self.delete_button)
        right_layout.addLayout(actions)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([550, 550])
        self.setCentralWidget(splitter)
        self.set_game_controls_enabled(False)

    def t(self, key: str, **values: str) -> str:
        # Centraliza la búsqueda de traducciones y la interpolación de valores.
        return TEXTS[self.language][key].format(**values)

    def set_language(self, language: str) -> None:
        # Actualizar etiquetas no reconstruye la ventana ni pierde la selección.
        self.language = language
        self.language_actions[language].setChecked(True)
        self.file_menu.setTitle(self.t("file_menu"))
        self.language_menu.setTitle(self.t("language_menu"))
        self.open_action.setText(self.t("open_xml"))
        self.exit_action.setText(self.t("exit"))
        self.previous_button.setText(self.t("previous"))
        self.next_button.setText(self.t("next"))
        self.loading_label.setText(self.t("loading_xml"))
        self.file_caption.setText(self.t("file_caption"))
        self.developer_caption.setText(self.t("developer_caption"))
        self.publisher_caption.setText(self.t("publisher_caption"))
        self.language_caption.setText(self.t("language_caption"))
        self.region_caption.setText(self.t("region_caption"))
        self.description.setPlaceholderText(self.t("description_placeholder"))
        self.confirm_checkbox.setText(self.t("confirm_before_remove"))
        self.delete_button.setText(self.t("remove_file"))

        row = self.game_list.currentRow()
        if 0 <= row < len(self.games):
            self.show_game(row)
        else:
            self.clear_game_details()
            self.game_title.setText(self.t(self.empty_state))
        self.set_file_window_title()

    def set_file_window_title(self) -> None:
        # Añade el nombre del XML cuando ya se ha cargado una lista.
        if self.xml_path is None:
            self.setWindowTitle(self.t("window_title"))
        else:
            self.setWindowTitle(f"{self.t('window_title')} - {self.xml_path.name}")

    def set_game_controls_enabled(self, enabled: bool) -> None:
        self.previous_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def open_xml(self) -> None:
        if self.load_thread is not None:
            return

        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.t("open_dialog"),
            "",
            self.t("xml_filter"),
        )
        if not filename:
            return

        selected_path = Path(filename).resolve()
        self.loading_xml_path = selected_path
        self.loading_progress.setValue(0)
        self.loading_label.show()
        self.loading_progress.show()
        self.open_action.setEnabled(False)

        self.load_thread = GameLoadThread(selected_path)
        self.load_thread.loaded.connect(self.on_games_loaded)
        self.load_thread.failed.connect(self.on_load_failed)
        self.load_thread.progress.connect(self.loading_progress.setValue)
        self.load_thread.finished.connect(self.on_load_finished)
        self.load_thread.start()

    def on_games_loaded(self, games: list[GameEntry]) -> None:
        if self.loading_xml_path is None:
            return

        self.xml_path = self.loading_xml_path
        self.games = games
        self.empty_state = "empty_xml"
        self.game_list.clear()
        self.game_list.addItems([game.name for game in games])
        self.set_game_controls_enabled(bool(games))
        self.set_file_window_title()
        if games:
            self.empty_state = "initial_prompt"
            self.game_list.setCurrentRow(0)
        else:
            self.clear_game_details()
            self.game_title.setText(self.t("empty_xml"))

    def on_load_failed(self, message: str) -> None:
        QMessageBox.critical(self, self.t("open_error"), message)

    def on_load_finished(self) -> None:
        self.loading_label.hide()
        self.loading_progress.hide()
        self.open_action.setEnabled(True)
        self.loading_xml_path = None
        thread = self.load_thread
        self.load_thread = None
        if thread is not None:
            thread.deleteLater()

    def closeEvent(self, event) -> None:
        # Esperar al hilo evita destruir una ventana mientras la carga sigue activa.
        if self.load_thread is not None:
            self.load_thread.wait()
        super().closeEvent(event)

    def clear_game_details(self) -> None:
        self.current_image = None
        self.description.clear()
        self.file_label.setText("—")
        self.developer_label.setText("—")
        self.publisher_label.setText("—")
        self.language_label.setText("—")
        self.region_label.setText("—")
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText(self.t("no_image"))

    def show_game(self, row: int) -> None:
        # Ignorar índices inválidos, por ejemplo cuando la lista queda vacía.
        if row < 0 or row >= len(self.games):
            return

        game = self.games[row]
        self.game_title.setText(game.name)
        self.description.setPlainText(game.description)
        self.file_label.setText(game.rom_path.name if game.rom_path else "—")
        self.developer_label.setText(game.developer or "—")
        self.publisher_label.setText(game.publisher or "—")
        self.language_label.setText(game.language or "—")
        self.region_label.setText(game.region or "—")
        self.current_image = game.image_path
        self.update_image()

    def update_image(self) -> None:
        # Si no hay una imagen legible, mostrar el texto de estado correspondiente.
        pixmap = QPixmap(str(self.current_image)) if self.current_image else QPixmap()
        if pixmap.isNull():
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText(self.t("image_unavailable"))
            return

        self.image_label.setText("")
        # Mantener la proporción original evita deformar las carátulas.
        self.image_label.setPixmap(
            pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_image()

    def select_game(self, offset: int) -> None:
        row = self.game_list.currentRow()
        next_row = row + offset
        # La navegación se limita a las filas existentes.
        if 0 <= next_row < self.game_list.count():
            self.game_list.setCurrentRow(next_row)

    def delete_game(self) -> None:
        row = self.game_list.currentRow()
        if row < 0:
            return

        game = self.games[row]
        # Comprobar la ruta antes de abrir diálogos o intentar mover el archivo.
        if game.rom_path is None:
            QMessageBox.warning(
                self, self.t("missing_path_title"), self.t("missing_path")
            )
            return

        if not game.rom_path.is_file():
            QMessageBox.warning(
                self,
                self.t("not_found_title"),
                self.t("not_found", path=str(game.rom_path)),
            )
            return

        if self.confirm_checkbox.isChecked():
            answer = QMessageBox.question(
                self,
                self.t("confirm_title"),
                self.t("confirm_remove", path=str(game.rom_path)),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        try:
            # El respaldo queda junto al XML, aunque el programa se ejecute desde
            # otro directorio; los sufijos evitan reemplazar archivos existentes.
            backup_dir = self.xml_path.parent / "back"
            backup_dir.mkdir(exist_ok=True)
            destination = backup_dir / game.rom_path.name
            suffix = 1
            while destination.exists():
                destination = backup_dir / (
                    f"{game.rom_path.stem}_{suffix}{game.rom_path.suffix}"
                )
                suffix += 1
            shutil.move(str(game.rom_path), str(destination))
        except OSError as error:
            QMessageBox.critical(self, self.t("move_error_title"), str(error))
            return

        # Actualizar el modelo y la lista solo después de mover la ROM correctamente.
        self.games.pop(row)
        self.game_list.takeItem(row)
        if self.games:
            self.game_list.setCurrentRow(min(row, len(self.games) - 1))
            self.show_game(self.game_list.currentRow())
            self.set_game_controls_enabled(True)
        else:
            self.clear_game_details()
            self.empty_state = "empty_list"
            self.game_title.setText(self.t("empty_list"))
            self.set_game_controls_enabled(False)


def main() -> int:
    app = QApplication(sys.argv)
    window = GameListWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())