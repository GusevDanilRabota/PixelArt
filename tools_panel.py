# tools_panel.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSlider, QSpinBox, QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSignal

class ToolsPanel(QWidget):
    toolChanged = pyqtSignal(str)      # 'pen', 'eraser', 'eyedropper'
    zoomChanged = pyqtSignal(int)      # значение размера пикселя

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Группа инструментов
        tools_label = QLabel("Инструменты")
        layout.addWidget(tools_label)

        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)

        self.pen_btn = QPushButton("Карандаш")
        self.pen_btn.setCheckable(True)
        self.pen_btn.setChecked(True)
        self.pen_btn.clicked.connect(lambda: self.toolChanged.emit('pen'))

        self.eraser_btn = QPushButton("Ластик")
        self.eraser_btn.setCheckable(True)
        self.eraser_btn.clicked.connect(lambda: self.toolChanged.emit('eraser'))

        self.eyedropper_btn = QPushButton("Пипетка")
        self.eyedropper_btn.setCheckable(True)
        self.eyedropper_btn.clicked.connect(lambda: self.toolChanged.emit('eyedropper'))

        self.tool_group.addButton(self.pen_btn)
        self.tool_group.addButton(self.eraser_btn)
        self.tool_group.addButton(self.eyedropper_btn)

        layout.addWidget(self.pen_btn)
        layout.addWidget(self.eraser_btn)
        layout.addWidget(self.eyedropper_btn)

        layout.addSpacing(20)

        # Управление зумом
        zoom_label = QLabel("Масштаб")
        layout.addWidget(zoom_label)

        zoom_controls = QHBoxLayout()
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(5, 40)      # pixel_size от 5 до 40
        self.zoom_slider.setValue(20)         # значение по умолчанию 20
        self.zoom_slider.setTickInterval(5)
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)

        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(5, 40)
        self.zoom_spin.setValue(20)
        self.zoom_spin.setSuffix(" px")

        # Синхронизация слайдера и спинбокса
        self.zoom_slider.valueChanged.connect(self.zoom_spin.setValue)
        self.zoom_spin.valueChanged.connect(self.zoom_slider.setValue)
        self.zoom_slider.valueChanged.connect(self.zoomChanged.emit)

        zoom_controls.addWidget(self.zoom_slider)
        zoom_controls.addWidget(self.zoom_spin)

        layout.addLayout(zoom_controls)
        layout.addStretch()

    def set_zoom(self, value):
        """Установить значение зума извне."""
        self.zoom_slider.setValue(value)