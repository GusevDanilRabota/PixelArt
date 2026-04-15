# color_palette.py
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QLabel, QSpinBox, QScrollArea
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
            # Для n >= 3 генерируем цвета равномерно по HSV
            for i in range(n):
                hue = int(360 * i / n) % 360
                color = QColor()
                color.setHsv(hue, 255, 255)
                self.colors.append(color)
        # Сбрасываем активный индекс, если он выходит за границы
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
        # Для простоты прозрачных цветов пока нет, но можно расширить
        return False


class ColorSwatch(QPushButton):
    """Виджет для отображения одного цвета в палитре (только выбор)."""
    clicked_with_index = pyqtSignal(int)

    def __init__(self, index, color):
        super().__init__()
        self.index = index
        self.color = color
        self.setFixedSize(30, 30)
        self.setCheckable(True)
        self.clicked.connect(self.emit_index)
        self.update_style()

    def emit_index(self):
        self.clicked_with_index.emit(self.index)

    def update_style(self):
        style = f"background-color: {self.color.name()}; border: 1px solid #888;"
        self.setStyleSheet(style)


class PaletteWidget(QWidget):
    colorSelected = pyqtSignal(int)  # сигнал: индекс выбранного цвета

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.swatches = []
        self.setup_ui()
        self.update_palette()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Элемент управления разрядностью
        control_layout = QVBoxLayout()
        control_layout.addWidget(QLabel("Разрядность:"))
        self.bit_depth_spin = QSpinBox()
        self.bit_depth_spin.setRange(1, 8)
        self.bit_depth_spin.setValue(self.model.bit_depth)
        self.bit_depth_spin.valueChanged.connect(self.on_bit_depth_changed)
        control_layout.addWidget(self.bit_depth_spin)
        layout.addLayout(control_layout)

        # Область с прокруткой для вертикального списка цветов
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

    def update_palette(self):
        # Удаляем старые образцы
        for swatch in self.swatches:
            swatch.deleteLater()
        self.swatches.clear()

        # Создаём новые образцы и добавляем в вертикальный layout
        for i, color in enumerate(self.model.colors):
            swatch = ColorSwatch(i, color)
            swatch.clicked_with_index.connect(self.select_color)
            self.swatches.append(swatch)
            self.scroll_layout.addWidget(swatch)

        # Выделяем активный цвет
        if self.model.active_color_index < len(self.swatches):
            self.swatches[self.model.active_color_index].setChecked(True)

    def select_color(self, index):
        # Снимаем выделение с предыдущего
        if self.model.active_color_index < len(self.swatches):
            self.swatches[self.model.active_color_index].setChecked(False)
        self.model.active_color_index = index
        self.swatches[index].setChecked(True)
        self.colorSelected.emit(index)

    def on_bit_depth_changed(self, value):
        self.model.set_bit_depth(value)
        self.update_palette()