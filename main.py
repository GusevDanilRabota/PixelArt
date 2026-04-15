import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QSplitter, QTextEdit,
    QVBoxLayout, QTabWidget
)
from PyQt5.QtCore import Qt

class LeftPanel(QTabWidget):
    """Левая панель с вкладками Файлы / Инструменты"""
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(200)

        # Вкладка "Файлы"
        self.file_tree = QTextEdit()
        self.file_tree.setPlainText("Файловое дерево")
        self.addTab(self.file_tree, "Файлы")

        # Вкладка "Инструменты"
        self.tools = QTextEdit()
        self.tools.setPlainText("Инструменты")
        self.addTab(self.tools, "Инструменты")

class DrawingPanel(QTextEdit):
    """Область рисования по пикселям"""
    def __init__(self):
        super().__init__()
        self.setPlainText("Область рисования (пиксельная сетка)")
        self.setMinimumSize(400, 300)

class ColorPanel(QTextEdit):
    """Панель выбора цвета / палитра"""
    def __init__(self):
        super().__init__()
        self.setPlainText("Палитра / выбор цвета")
        self.setMinimumSize(150, 300)

class TopArea(QSplitter):
    """Верхняя часть рабочей области: рисование + палитра"""
    def __init__(self):
        super().__init__(Qt.Horizontal)
        self.addWidget(DrawingPanel())
        self.addWidget(ColorPanel())
        self.setSizes([600, 200])

class AnimationPanel(QTextEdit):
    """Нижняя панель анимации"""
    def __init__(self):
        super().__init__()
        self.setPlainText("Шкала анимации / кадры")
        self.setMinimumHeight(150)

class WorkArea(QSplitter):
    """Рабочая область: верхняя часть + анимация"""
    def __init__(self):
        super().__init__(Qt.Vertical)
        self.setMinimumWidth(500)
        self.addWidget(TopArea())
        self.addWidget(AnimationPanel())
        self.setSizes([600, 200])

class MainWindow(QWidget):
    """Главное окно приложения"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelArt")
        self.resize(1920, 1080)

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(LeftPanel())
        main_splitter.addWidget(WorkArea())
        main_splitter.setSizes([250, 800])

        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())