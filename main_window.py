from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QVBoxLayout, QStatusBar,
    QAction, QWidget, QInputDialog
)
from PyQt5.QtCore import Qt
from left_panel import LeftPanel
from work_area import WorkArea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelArt")
        self.resize(1920, 1080)

        self._create_menu_bar()
        self.left_panel = LeftPanel()
        self.work_area = WorkArea()

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.left_panel)
        main_splitter.addWidget(self.work_area)
        main_splitter.setSizes([250, 800])

        self._create_status_bar()

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(main_splitter)
        self.setCentralWidget(central_widget)

    def _create_menu_bar(self):
        menubar = self.menuBar()

        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')

        new_action = QAction('Новый', self)
        new_action.triggered.connect(self.on_new_file)
        file_menu.addAction(new_action)

        open_action = QAction('Открыть...', self)
        open_action.triggered.connect(self.on_open_file)
        file_menu.addAction(open_action)

        save_action = QAction('Сохранить', self)
        save_action.triggered.connect(self.on_save_file)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        resize_action = QAction('Размер холста...', self)
        resize_action.triggered.connect(self.on_resize_canvas)
        file_menu.addAction(resize_action)

        file_menu.addSeparator()

        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню "Помощь"
        help_menu = menubar.addMenu('Помощь')
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        status = QStatusBar()
        status.showMessage("Готов к работе")
        self.setStatusBar(status)

    # Обработчики
    def on_new_file(self):
        self.work_area.drawing_panel.clear()

    def on_open_file(self):
        print("Открыть файл")

    def on_save_file(self):
        print("Сохранить файл")

    def on_about(self):
        print("О программе PixelArt")

    def on_resize_canvas(self):
        current_w = self.work_area.drawing_panel.grid_width
        current_h = self.work_area.drawing_panel.grid_height

        width, ok1 = QInputDialog.getInt(
            self, "Размер холста", "Ширина (в пикселях):",
            value=current_w, min=1, max=1024
        )
        if not ok1:
            return
        height, ok2 = QInputDialog.getInt(
            self, "Размер холста", "Высота (в пикселях):",
            value=current_h, min=1, max=1024
        )
        if ok2:
            self.work_area.drawing_panel.set_grid_size(width, height)