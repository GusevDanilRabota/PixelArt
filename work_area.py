from PyQt5.QtWidgets import QSplitter
from PyQt5.QtCore import Qt
from drawing_panel import DrawingPanel
from color_panel import ColorPanel
from animation_panel import AnimationPanel

class WorkArea(QSplitter):
    """Рабочая область: верх (рисование+палитра) и низ (анимация)"""
    def __init__(self):
        super().__init__(Qt.Vertical)
        self.setMinimumWidth(500)

        # Верхняя часть
        top_splitter = QSplitter(Qt.Horizontal)
        self.drawing_panel = DrawingPanel()  # Используем новый класс с сеткой
        self.color_panel = ColorPanel()
        top_splitter.addWidget(self.drawing_panel)
        top_splitter.addWidget(self.color_panel)
        top_splitter.setSizes([600, 200])

        # Нижняя часть
        self.animation_panel = AnimationPanel()

        self.addWidget(top_splitter)
        self.addWidget(self.animation_panel)
        self.setSizes([600, 200])