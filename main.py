import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QSplitter, QTextEdit,
    QVBoxLayout, QTabWidget
)
from PyQt5.QtCore import Qt

class main_window_t(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelArt")
        self.resize(1920, 1080)

        # Основной горизонтальный разделитель (левая панель / рабочая область)
        main_splitter = QSplitter(Qt.Horizontal)

        # --- Левая часть: вкладки (Файлы / Инструменты) ---
        tab_widget = QTabWidget()
        file_tree_tab = QTextEdit()
        file_tree_tab.setPlainText("Файловое дерево")
        tab_widget.addTab(file_tree_tab, "Файлы")
        tools_tab = QTextEdit()
        tools_tab.setPlainText("Инструменты")
        tab_widget.addTab(tools_tab, "Инструменты")
        tab_widget.setMinimumWidth(200)

        # --- Правая часть: рабочая область, разбитая на три части ---
        # Вертикальный разделитель для рабочей области
        work_vertical_splitter = QSplitter(Qt.Vertical)

        # Верхняя часть: горизонтальный разделитель (рисование / цвет)
        top_horizontal_splitter = QSplitter(Qt.Horizontal)

        # Левая верхняя: область рисования по пикселям
        draw_widget = QTextEdit()
        draw_widget.setPlainText("Область рисования (пиксельная сетка)")
        draw_widget.setMinimumSize(400, 300)

        # Правая верхняя: выбор цвета
        color_widget = QTextEdit()
        color_widget.setPlainText("Палитра / выбор цвета")
        color_widget.setMinimumSize(150, 300)

        top_horizontal_splitter.addWidget(draw_widget)
        top_horizontal_splitter.addWidget(color_widget)
        top_horizontal_splitter.setSizes([600, 200])  # начальные пропорции

        # Нижняя часть: виджет анимаций
        animation_widget = QTextEdit()
        animation_widget.setPlainText("Шкала анимации / кадры")
        animation_widget.setMinimumHeight(150)

        # Добавляем верхний разделитель и нижний виджет в вертикальный разделитель
        work_vertical_splitter.addWidget(top_horizontal_splitter)
        work_vertical_splitter.addWidget(animation_widget)
        work_vertical_splitter.setSizes([600, 200])  # высоты верхней и нижней частей

        work_vertical_splitter.setMinimumWidth(500)

        # Собираем основной разделитель
        main_splitter.addWidget(tab_widget)
        main_splitter.addWidget(work_vertical_splitter)
        main_splitter.setSizes([250, 800])

        # Размещаем основной разделитель в окне
        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = main_window_t()
    window.show()
    sys.exit(app.exec_())