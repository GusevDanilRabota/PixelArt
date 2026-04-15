# work_area.py
from PyQt5.QtWidgets import QSplitter
from PyQt5.QtCore import Qt
from drawing_panel import DrawingPanel
from color_panel import ColorPanel
from animation_panel import AnimationPanel
from color_palette import PaletteModel

class WorkArea(QSplitter):
    def __init__(self):
        super().__init__(Qt.Vertical)
        self.setMinimumWidth(500)

        # Создаем модель палитры
        self.palette_model = PaletteModel(bit_depth=8)

        # Верхняя часть
        top_splitter = QSplitter(Qt.Horizontal)
        self.drawing_panel = DrawingPanel(self.palette_model)
        self.color_panel = ColorPanel(self.palette_model)
        top_splitter.addWidget(self.drawing_panel)
        top_splitter.addWidget(self.color_panel)
        top_splitter.setSizes([600, 200])

        # Нижняя часть
        self.animation_panel = AnimationPanel()

        self.addWidget(top_splitter)
        self.addWidget(self.animation_panel)
        self.setSizes([600, 200])

        # Связываем сигнал выбора цвета с обновлением курсора (опционально)
        self.color_panel.palette_widget.colorSelected.connect(self.on_color_selected)

    def on_color_selected(self, index):
        # Можно обновить статус бар или что-то еще
        pass