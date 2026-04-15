from PyQt5.QtWidgets import QTabWidget, QTextEdit
from tools_panel import ToolsPanel

class LeftPanel(QTabWidget):
    """Левая панель с вкладками Файлы / Инструменты"""
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(200)

        file_tree = QTextEdit()
        file_tree.setPlainText("Файловое дерево")
        self.addTab(file_tree, "Файлы")

        self.tools_panel = ToolsPanel()
        self.addTab(self.tools_panel, "Инструменты")