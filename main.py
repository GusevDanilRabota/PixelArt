import sys
from PyQt5.QtWidgets import QApplication, QWidget, QSplitter, QTextEdit, QVBoxLayout
from PyQt5.QtCore import Qt

class main_window_t(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelArt") # Заголовок окна
        self.resize(1920, 1080)         # Размер окна (ширина, высота)

        # Создаём сплиттер с горизонтальным разделением (лево-право)
        splitter = QSplitter(Qt.Horizontal)

        # Файловое дерево/ Набор инструментов/ (текстовое поле)
        files_tree_widget = QTextEdit()
        files_tree_widget.setPlainText("Файловое дерево/ Набор инструментов/")

        # Рабочая область (текстовое поле)
        work_spase_widget = QTextEdit()
        work_spase_widget.setPlainText("Рабочая область")

        # Опционально: минимальные ширины, чтобы ползунок не схлопывал часть до нуля
        files_tree_widget.setMinimumWidth(50)
        work_spase_widget.setMinimumWidth(50)

        # Добавляем виджеты в сплиттер
        splitter.addWidget(files_tree_widget)
        splitter.addWidget(work_spase_widget)

        # Начальные пропорции (ширина левой и правой частей)
        splitter.setSizes([200, 400])

        # Размещаем сплиттер в окне
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main_window_t()
    window.show()
    sys.exit(app.exec_())