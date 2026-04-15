# drawing_panel.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush

class DrawingPanel(QWidget):
    def __init__(self, palette_model, grid_width=32, grid_height=32, pixel_size=20):
        super().__init__()
        self.palette_model = palette_model
        self.pixel_size = pixel_size
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.pixels = {}  # {(x, y): index}
        self._update_minimum_size()

    def _update_minimum_size(self):
        self.setMinimumSize(
            self.grid_width * self.pixel_size,
            self.grid_height * self.pixel_size
        )

    def set_grid_size(self, width, height):
        self.grid_width = max(1, width)
        self.grid_height = max(1, height)
        self.pixels.clear()
        self._update_minimum_size()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Размеры холста в пикселях
        canvas_width = self.grid_width * self.pixel_size
        canvas_height = self.grid_height * self.pixel_size
        canvas_rect = QRect(0, 0, canvas_width, canvas_height)

        # Фон вокруг холста
        painter.fillRect(self.rect(), QBrush(Qt.lightGray))

        # Шахматный фон внутри холста
        self._draw_transparency_background(painter, canvas_rect)

        # Рисуем пиксели
        for (x, y), index in self.pixels.items():
            color = self.palette_model.get_color(index)
            if color.alpha() > 0:
                painter.fillRect(
                    x * self.pixel_size, y * self.pixel_size,
                    self.pixel_size, self.pixel_size, color
                )

        # Сетка
        pen = QPen(QColor(200, 200, 200))
        pen.setWidth(1)
        painter.setPen(pen)

        for x in range(0, canvas_width + 1, self.pixel_size):
            painter.drawLine(x, 0, x, canvas_height)
        for y in range(0, canvas_height + 1, self.pixel_size):
            painter.drawLine(0, y, canvas_width, y)

    def _draw_transparency_background(self, painter, rect):
        cell_size = 10
        light_color = QColor(255, 255, 255)
        dark_color = QColor(200, 200, 200)

        for row in range(rect.top(), rect.bottom(), cell_size):
            for col in range(rect.left(), rect.right(), cell_size):
                if ((row // cell_size) + (col // cell_size)) % 2 == 0:
                    color = light_color
                else:
                    color = dark_color
                w = min(cell_size, rect.right() - col)
                h = min(cell_size, rect.bottom() - row)
                painter.fillRect(col, row, w, h, color)

    def set_pixel(self, x, y, color_index):
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            self.pixels[(x, y)] = color_index
            self.update()

    def clear(self):
        self.pixels.clear()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._draw_at_mouse(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self._draw_at_mouse(event)

    def _draw_at_mouse(self, event):
        x = event.x() // self.pixel_size
        y = event.y() // self.pixel_size
        self.set_pixel(x, y, self.palette_model.active_color_index)