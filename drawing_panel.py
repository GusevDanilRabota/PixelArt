# drawing_panel.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush

class DrawingPanel(QWidget):
    colorPicked = pyqtSignal(int)  # новый сигнал

    def __init__(self, palette_model, grid_width=32, grid_height=32, pixel_size=20):
        super().__init__()
        self.palette_model = palette_model
        self.pixel_size = pixel_size
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.pixels = {}
        self.onion_skin_frame = None
        self.onion_skin_alpha = 100

        # Новые атрибуты
        self.current_tool = 'pen'        # 'pen', 'eraser', 'eyedropper'
        self.zoom_level = pixel_size     # текущий размер пикселя

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

    def set_onion_skin(self, frame):
        """Устанавливает кадр для отображения полупрозрачным слоем."""
        self.onion_skin_frame = frame
        self.update()

    def clear_onion_skin(self):
        self.onion_skin_frame = None
        self.update()

    def load_frame(self, frame):
        """Загружает кадр в холст для редактирования."""
        self.pixels = {pos: idx for pos, idx in frame['pixels'].items()}
        # Размеры кадра могут отличаться от текущего холста? Пока считаем, что совпадают.
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        canvas_width = self.grid_width * self.pixel_size
        canvas_height = self.grid_height * self.pixel_size
        canvas_rect = QRect(0, 0, canvas_width, canvas_height)

        # Фон вокруг холста
        painter.fillRect(self.rect(), QBrush(Qt.lightGray))

        # Шахматный фон внутри холста
        self._draw_transparency_background(painter, canvas_rect)

        # Если есть onion skin, рисуем его полупрозрачным
        if self.onion_skin_frame:
            self._draw_onion_skin(painter)

        # Рисуем пиксели текущего холста
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

    def _draw_onion_skin(self, painter):
        """Рисует предыдущий кадр с заданной прозрачностью."""
        frame = self.onion_skin_frame
        if not frame:
            return
        # Проверяем совместимость размеров (должны совпадать)
        for (x, y), index in frame['pixels'].items():
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                color = self.palette_model.get_color(index)
                if color.alpha() > 0:
                    # Создаём полупрозрачный цвет
                    onion_color = QColor(color.red(), color.green(), color.blue(), self.onion_skin_alpha)
                    painter.fillRect(
                        x * self.pixel_size, y * self.pixel_size,
                        self.pixel_size, self.pixel_size, onion_color
                    )

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

    def set_tool(self, tool):
        """Установить текущий инструмент."""
        self.current_tool = tool

    def set_zoom(self, pixel_size):
        """Установить масштаб (размер пикселя в пикселях)."""
        self.pixel_size = pixel_size
        self._update_minimum_size()
        self.update()

    # Переопределяем обработчики мыши с учётом инструментов
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.current_tool == 'eyedropper':
                self._pick_color(event)
            else:
                self._draw_at_mouse(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if self.current_tool in ('pen', 'eraser'):
                self._draw_at_mouse(event)

    def _draw_at_mouse(self, event):
        x = event.x() // self.pixel_size
        y = event.y() // self.pixel_size
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            if self.current_tool == 'pen':
                color_index = self.palette_model.active_color_index
                self.pixels[(x, y)] = color_index
            elif self.current_tool == 'eraser':
                # Удаляем пиксель (ластик)
                if (x, y) in self.pixels:
                    del self.pixels[(x, y)]
            self.update()

    def _pick_color(self, event):
        """Пипетка: выбрать цвет из текущего пикселя."""
        x = event.x() // self.pixel_size
        y = event.y() // self.pixel_size
        if (x, y) in self.pixels:
            index = self.pixels[(x, y)]
            # Устанавливаем активный цвет в палитре
            self.palette_model.active_color_index = index
            # Оповещаем палитру об изменении выбора (нужен доступ к ColorPanel)
            # Это будет сделано через сигналы в WorkArea
            self.colorPicked.emit(index)
