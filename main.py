import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile, QTextStream
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Загрузка стилей
    file = QFile("style.qss")
    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
        file.close()
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())