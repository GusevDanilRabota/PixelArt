from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QVBoxLayout, QStatusBar,
    QAction, QWidget
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

        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

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
        print("Создать новый файл")

    def on_open_file(self):
        print("Открыть файл")

    def on_save_file(self):
        print("Сохранить файл")

    def on_about(self):
        print("О программе PixelArt")