from PyQt5.QtWidgets import QTabWidget, QTextEdit

class LeftPanel(QTabWidget):
    """Левая панель с вкладками Файлы / Инструменты"""
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(200)

        file_tree = QTextEdit()
        file_tree.setPlainText("Файловое дерево")
        self.addTab(file_tree, "Файлы")

        tools = QTextEdit()
        tools.setPlainText("Инструменты")
        self.addTab(tools, "Инструменты")