from PyQt5.QtWidgets import QTextEdit

class AnimationPanel(QTextEdit):
    """Панель анимации (пока заглушка)"""
    def __init__(self):
        super().__init__()
        self.setPlainText("Шкала анимации / кадры")
        self.setMinimumHeight(150)