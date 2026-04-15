# drawing_panel.py
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QCursor, QImage

class DrawingPanel(QWidget):
    colorPicked = pyqtSignal(int)
    cursorMoved = pyqtSignal(int, int)
    colorChanged = pyqtSignal(QColor)

    MAX_UNDO = 50

    def __init__(self, palette_model, grid_width=32, grid_height=32, pixel_size=20):
        super().__init__()
        self.palette_model = palette_model
        self.pixel_size = pixel_size
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.pixels = {}
        self.onion_skin_frame = None
        self.onion_skin_alpha = 100
        self.current_tool = 'pen'
        
        # Панорамирование
        self.pan_offset_x = 0
        self.pan_offset_y = 0
        self.pan_active = False
        self.last_pan_pos = None
        self.space_pressed = False
        
        # Undo/Redo
        self.undo_stack = []
        self.redo_stack = []
        self._push_undo_state()
        
        self.setFocusPolicy(Qt.StrongFocus)
        self._update_minimum_size()

    def undo(self):
        if len(self.undo_stack) > 1:
            current = self.undo_stack.pop()
            self.redo_stack.append(current)
            prev = self.undo_stack[-1]
            self.pixels = {pos: idx for pos, idx in prev.items()}
            self.update()

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            self.pixels = {pos: idx for pos, idx in state.items()}
            self.update()

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
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._push_undo_state()
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

    def _push_undo_state(self):
        """Сохраняет текущее состояние пикселей в стек undo."""
        state = {pos: idx for pos, idx in self.pixels.items()}
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.MAX_UNDO:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def set_pixel(self, x, y, color_index):
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            old = self.pixels.get((x, y))
            if old != color_index:
                self._push_undo_state()
                self.pixels[(x, y)] = color_index
                self.update()

    def clear(self):
        self._push_undo_state()
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.space_pressed = True
            self.setCursor(Qt.OpenHandCursor)
            event.accept()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.space_pressed = False
            self.setCursor(Qt.ArrowCursor)
            self.pan_active = False
            event.accept()

    # Переопределяем обработчики мыши с учётом инструментов
    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton or (self.space_pressed and event.button() == Qt.LeftButton):
            self.pan_active = True
            self.last_pan_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.LeftButton:
            if self.current_tool == 'eyedropper':
                self._pick_color(event)
            else:
                self._draw_at_mouse(event)

    def mouseMoveEvent(self, event):
        # Отправляем координаты для статус-бара
        x = (event.x() - self.pan_offset_x) // self.pixel_size
        y = (event.y() - self.pan_offset_y) // self.pixel_size
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            self.cursorMoved.emit(x, y)
        else:
            self.cursorMoved.emit(-1, -1)

        if self.pan_active:
            delta = event.pos() - self.last_pan_pos
            self.pan_offset_x += delta.x()
            self.pan_offset_y += delta.y()
            self.last_pan_pos = event.pos()
            self.update()
            event.accept()
        elif event.buttons() & Qt.LeftButton:
            if self.current_tool in ('pen', 'eraser'):
                self._draw_at_mouse(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton or (self.space_pressed and event.button() == Qt.LeftButton):
            self.pan_active = False
            self.setCursor(Qt.OpenHandCursor if self.space_pressed else Qt.ArrowCursor)
            event.accept()

    def _draw_at_mouse(self, event):
        x = (event.x() - self.pan_offset_x) // self.pixel_size
        y = (event.y() - self.pan_offset_y) // self.pixel_size
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            if self.current_tool == 'pen':
                color_index = self.palette_model.active_color_index
                if self.pixels.get((x, y)) != color_index:
                    self._push_undo_state()
                    self.pixels[(x, y)] = color_index
                    self.update()
            elif self.current_tool == 'eraser':
                if (x, y) in self.pixels:
                    self._push_undo_state()
                    del self.pixels[(x, y)]
                    self.update()

    def _pick_color(self, event):
        x = (event.x() - self.pan_offset_x) // self.pixel_size
        y = (event.y() - self.pan_offset_y) // self.pixel_size
        if (x, y) in self.pixels:
            index = self.pixels[(x, y)]
            self.palette_model.active_color_index = index
            self.colorPicked.emit(index)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Применяем смещение панорамирования
        painter.translate(self.pan_offset_x, self.pan_offset_y)

        canvas_width = self.grid_width * self.pixel_size
        canvas_height = self.grid_height * self.pixel_size
        canvas_rect = QRect(0, 0, canvas_width, canvas_height)

        # Фон вокруг холста
        painter.fillRect(self.rect(), QBrush(Qt.lightGray))

        # Шахматный фон внутри холста
        self._draw_transparency_background(painter, canvas_rect)

        if self.onion_skin_frame:
            self._draw_onion_skin(painter)

        for (x, y), index in self.pixels.items():
            color = self.palette_model.get_color(index)
            if color.alpha() > 0:
                painter.fillRect(
                    x * self.pixel_size, y * self.pixel_size,
                    self.pixel_size, self.pixel_size, color
                )

        pen = QPen(QColor(200, 200, 200))
        pen.setWidth(1)
        painter.setPen(pen)
        for x in range(0, canvas_width + 1, self.pixel_size):
            painter.drawLine(x, 0, x, canvas_height)
        for y in range(0, canvas_height + 1, self.pixel_size):
            painter.drawLine(0, y, canvas_width, y)

    def set_active_color(self, index):
        """Вызывается при смене активного цвета в палитре."""
        color = self.palette_model.get_color(index)
        self.colorChanged.emit(color)