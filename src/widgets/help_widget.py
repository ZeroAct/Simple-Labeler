from PyQt5.QtWidgets import \
    QApplication, QLabel, QWidget, QVBoxLayout, QGroupBox

from PyQt5.QtGui import \
    QPixmap, QPainter, QColor, QPen, QFont

from PyQt5.QtCore import \
    Qt, QPoint, pyqtSignal

# Canvs Class
class HelpWidget(QGroupBox):
    def __init__(self):
        super().__init__("사용방법")
        
        l = QVBoxLayout()
        l.addWidget(QLabel("프레임 이동 : a, s"))
        l.addWidget(QLabel("박스 확정 : space, enter"))
        l.addWidget(QLabel("박스 선택 : 마우스 우클릭"))
        l.addWidget(QLabel("현재 박스 제거 : 마우스 우클릭"))
        
        self.setLayout(l)

if __name__ == "__main__":
    app = QApplication([])
    w = HelpWidget()
    w.show()
    app.exec_()