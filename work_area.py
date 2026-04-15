# work_area.py
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage, QColor
from drawing_panel import DrawingPanel
from color_panel import ColorPanel
from animation_panel import AnimationPanel, AnimationModel
from color_palette import PaletteModel

class WorkArea(QSplitter):
    def __init__(self):
        super().__init__(Qt.Vertical)
        self.setMinimumWidth(500)

        # Модели
        self.palette_model = PaletteModel(bit_depth=8)
        self.animation_model = AnimationModel()

        # Верхняя часть (рисование + палитра)
        top_splitter = QSplitter(Qt.Horizontal)
        self.drawing_panel = DrawingPanel(self.palette_model)
        self.color_panel = ColorPanel(self.palette_model)
        top_splitter.addWidget(self.drawing_panel)
        top_splitter.addWidget(self.color_panel)
        top_splitter.setSizes([600, 200])

        # Нижняя часть (анимация)
        self.animation_panel = AnimationPanel(self.animation_model)
        self.animation_panel.frameAdded.connect(self.on_add_frame)
        self.animation_panel.frameSelected.connect(self.on_frame_selected)
        self.animation_panel.frameDeleted.connect(self.on_frame_deleted)
        self.animation_panel.playStateChanged.connect(self.on_play_state_changed)

        self.addWidget(top_splitter)
        self.addWidget(self.animation_panel)
        self.setSizes([600, 200])

        self.color_panel.palette_widget.colorSelected.connect(self.on_color_selected)

    def on_color_selected(self, index):
        pass

    def on_add_frame(self):
        """Добавляет текущий холст как новый кадр."""
        # Сохраняем текущий кадр
        pixels = self.drawing_panel.pixels
        w = self.drawing_panel.grid_width
        h = self.drawing_panel.grid_height
        new_index = self.animation_model.add_frame(pixels, w, h)

        # Создаём миниатюру для списка
        pixmap = self.create_frame_thumbnail(new_index)
        self.animation_panel.add_frame_to_list(new_index, pixmap)

        # Устанавливаем onion skin предыдущего кадра (если есть)
        if new_index > 0:
            prev_frame = self.animation_model.get_frame(new_index - 1)
            self.drawing_panel.set_onion_skin(prev_frame)
        else:
            self.drawing_panel.clear_onion_skin()

        # Очищаем холст для рисования следующего кадра
        self.drawing_panel.clear()

    def create_frame_thumbnail(self, index):
        """Создаёт QPixmap миниатюру кадра для отображения в списке."""
        frame = self.animation_model.get_frame(index)
        if not frame:
            return QPixmap()
        w, h = frame['width'], frame['height']
        image = QImage(w, h, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        for (x, y), idx in frame['pixels'].items():
            color = self.palette_model.get_color(idx)
            image.setPixelColor(x, y, color)
        pixmap = QPixmap.fromImage(image).scaled(50, 50, Qt.KeepAspectRatio, Qt.FastTransformation)
        return pixmap

    def on_frame_selected(self, index):
        """Загружает выбранный кадр на холст."""
        frame = self.animation_model.get_frame(index)
        if frame:
            self.drawing_panel.load_frame(frame)
            # При выборе кадра отключаем onion skin или показываем предыдущий?
            if index > 0:
                prev_frame = self.animation_model.get_frame(index - 1)
                self.drawing_panel.set_onion_skin(prev_frame)
            else:
                self.drawing_panel.clear_onion_skin()
            self.animation_model.current_frame_index = index

    def on_frame_deleted(self, index):
        self.animation_model.delete_frame(index)
        # Если после удаления есть кадры, показываем последний или выбранный
        if self.animation_model.frames:
            new_idx = min(index, len(self.animation_model.frames)-1)
            self.animation_panel.frame_list.setCurrentRow(new_idx)
            self.on_frame_selected(new_idx)
        else:
            self.drawing_panel.clear()
            self.drawing_panel.clear_onion_skin()

    def on_play_state_changed(self, playing):
        """При воспроизведении временно отключаем редактирование."""
        self.drawing_panel.setEnabled(not playing)
        if playing:
            # Можно показывать первый кадр, если ничего не выбрано
            if self.animation_panel.frame_list.currentRow() < 0 and self.animation_model.frames:
                self.animation_panel.frame_list.setCurrentRow(0)
        else:
            # При остановке возвращаем текущий кадр
            pass