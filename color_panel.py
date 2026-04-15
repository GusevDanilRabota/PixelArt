# color_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from color_palette import PaletteWidget

class ColorPanel(QWidget):
    """Панель палитры."""
    def __init__(self, palette_model):
        super().__init__()
        layout = QVBoxLayout()
        self.palette_widget = PaletteWidget(palette_model)
        layout.addWidget(self.palette_widget)
        self.setLayout(layout)
        self.setMinimumSize(250, 300)