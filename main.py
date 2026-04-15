import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QSplitter, QTextEdit,
    QVBoxLayout, QTabWidget
)
from PyQt5.QtCore import Qt

class main_window_t(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelArt") # Заголовок окна
        self.resize(1920, 1080)         # Размер окна (ширина, высота)

        # Создаём сплиттер с горизонтальным разделением (лево-право)
        splitter = QSplitter(Qt.Horizontal)

        # --- Левая часть: вкладки ---
        tab_widget = QTabWidget()

        # Вкладка "Файловое дерево"
        file_tree_tab = QTextEdit()
        file_tree_tab.setPlainText("Здесь будет файловое дерево")
        tab_widget.addTab(file_tree_tab, "Файлы")

        # Вкладка "Инструменты"
        tools_tab = QTextEdit()
        tools_tab.setPlainText("Здесь будут инструменты")
        tab_widget.addTab(tools_tab, "Инструменты")

        # Можно добавить ещё вкладки при необходимости

        # --- Правая часть: рабочая область ---
        work_space_widget = QTextEdit()
        work_space_widget.setPlainText("Рабочая область")

        # Минимальные ширины
        tab_widget.setMinimumWidth(200)
        work_space_widget.setMinimumWidth(400)

        # Добавляем в сплиттер
        splitter.addWidget(tab_widget)
        splitter.addWidget(work_space_widget)

        # Начальные пропорции
        splitter.setSizes([300, 600])

        # Компоновка
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main_window_t()
    window.show()
    sys.exit(app.exec_())