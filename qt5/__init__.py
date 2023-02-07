import os
import pathlib
from typing import Optional

from PySide6 import QtWidgets
from PySide6.QtGui import QPainter, QColor, QPixmap

app = QtWidgets.QApplication([])


class CreativePainter:
    def __init__(self, width: int, height: int, bg_color: Optional[QColor] = None):
        self.painter = QPainter()
        self.image = QPixmap(width, height)
        self.width = width
        self.height = height
        self.bg_color = bg_color

        if self.bg_color is not None:
            self.image.fill(self.bg_color)

    def clear_image(self):
        self.image = QPixmap(self.width, self.height)

        if self.bg_color is not None:
            self.image.fill(self.bg_color)

    def __enter__(self):
        self.painter.begin(self.image)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.painter.end()

    def save_image(self, full_file_name: str, quality: int = 100, overwrite: bool = True):
        directory = os.path.dirname(full_file_name)
        if directory != '' and not directory.startswith('.') and not os.path.exists(directory):
            os.mkdir(directory)

        # Do not overwrite the image if it exists already
        if not overwrite and os.path.exists(full_file_name):
            raise Exception('File exists and overwrite is set to False!')

        file_extension = pathlib.Path(full_file_name).suffix[1:]

        return self.image.save(full_file_name, file_extension, quality)
