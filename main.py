import sys
from PyQt5.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv)        # Создаём приложение
window = QWidget()                  # Создаём виджет (окно)
window.setWindowTitle("PixelArt")   # Заголовок окна
window.resize(1920, 1080)             # Размер окна (ширина, высота)
window.show()                       # Показываем окно
sys.exit(app.exec_())               # Запускаем главный цикл обработки событий