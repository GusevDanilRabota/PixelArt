# color_palette.py
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel, QSpinBox,
    QScrollArea, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

class PaletteModel:
    """Модель данных палитры."""
    def __init__(self, bit_depth=8):
        self.bit_depth = bit_depth
        self.max_colors = 2 ** bit_depth
        self.colors = []
        self.active_color_index = 0
        self.generate_palette()

    def generate_palette(self):
        """Генерирует цвета палитры в зависимости от разрядности."""
        n = self.max_colors
        self.colors = []
        if n == 1:
            self.colors = [QColor(0, 0, 0)]
        elif n == 2:
            self.colors = [QColor(0, 0, 0), QColor(255, 255, 255)]
        else:
            for i in range(n):
                hue = int(360 * i / n) % 360
                color = QColor()
                color.setHsv(hue, 255, 255)
                self.colors.append(color)
        if self.active_color_index >= n:
            self.active_color_index = 0

    def set_bit_depth(self, bit_depth):
        """Изменяет разрядность и перегенерирует палитру."""
        self.bit_depth = bit_depth
        self.max_colors = 2 ** bit_depth
        self.generate_palette()

    def get_color(self, index):
        if 0 <= index < self.max_colors:
            return self.colors[index]
        return QColor(0, 0, 0, 0)

    def is_transparent(self, index):
        return False


class ColorSwatch(QPushButton):
    """Виджет для отображения одного цвета в палитре (только выбор)."""
    clicked_with_index = pyqtSignal(int)

    def __init__(self, index, color):
        super().__init__()
        self.index = index
        self.color = color
        self.setCheckable(True)
        self.clicked.connect(self.emit_index)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(30)
        self.update_style()

    def emit_index(self):
        self.clicked_with_index.emit(self.index)

    def update_style(self):
        style = f"background-color: {self.color.name()}; border: 1px solid #888;"
        self.setStyleSheet(style)


class PaletteWidget(QWidget):
    colorSelected = pyqtSignal(int)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.swatches = []
        self.max_rows_per_column = 10
        self.setup_ui()
        self.update_palette()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        control_layout = QVBoxLayout()
        control_layout.addWidget(QLabel("Разрядность:"))
        self.bit_depth_spin = QSpinBox()
        self.bit_depth_spin.setRange(1, 8)
        self.bit_depth_spin.setValue(self.model.bit_depth)
        self.bit_depth_spin.valueChanged.connect(self.on_bit_depth_changed)
        control_layout.addWidget(self.bit_depth_spin)
        main_layout.addLayout(control_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.grid_layout.setSpacing(2)

        self.scroll_area.setWidget(self.grid_widget)
        main_layout.addWidget(self.scroll_area)

    def update_palette(self):
        for swatch in self.swatches:
            swatch.deleteLater()
        self.swatches.clear()

        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        for i, color in enumerate(self.model.colors):
            swatch = ColorSwatch(i, color)
            swatch.clicked_with_index.connect(self.select_color)
            self.swatches.append(swatch)

        self.relayout_swatches()

        if self.model.active_color_index < len(self.swatches):
            self.swatches[self.model.active_color_index].setChecked(True)

    def relayout_swatches(self):
        """Размещает образцы в один столбец, каждый растянут по ширине."""
        # Удаляем старую сетку
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        # Добавляем образцы в одну колонку
        for idx, swatch in enumerate(self.swatches):
            self.grid_layout.addWidget(swatch, idx, 0)

        # Единственная колонка растягивается на всю ширину
        self.grid_layout.setColumnStretch(0, 1)

    def select_color(self, index):
        if self.model.active_color_index < len(self.swatches):
            self.swatches[self.model.active_color_index].setChecked(False)
        self.model.active_color_index = index
        self.swatches[index].setChecked(True)
        self.colorSelected.emit(index)

    def on_bit_depth_changed(self, value):
        self.model.set_bit_depth(value)
        self.update_palette()

    def set_active_color(self, index):
        if 0 <= index < len(self.swatches):
            self.select_color(index)