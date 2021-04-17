from PyQt5.QtWidgets import \
    QLabel, QSlider, QApplication

from PyQt5.QtGui import \
    QPixmap

from PyQt5.QtCore import \
    Qt, pyqtSignal
    
# Image Hint Label
class ImageHintLabel(QLabel):
    def __init__(self, 
                 size:tuple=(340, 180)) -> QLabel:
        super().__init__()
        
        self.setWindowFlag(Qt.FramelessWindowHint)
        
        self.size = size
        
    def setPixmap(self, pixmap):
        if pixmap.width() / pixmap.height() > 1:
            pixmap = pixmap.scaledToWidth(self.size[0])
        else:
            pixmap = pixmap.scaledToHeight(self.size[1])
        
        super().setPixmap(pixmap)

class HintSlider(QSlider):
    update_canvas = pyqtSignal(int)
    
    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        
        self.parent = parent
        
        self.hint_label = ImageHintLabel()
        
        self.setSingleStep(1)
        
        self.min_val = 0
        self.max_val = 1
        
        self.setRange(self.min_val, self.max_val)
        
    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            ev.accept()
            x = ev.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
            self.setValue(int(value))
            
            # TODO
            self.hint_label.setPixmap(QPixmap(self.parent.get_image_path(self.value())))
            self.hint_label.move(self.parent.x()+self.x()+ev.x()+20,
                                 self.parent.y()+self.y()-130)
            self.hint_label.show()
        else:
            return super().mousePressEvent(ev)
        
    def mouseMoveEvent(self, ev):
        if ev.buttons() & Qt.LeftButton:
            ev.accept()
            x = ev.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
            self.setValue(int(value))
            
            # TODO
            self.hint_label.setPixmap(QPixmap(self.parent.get_image_path(self.value())))
            self.hint_label.move(self.parent.x()+self.x()+ev.x()+20,
                                 self.parent.y()+self.y()-130)
        else:
            return super().mouseMoveEvent(ev)
    
    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self.update_canvas.emit(self.value())
            self.hint_label.hide()
        else:
            return super().mousePressEvent(ev)
    
    def setValue(self, v):
        if v < self.min_value:
            v = self.min_value
        
        if v > self.max_value:
            v = self.max_value
        super().setValue(v)
        
    def setRange(self, min_val, max_val):
        self.min_value = min_val
        self.max_value = max_val
        
        super().setRange(min_val, max_val)

if __name__ == "__main__":
    app = QApplication([])
    w = HintSlider(Qt.Horizontal,
                   None)
    w.show()
    app.exec_()