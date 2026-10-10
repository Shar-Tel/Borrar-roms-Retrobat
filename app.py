import shutil
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPixmap
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
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)


@dataclass
class GameEntry:
    name: str
    description: str
    language: str
    region: str
    image_path: Path | None
    rom_path: Path | None


def read_field(game: ET.Element, tag: str) -> str:
    element = game.find(tag)
    return element.text.strip() if element is not None and element.text else ""


def load_games(xml_path: Path) -> list[GameEntry]:
    root = ET.parse(xml_path).getroot()
    games = []

    for game in root.findall("game"):
        raw_image = read_field(game, "image")
        raw_rom = read_field(game, "path")
        games.append(
            GameEntry(
                name=read_field(game, "name") or Path(raw_rom).stem or "Sin nombre",
                description=read_field(game, "desc"),
                language=read_field(game, "lang"),
                region=read_field(game, "region"),
                image_path=(xml_path.parent / raw_image).resolve() if raw_image else None,
                rom_path=(xml_path.parent / raw_rom).resolve() if raw_rom else None,
            )
        )

    return sorted(games, key=lambda game: game.name.casefold())


class GameListWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Gestor de juegos")
        self.resize(1100, 700)
        self.xml_path: Path | None = None
        self.games: list[GameEntry] = []
        self.current_image: Path | None = None

        open_action = QAction("Abrir XML...", self)
        open_action.triggered.connect(self.open_xml)
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu = self.menuBar().addMenu("Archivo")
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.game_list = QListWidget()
        self.game_list.currentRowChanged.connect(self.show_game)
        left_layout.addWidget(self.game_list)

        navigation = QHBoxLayout()
        self.previous_button = QPushButton("Anterior")
        self.previous_button.clicked.connect(lambda: self.select_game(-1))
        self.next_button = QPushButton("Siguiente")
        self.next_button.clicked.connect(lambda: self.select_game(1))
        navigation.addWidget(self.previous_button)
        navigation.addWidget(self.next_button)
        left_layout.addLayout(navigation)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.game_title = QLabel("Abre un archivo gamelist.xml")
        self.game_title.setStyleSheet("font-size: 20px; font-weight: 600;")
        right_layout.addWidget(self.game_title)

        metadata = QFormLayout()
        self.language_label = QLabel("—")
        self.region_label = QLabel("—")
        metadata.addRow("Idioma:", self.language_label)
        metadata.addRow("Región:", self.region_label)
        right_layout.addLayout(metadata)

        self.description = QPlainTextEdit()
        self.description.setReadOnly(True)
        self.description.setPlaceholderText("Sin descripción")
        right_layout.addWidget(self.description, 1)

        self.image_label = QLabel("Sin imagen")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumHeight(220)
        self.image_label.setStyleSheet("background: #20242a; color: #c6cbd2;")
        right_layout.addWidget(self.image_label, 1)

        actions = QHBoxLayout()
        self.confirm_checkbox = QCheckBox("Confirmar antes de borrar")
        self.confirm_checkbox.setChecked(True)
        self.delete_button = QPushButton("Borrar archivo")
        self.delete_button.clicked.connect(self.delete_game)
        actions.addWidget(self.confirm_checkbox)
        actions.addStretch()
        actions.addWidget(self.delete_button)
        right_layout.addLayout(actions)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        self.setCentralWidget(splitter)
        self.set_game_controls_enabled(False)

    def set_game_controls_enabled(self, enabled: bool) -> None:
        self.previous_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)

    def open_xml(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self, "Abrir lista de juegos", "", "Archivos XML (*.xml);;Todos los archivos (*)"
        )
        if not filename:
            return

        selected_path = Path(filename)
        try:
            games = load_games(selected_path)
        except (ET.ParseError, OSError) as error:
            QMessageBox.critical(self, "No se pudo abrir el XML", str(error))
            return

        self.xml_path = selected_path.resolve()
        self.games = games
        self.game_list.clear()
        self.game_list.addItems([game.name for game in games])
        self.set_game_controls_enabled(bool(games))
        self.setWindowTitle(f"Gestor de juegos - {selected_path.name}")
        if games:
            self.game_list.setCurrentRow(0)
        else:
            self.clear_game_details()
            self.game_title.setText("El XML no contiene juegos")

    def clear_game_details(self) -> None:
        self.current_image = None
        self.description.clear()
        self.language_label.setText("—")
        self.region_label.setText("—")
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("Sin imagen")

    def show_game(self, row: int) -> None:
        if row < 0 or row >= len(self.games):
            return

        game = self.games[row]
        self.game_title.setText(game.name)
        self.description.setPlainText(game.description)
        self.language_label.setText(game.language or "—")
        self.region_label.setText(game.region or "—")
        self.current_image = game.image_path
        self.update_image()

    def update_image(self) -> None:
        pixmap = QPixmap(str(self.current_image)) if self.current_image else QPixmap()
        if pixmap.isNull():
            self.image_label.setPixmap(QPixmap())
            self.image_label.setText("Imagen no disponible")
            return

        self.image_label.setText("")
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
        if 0 <= next_row < self.game_list.count():
            self.game_list.setCurrentRow(next_row)

    def delete_game(self) -> None:
        row = self.game_list.currentRow()
        if row < 0:
            return

        game = self.games[row]
        if game.rom_path is None:
            QMessageBox.warning(self, "Ruta no disponible", "Este juego no tiene un campo <path>.")
            return

        if not game.rom_path.is_file():
            QMessageBox.warning(
                self, "Archivo no encontrado", f"No se encontró el archivo:\n{game.rom_path}"
            )
            return

        if self.confirm_checkbox.isChecked():
            answer = QMessageBox.question(
                self,
                "Confirmar borrado",
                f"¿Borrar este archivo?\n{game.rom_path}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        try:
            backup_dir = Path.cwd() / "back"
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
            QMessageBox.critical(self, "No se pudo mover el archivo a back", str(error))
            return

        self.games.pop(row)
        self.game_list.takeItem(row)
        if self.games:
            self.game_list.setCurrentRow(min(row, len(self.games) - 1))
            self.show_game(self.game_list.currentRow())
            self.set_game_controls_enabled(True)
        else:
            self.clear_game_details()
            self.game_title.setText("No quedan juegos en la lista")
            self.set_game_controls_enabled(False)


def main() -> int:
    app = QApplication(sys.argv)
    window = GameListWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())