# main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QVBoxLayout, QStatusBar,
    QAction, QWidget, QInputDialog, QFileDialog, QMessageBox, QMenu
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPainter, QColor, QKeySequence
from left_panel import LeftPanel
from work_area import WorkArea
from PIL import Image
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelArt")
        self.resize(1920, 1080)

        self._create_menu_bar()
        self.left_panel = LeftPanel()
        self.work_area = WorkArea()

        # Связываем инструменты и зум из левой панели
        tools = self.left_panel.tools_panel
        tools.toolChanged.connect(self.work_area.drawing_panel.set_tool)
        tools.zoomChanged.connect(self.work_area.drawing_panel.set_zoom)

        # При выборе цвета пипеткой обновляем выделение в палитре
        self.work_area.drawing_panel.colorPicked.connect(self.on_color_picked)

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

        self._create_actions()
        self._create_view_menu()

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

        resize_action = QAction('Размер холста...', self)
        resize_action.triggered.connect(self.on_resize_canvas)
        file_menu.addAction(resize_action)

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

    def on_new_file(self):
        # Сброс анимации
        self.work_area.animation_model.clear()
        self.work_area.animation_panel.clear_list()
        self.work_area.drawing_panel.clear_onion_skin()
        # Сброс холста
        self.work_area.drawing_panel.set_grid_size(32, 32)
        self.work_area.palette_model.set_bit_depth(8)
        self.work_area.color_panel.palette_widget.bit_depth_spin.setValue(8)
        self.work_area.color_panel.palette_widget.update_palette()
        self.work_area.drawing_panel.clear()

    def on_open_file(self):
        print("Открыть файл")

    def on_save_file(self):
        # Сохраняем текущий кадр как PNG с индексированной палитрой
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "", "PNG Files (*.png)")
        if not file_path:
            return

        w = self.work_area.drawing_panel.grid_width
        h = self.work_area.drawing_panel.grid_height
        palette_model = self.work_area.palette_model

        indices = np.zeros((h, w), dtype=np.uint8)
        for (x, y), index in self.work_area.drawing_panel.pixels.items():
            if 0 <= x < w and 0 <= y < h:
                indices[y, x] = index

        palette = []
        for color in palette_model.colors[:palette_model.max_colors]:
            palette.extend([color.red(), color.green(), color.blue()])
        while len(palette) < 768:
            palette.extend([0, 0, 0])

        img = Image.fromarray(indices, mode='P')
        img.putpalette(palette)

        transparent_index = None
        for i, color in enumerate(palette_model.colors):
            if color.alpha() == 0:
                transparent_index = i
                break

        if transparent_index is not None:
            transparency = bytes([0 if i == transparent_index else 255 for i in range(palette_model.max_colors)])
            img.info['transparency'] = transparency

        img.save(file_path, format='PNG', transparency=transparent_index)
        QMessageBox.information(self, "Сохранение", f"Изображение сохранено в {file_path}")

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

    def on_color_picked(self, index):
        """Обновить выделение цвета в виджете палитры."""
        pw = self.work_area.color_panel.palette_widget
        if 0 <= index < len(pw.swatches):
            pw.set_active_color(index)

    def _create_actions(self):
        # Инструменты
        self.pen_action = QAction("Карандаш", self)
        self.pen_action.setShortcut(QKeySequence("B"))
        self.pen_action.triggered.connect(lambda: self.work_area.drawing_panel.set_tool('pen'))
        self.addAction(self.pen_action)

        self.eraser_action = QAction("Ластик", self)
        self.eraser_action.setShortcut(QKeySequence("E"))
        self.eraser_action.triggered.connect(lambda: self.work_area.drawing_panel.set_tool('eraser'))
        self.addAction(self.eraser_action)

        self.eyedropper_action = QAction("Пипетка", self)
        self.eyedropper_action.setShortcut(QKeySequence("I"))
        self.eyedropper_action.triggered.connect(lambda: self.work_area.drawing_panel.set_tool('eyedropper'))
        self.addAction(self.eyedropper_action)

        # Заливка (пока не реализована, добавим позже)
        self.fill_action = QAction("Заливка", self)
        self.fill_action.setShortcut(QKeySequence("G"))
        # self.fill_action.triggered.connect(...)
        self.addAction(self.fill_action)

        # Отмена / повтор
        self.undo_action = QAction("Отменить", self)
        self.undo_action.setShortcut(QKeySequence.Undo)  # Ctrl+Z
        self.undo_action.triggered.connect(self.work_area.drawing_panel.undo)
        self.addAction(self.undo_action)

        self.redo_action = QAction("Повторить", self)
        self.redo_action.setShortcut(QKeySequence.Redo)  # Ctrl+Y или Ctrl+Shift+Z
        self.redo_action.triggered.connect(self.work_area.drawing_panel.redo)
        self.addAction(self.redo_action)

        # Сохранение
        self.save_action = QAction("Сохранить", self)
        self.save_action.setShortcut(QKeySequence.Save)  # Ctrl+S
        self.save_action.triggered.connect(self.on_save_file)
        self.addAction(self.save_action)

        # Переключение панелей
        self.toggle_left_panel_action = QAction("Левая панель", self, checkable=True)
        self.toggle_left_panel_action.setChecked(True)
        self.toggle_left_panel_action.setShortcut(QKeySequence("Ctrl+1"))
        self.toggle_left_panel_action.toggled.connect(self.left_panel.setVisible)
        self.addAction(self.toggle_left_panel_action)

        self.toggle_color_panel_action = QAction("Палитра", self, checkable=True)
        self.toggle_color_panel_action.setChecked(True)
        self.toggle_color_panel_action.setShortcut(QKeySequence("Ctrl+2"))
        self.toggle_color_panel_action.toggled.connect(self.work_area.color_panel.setVisible)
        self.addAction(self.toggle_color_panel_action)

        self.toggle_animation_panel_action = QAction("Анимация", self, checkable=True)
        self.toggle_animation_panel_action.setChecked(True)
        self.toggle_animation_panel_action.setShortcut(QKeySequence("Ctrl+3"))
        self.toggle_animation_panel_action.toggled.connect(self.work_area.animation_panel.setVisible)
        self.addAction(self.toggle_animation_panel_action)

    def _create_view_menu(self):
        view_menu = self.menuBar().addMenu("Вид")
        view_menu.addAction(self.toggle_left_panel_action)
        view_menu.addAction(self.toggle_color_panel_action)
        view_menu.addAction(self.toggle_animation_panel_action)