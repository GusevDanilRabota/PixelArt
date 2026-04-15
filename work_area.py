# work_area.py
from PyQt5.QtWidgets import QSplitter, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt
from drawing_panel import DrawingPanel
from color_panel import ColorPanel
from animation_panel import AnimationPanel, AnimationModel
from color_palette import PaletteModel

class WorkArea(QSplitter):
    def __init__(self):
        super().__init__(Qt.Vertical)
        self.setMinimumWidth(500)

        self.palette_model = PaletteModel(bit_depth=8)
        self.animation_model = AnimationModel()

        # --- Верхняя часть: холст (по центру) и палитра ---
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        # Контейнер для центрирования холста
        canvas_container = QWidget()
        canvas_layout = QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(0, 0, 0, 0)
        canvas_layout.setSpacing(0)

        self.drawing_panel = DrawingPanel(self.palette_model)

        # Добавляем растяжения со всех сторон, чтобы холст был по центру
        canvas_layout.addStretch(1)
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(self.drawing_panel)
        h_layout.addStretch(1)
        canvas_layout.addLayout(h_layout)
        canvas_layout.addStretch(1)

        self.color_panel = ColorPanel(self.palette_model)

        top_layout.addWidget(canvas_container, 1)  # холст занимает всё доступное пространство
        top_layout.addWidget(self.color_panel, 0)  # палитра фиксированной ширины

        self.addWidget(top_widget)

        # --- Нижняя часть: панель анимации с предпросмотром ---
        self.animation_panel = AnimationPanel(self.animation_model, self.palette_model)
        self.animation_panel.frameAdded.connect(self.on_add_frame)
        self.animation_panel.frameSelected.connect(self.on_frame_selected)
        self.animation_panel.frameDeleted.connect(self.on_frame_deleted)

        self.addWidget(self.animation_panel)
        self.setSizes([600, 250])

        self.color_panel.palette_widget.colorSelected.connect(self.on_color_selected)

    def on_color_selected(self, index):
        pass

    def on_add_frame(self):
        """Добавляет текущий холст как новый кадр."""
        pixels = self.drawing_panel.pixels
        w = self.drawing_panel.grid_width
        h = self.drawing_panel.grid_height
        new_index = self.animation_model.add_frame(pixels, w, h)

        pixmap = self.animation_panel.create_frame_thumbnail(new_index)
        self.animation_panel.add_frame_to_list(new_index, pixmap)

        # Устанавливаем onion skin - только что добавленный кадр (последний)
        last_frame = self.animation_model.get_frame(new_index)
        self.drawing_panel.set_onion_skin(last_frame)

    def on_frame_selected(self, index):
        frame = self.animation_model.get_frame(index)
        if frame:
            self.drawing_panel.load_frame(frame)
            # При выборе кадра показываем предыдущий кадр (если есть)
            if index > 0:
                prev_frame = self.animation_model.get_frame(index - 1)
                self.drawing_panel.set_onion_skin(prev_frame)
            else:
                self.drawing_panel.clear_onion_skin()
            self.animation_model.current_frame_index = index

    def on_frame_deleted(self, index):
        self.animation_model.delete_frame(index)
        if self.animation_model.frames:
            new_idx = min(index, len(self.animation_model.frames)-1)
            self.animation_panel.frame_list.setCurrentRow(new_idx)
            self.on_frame_selected(new_idx)
        else:
            self.drawing_panel.clear()
            self.drawing_panel.clear_onion_skin()