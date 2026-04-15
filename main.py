import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QSplitter, QTextEdit,
    QVBoxLayout, QTabWidget
)
from PyQt5.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelArt")
        self.resize(1920, 1080)

        # Создаём все компоненты
        left_panel = self._create_left_panel()
        work_area = self._create_work_area()

        # Основной горизонтальный разделитель
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(work_area)
        main_splitter.setSizes([250, 800])

        # Главный layout
        layout = QVBoxLayout()
        layout.addWidget(main_splitter)
        self.setLayout(layout)

    def _create_left_panel(self):
        """Левая панель с вкладками (Файлы / Инструменты)"""
        tab_widget = QTabWidget()
        tab_widget.setMinimumWidth(200)

        # Вкладка "Файлы"
        file_tree_tab = QTextEdit()
        file_tree_tab.setPlainText("Файловое дерево")
        tab_widget.addTab(file_tree_tab, "Файлы")

        # Вкладка "Инструменты"
        tools_tab = QTextEdit()
        tools_tab.setPlainText("Инструменты")
        tab_widget.addTab(tools_tab, "Инструменты")

        return tab_widget

    def _create_work_area(self):
        """Рабочая область: верх (рисование + палитра) и низ (анимация)"""
        work_splitter = QSplitter(Qt.Vertical)
        work_splitter.setMinimumWidth(500)

        # Верхняя часть
        top_area = self._create_top_area()
        work_splitter.addWidget(top_area)

        # Нижняя часть (анимация)
        animation_panel = self._create_animation_panel()
        work_splitter.addWidget(animation_panel)

        work_splitter.setSizes([600, 200])
        return work_splitter

    def _create_top_area(self):
        """Верхняя часть: рисование (слева) и палитра (справа)"""
        top_splitter = QSplitter(Qt.Horizontal)

        drawing_panel = self._create_drawing_panel()
        top_splitter.addWidget(drawing_panel)

        color_panel = self._create_color_panel()
        top_splitter.addWidget(color_panel)

        top_splitter.setSizes([600, 200])
        return top_splitter

    def _create_drawing_panel(self):
        """Панель рисования по пикселям"""
        widget = QTextEdit()
        widget.setPlainText("Область рисования (пиксельная сетка)")
        widget.setMinimumSize(400, 300)
        return widget

    def _create_color_panel(self):
        """Панель выбора цвета / палитра"""
        widget = QTextEdit()
        widget.setPlainText("Палитра / выбор цвета")
        widget.setMinimumSize(150, 300)
        return widget

    def _create_animation_panel(self):
        """Нижняя панель анимации"""
        widget = QTextEdit()
        widget.setPlainText("Шкала анимации / кадры")
        widget.setMinimumHeight(150)
        return widget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())