# main_window.py
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QVBoxLayout, QStatusBar, QLabel,
    QAction, QWidget, QInputDialog, QFileDialog, QMessageBox,
    QDialog, QFormLayout, QSpinBox, QCheckBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QColor, QImage
from left_panel import LeftPanel
from work_area import WorkArea
from PIL import Image
import numpy as np
import io

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PixelArt")
        self.resize(1920, 1080)

        # Сначала создаём панели
        self.left_panel = LeftPanel()
        self.work_area = WorkArea()

        # Теперь создаём действия (они используют self.work_area)
        self._create_actions()

        # Затем создаём меню (использует действия и work_area)
        self._create_menu_bar()

        # Связываем сигналы инструментов и зума
        tools = self.left_panel.tools_panel
        tools.toolChanged.connect(self.work_area.drawing_panel.set_tool)
        tools.zoomChanged.connect(self.work_area.drawing_panel.set_zoom)
        self.work_area.drawing_panel.colorPicked.connect(self.on_color_picked)

        # Основной сплиттер
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.left_panel)
        main_splitter.addWidget(self.work_area)
        main_splitter.setSizes([250, 800])

        # Строка состояния
        self._create_status_bar()
        self._connect_status_signals()

        # Центральный виджет
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(main_splitter)
        self.setCentralWidget(central_widget)

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

        self.fill_action = QAction("Заливка", self)
        self.fill_action.setShortcut(QKeySequence("G"))
        # self.fill_action.triggered.connect(...)  # TODO: реализовать заливку
        self.addAction(self.fill_action)

        # Отмена / повтор
        self.undo_action = QAction("Отменить", self)
        self.undo_action.setShortcut(QKeySequence.Undo)  # Ctrl+Z
        self.undo_action.triggered.connect(self.work_area.drawing_panel.undo)
        self.addAction(self.undo_action)

        self.redo_action = QAction("Повторить", self)
        self.redo_action.setShortcut(QKeySequence.Redo)  # Ctrl+Y
        self.redo_action.triggered.connect(self.work_area.drawing_panel.redo)
        self.addAction(self.redo_action)

        # Сохранение
        self.save_action = QAction("Сохранить", self)
        self.save_action.setShortcut(QKeySequence.Save)  # Ctrl+S
        self.save_action.triggered.connect(self.on_save_file)
        self.addAction(self.save_action)

        # Удаление кадра
        self.delete_frame_action = QAction("Удалить кадр", self)
        self.delete_frame_action.setShortcut(QKeySequence.Delete)
        self.delete_frame_action.triggered.connect(self.work_area.animation_panel.on_delete_frame)
        self.addAction(self.delete_frame_action)

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

    def _create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('Файл')

        new_action = QAction('Новый', self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.on_new_file)
        file_menu.addAction(new_action)

        open_action = QAction('Открыть...', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.on_open_file)
        file_menu.addAction(open_action)

        file_menu.addAction(self.save_action)

        file_menu.addSeparator()

        export_action = QAction('Экспорт спрайт-листа...', self)
        export_action.triggered.connect(self.on_export_spritesheet)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        resize_action = QAction('Размер холста...', self)
        resize_action.triggered.connect(self.on_resize_canvas)
        file_menu.addAction(resize_action)

        file_menu.addSeparator()
        exit_action = QAction('Выход', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Вид
        view_menu = menubar.addMenu('Вид')
        view_menu.addAction(self.toggle_left_panel_action)
        view_menu.addAction(self.toggle_color_panel_action)
        view_menu.addAction(self.toggle_animation_panel_action)

        help_menu = menubar.addMenu('Помощь')
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.coord_label = QLabel("X: --, Y: --")
        self.color_label = QLabel("Цвет: ")
        self.color_sample = QLabel()
        self.color_sample.setFixedSize(16, 16)
        self.color_sample.setStyleSheet("border: 1px solid #888; background-color: #000;")

        self.statusBar.addPermanentWidget(self.coord_label)
        self.statusBar.addPermanentWidget(self.color_label)
        self.statusBar.addPermanentWidget(self.color_sample)

        self.statusBar.showMessage("Готов")

    def _connect_status_signals(self):
        dp = self.work_area.drawing_panel
        dp.cursorMoved.connect(self.update_coords)
        dp.colorChanged.connect(self.update_color_display)
        # начальное значение цвета
        idx = self.work_area.palette_model.active_color_index
        dp.colorChanged.emit(self.work_area.palette_model.get_color(idx))

    def update_coords(self, x, y):
        if x >= 0 and y >= 0:
            self.coord_label.setText(f"X: {x}, Y: {y}")
        else:
            self.coord_label.setText("X: --, Y: --")

    def update_color_display(self, color: QColor):
        self.color_label.setText(f"Цвет: {color.name()}")
        self.color_sample.setStyleSheet(f"border: 1px solid #888; background-color: {color.name()};")

    def on_color_picked(self, index):
        pw = self.work_area.color_panel.palette_widget
        if 0 <= index < len(pw.swatches):
            pw.set_active_color(index)

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

    def on_export_spritesheet(self):
        frames = self.work_area.animation_model.frames
        if not frames:
            QMessageBox.warning(self, "Экспорт", "Нет кадров для экспорта.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Параметры спрайт-листа")
        layout = QFormLayout(dialog)

        cols_spin = QSpinBox()
        cols_spin.setRange(1, len(frames))
        cols_spin.setValue(min(4, len(frames)))
        layout.addRow("Количество столбцов:", cols_spin)

        spacing_spin = QSpinBox()
        spacing_spin.setRange(0, 20)
        spacing_spin.setValue(1)
        layout.addRow("Отступ между кадрами (px):", spacing_spin)

        transparent_cb = QCheckBox()
        transparent_cb.setChecked(True)
        layout.addRow("Прозрачный фон:", transparent_cb)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        if dialog.exec_() != QDialog.Accepted:
            return

        cols = cols_spin.value()
        spacing = spacing_spin.value()
        use_transparency = transparent_cb.isChecked()

        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить спрайт-лист", "", "PNG Files (*.png)")
        if not file_path:
            return

        try:
            self._export_spritesheet(frames, cols, spacing, use_transparency, file_path)
            QMessageBox.information(self, "Экспорт", f"Спрайт-лист сохранён в {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")

    def _export_spritesheet(self, frames, cols, spacing, transparent, output_path):
        widths = [f['width'] for f in frames]
        heights = [f['height'] for f in frames]
        max_w = max(widths) if widths else 1
        max_h = max(heights) if heights else 1

        rows = (len(frames) + cols - 1) // cols
        sheet_w = cols * max_w + (cols - 1) * spacing
        sheet_h = rows * max_h + (rows - 1) * spacing

        if transparent:
            sheet_img = Image.new('RGBA', (sheet_w, sheet_h), (0, 0, 0, 0))
        else:
            sheet_img = Image.new('RGBA', (sheet_w, sheet_h), (255, 255, 255, 255))

        palette_model = self.work_area.palette_model

        for idx, frame in enumerate(frames):
            row = idx // cols
            col = idx % cols
            x_offset = col * (max_w + spacing)
            y_offset = row * (max_h + spacing)

            w, h = frame['width'], frame['height']
            qimg = QImage(w, h, QImage.Format_ARGB32)
            qimg.fill(Qt.transparent)
            for (x, y), color_idx in frame['pixels'].items():
                color = palette_model.get_color(color_idx)
                qimg.setPixelColor(x, y, color)

            buffer = io.BytesIO()
            qimg.save(buffer, 'PNG')
            buffer.seek(0)
            frame_img = Image.open(buffer).convert('RGBA')
            sheet_img.paste(frame_img, (x_offset, y_offset), frame_img)

        sheet_img.save(output_path, 'PNG')