from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush

class DrawingPanel(QWidget):
    def __init__(self, grid_width=32, grid_height=32, pixel_size=20):
        """
        :param grid_width: количество пикселей по горизонтали
        :param grid_height: количество пикселей по вертикали
        :param pixel_size: размер одного пикселя в экранных точках
        """
        super().__init__()
        self.pixel_size = pixel_size
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.pixels = {}  # {(x, y): QColor}
        self._update_minimum_size()

    def _update_minimum_size(self):
        """Обновляет минимальный размер виджета в соответствии с размером сетки."""
        self.setMinimumSize(
            self.grid_width * self.pixel_size,
            self.grid_height * self.pixel_size
        )

    def set_grid_size(self, width, height):
        """Устанавливает новый размер холста в пикселях."""
        self.grid_width = max(1, width)
        self.grid_height = max(1, height)
        self.pixels.clear()
        self._update_minimum_size()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Фон (белый)
        painter.fillRect(self.rect(), QBrush(Qt.white))

        # Рисуем закрашенные пиксели
        for (x, y), color in self.pixels.items():
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                painter.fillRect(
                    x * self.pixel_size,
                    y * self.pixel_size,
                    self.pixel_size,
                    self.pixel_size,
                    color
                )

        # Рисуем сетку
        pen = QPen(QColor(200, 200, 200))
        pen.setWidth(1)
        painter.setPen(pen)

        width_px = self.grid_width * self.pixel_size
        height_px = self.grid_height * self.pixel_size

        # Вертикальные линии
        for x in range(0, width_px + 1, self.pixel_size):
            painter.drawLine(x, 0, x, height_px)
        # Горизонтальные линии
        for y in range(0, height_px + 1, self.pixel_size):
            painter.drawLine(0, y, width_px, y)

    def set_pixel(self, x, y, color):
        """Закрашивает пиксель по координатам сетки."""
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            self.pixels[(x, y)] = color
            self.update()

    def clear(self):
        """Очищает холст."""
        self.pixels.clear()
        self.update()

    # --- Рисование мышью ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._draw_at_mouse(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self._draw_at_mouse(event)

    def _draw_at_mouse(self, event):
        x = event.x() // self.pixel_size
        y = event.y() // self.pixel_size
        self.set_pixel(x, y, Qt.black)