from PyQt5.QtWidgets import QTextEdit

class DrawingPanel(QTextEdit):
    """Панель рисования (пока заглушка)"""
    def __init__(self):
        super().__init__()
        self.setPlainText("Область рисования (пиксельная сетка)")
        self.setMinimumSize(400, 300)