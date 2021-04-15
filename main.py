import sys
from PyQt5.QtWidgets import \
    QApplication, QMainWindow, QLabel

from PyQt5.QtGui import \
    QPixmap, QPainter, QColor, QPen

from PyQt5.QtCore import \
    Qt, QPoint, pyqtSignal


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        pass


if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec_()


