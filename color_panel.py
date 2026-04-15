from PyQt5.QtWidgets import QTextEdit

class ColorPanel(QTextEdit):
    """Панель палитры (пока заглушка)"""
    def __init__(self):
        super().__init__()
        self.setPlainText("Палитра / выбор цвета")
        self.setMinimumSize(150, 300)