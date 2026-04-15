# animation_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage, QColor, QIcon

class AnimationModel:
    """Модель данных анимации (последовательность кадров)."""
    def __init__(self):
        self.frames = []          # список словарей: {'pixels': dict, 'width': int, 'height': int}
        self.current_frame_index = -1

    def add_frame(self, pixels, width, height):
        """Добавляет кадр в конец списка."""
        # Глубокое копирование словаря пикселей
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
    """Панель управления анимацией."""
    frameAdded = pyqtSignal()               # при добавлении кадра
    frameSelected = pyqtSignal(int)         # при выборе кадра (индекс)
    frameDeleted = pyqtSignal(int)          # при удалении кадра
    playStateChanged = pyqtSignal(bool)     # True - играет, False - стоп

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.next_frame)
        self.is_playing = False
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
        self.frame_list.setIconSize(self.frame_list.iconSize() * 0.5)
        layout.addWidget(self.frame_list)

        self.setMinimumHeight(150)

    def on_add_frame(self):
        """Сигнал добавления кадра (будет обработан в WorkArea)."""
        self.frameAdded.emit()

    def add_frame_to_list(self, index, pixmap=None):
        """Добавляет визуальный элемент в список кадров."""
        item = QListWidgetItem(f"Кадр {index+1}")
        if pixmap:
            item.setIcon(QIcon(pixmap))  # преобразование QPixmap -> QIcon
        self.frame_list.addItem(item)
        self.frame_list.setCurrentRow(index)

    def on_frame_selection_changed(self):
        selected = self.frame_list.currentRow()
        if selected >= 0 and selected < len(self.model.frames):
            self.frameSelected.emit(selected)

    def on_delete_frame(self):
        selected = self.frame_list.currentRow()
        if selected >= 0:
            self.frameDeleted.emit(selected)
            self.frame_list.takeItem(selected)
            # Обновляем номера кадров в списке
            for i in range(self.frame_list.count()):
                self.frame_list.item(i).setText(f"Кадр {i+1}")

    def toggle_play(self):
        if not self.is_playing:
            if len(self.model.frames) > 0:
                self.is_playing = True
                self.play_btn.setText("⏸ Стоп")
                self.play_timer.start(100)  # 10 кадров в секунду
                self.playStateChanged.emit(True)
        else:
            self.stop_playback()

    def stop_playback(self):
        self.is_playing = False
        self.play_btn.setText("▶ Воспроизвести")
        self.play_timer.stop()
        self.playStateChanged.emit(False)

    def next_frame(self):
        """Переключение на следующий кадр при воспроизведении."""
        if not self.is_playing or len(self.model.frames) == 0:
            return
        current = self.frame_list.currentRow()
        next_idx = (current + 1) % len(self.model.frames)
        self.frame_list.setCurrentRow(next_idx)
        self.frameSelected.emit(next_idx)

    def clear_list(self):
        self.frame_list.clear()

    def update_after_delete(self, new_current_index):
        if new_current_index >= 0 and new_current_index < self.frame_list.count():
            self.frame_list.setCurrentRow(new_current_index)