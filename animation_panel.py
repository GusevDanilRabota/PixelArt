# animation_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QSpinBox, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QPixmap, QImage, QIcon

class AnimationModel:
    """Модель данных анимации (последовательность кадров)."""
    def __init__(self):
        self.frames = []          # список словарей: {'pixels': dict, 'width': int, 'height': int}
        self.current_frame_index = -1

    def add_frame(self, pixels, width, height):
        """Добавляет кадр в конец списка."""
        frame_pixels = {pos: idx for pos, idx in pixels.items()}
        self.frames.append({
            'pixels': frame_pixels,
            'width': width,
            'height': height
        })
        self.current_frame_index = len(self.frames) - 1
        return self.current_frame_index

    def get_frame(self, index):
        if 0 <= index < len(self.frames):
            return self.frames[index]
        return None

    def delete_frame(self, index):
        if 0 <= index < len(self.frames):
            del self.frames[index]
            if self.current_frame_index >= len(self.frames):
                self.current_frame_index = len(self.frames) - 1
            return True
        return False

    def clear(self):
        self.frames.clear()
        self.current_frame_index = -1


class AnimationPanel(QWidget):
    """Панель управления анимацией с предпросмотром."""
    frameAdded = pyqtSignal()
    frameSelected = pyqtSignal(int)   # выбор кадра для редактирования
    frameDeleted = pyqtSignal(int)

    def __init__(self, model, palette_model):
        super().__init__()
        self.model = model
        self.palette_model = palette_model
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.next_preview_frame)
        self.is_playing = False
        self.playback_index = 0
        self.fps = 10
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить кадр")
        self.add_btn.clicked.connect(self.on_add_frame)
        self.play_btn = QPushButton("▶ Воспроизвести")
        self.play_btn.clicked.connect(self.toggle_play)
        self.delete_btn = QPushButton("Удалить кадр")
        self.delete_btn.clicked.connect(self.on_delete_frame)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.play_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        # Список кадров
        self.frame_list = QListWidget()
        self.frame_list.setSelectionMode(QListWidget.SingleSelection)
        self.frame_list.itemSelectionChanged.connect(self.on_frame_selection_changed)
        self.frame_list.setIconSize(QSize(50, 50))
        layout.addWidget(self.frame_list)

        # Предпросмотр анимации
        preview_label_title = QLabel("Предпросмотр анимации:")
        layout.addWidget(preview_label_title)
        self.preview_label = QLabel()
        self.preview_label.setMinimumHeight(120)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #1e1e1e; border: 1px solid #444;")
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.preview_label)

        # Управление FPS
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(10)
        self.fps_spin.valueChanged.connect(self.on_fps_changed)
        fps_layout.addWidget(self.fps_spin)
        fps_layout.addStretch()
        layout.addLayout(fps_layout)

        self.update_preview()

    def create_frame_thumbnail(self, index):
        """Создаёт QPixmap для кадра по индексу."""
        frame = self.model.get_frame(index)
        if not frame:
            return QPixmap()
        w, h = frame['width'], frame['height']
        image = QImage(w, h, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        for (x, y), idx in frame['pixels'].items():
            color = self.palette_model.get_color(idx)
            image.setPixelColor(x, y, color)
        pixmap = QPixmap.fromImage(image)
        return pixmap

    def update_preview(self):
        """Обновить изображение в preview_label."""
        if 0 <= self.playback_index < len(self.model.frames):
            pixmap = self.create_frame_thumbnail(self.playback_index)
            # Масштабируем с сохранением пропорций под размер label
            scaled = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled)
        else:
            self.preview_label.clear()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_preview()

    def on_fps_changed(self, value):
        self.fps = value
        if self.is_playing:
            self.play_timer.setInterval(1000 // self.fps)

    def toggle_play(self):
        if not self.is_playing:
            if len(self.model.frames) > 0:
                self.is_playing = True
                self.play_btn.setText("⏸ Стоп")
                current = self.frame_list.currentRow()
                self.playback_index = current if current >= 0 else 0
                self.play_timer.start(1000 // self.fps)
        else:
            self.stop_playback()

    def stop_playback(self):
        self.is_playing = False
        self.play_btn.setText("▶ Воспроизвести")
        self.play_timer.stop()

    def next_preview_frame(self):
        if not self.is_playing or len(self.model.frames) == 0:
            return
        self.playback_index = (self.playback_index + 1) % len(self.model.frames)
        self.update_preview()

    def on_add_frame(self):
        self.frameAdded.emit()

    def add_frame_to_list(self, index, pixmap=None):
        item = QListWidgetItem(f"Кадр {index+1}")
        if pixmap:
            item.setIcon(QIcon(pixmap))
        self.frame_list.addItem(item)
        self.frame_list.setCurrentRow(index)
        self.playback_index = index
        self.update_preview()

    def on_frame_selection_changed(self):
        selected = self.frame_list.currentRow()
        if selected >= 0:
            self.frameSelected.emit(selected)
            if not self.is_playing:
                self.playback_index = selected
                self.update_preview()

    def on_delete_frame(self):
        selected = self.frame_list.currentRow()
        if selected >= 0:
            self.frameDeleted.emit(selected)
            self.frame_list.takeItem(selected)
            for i in range(self.frame_list.count()):
                self.frame_list.item(i).setText(f"Кадр {i+1}")
            self.update_preview()

    def clear_list(self):
        self.frame_list.clear()
        self.update_preview()