from PyQt5.QtWidgets import \
    QApplication, QLabel

from PyQt5.QtGui import \
    QPixmap, QPainter, QColor, QPen, QFont

from PyQt5.QtCore import \
    Qt, QPoint, pyqtSignal

from src.utils.color import color_list
from src.utils.dtype import Annotation

# Canvs Class
class Canvas(QLabel):
    get_annotation = pyqtSignal(Annotation)
    get_clicked_pos = pyqtSignal(int, int)
    
    def __init__(self,
                 parent:object,
                 size:tuple,
                 pixmap:QPixmap = None) -> QLabel:
        super().__init__(parent)
        
        ### initialize canvas
        self.size             = size
        self.aspect_ratio     = size[0]/size[1]
        
        self.ori              = None
        self.original_size    = size
        self._pixmap          = pixmap if pixmap is not None else QPixmap(500, 500)
        
        self.click_offset     = 3
        
        ### manage offset
        self.x_offset         = 0
        self.y_offset         = 0
        self.x_ratio          = 1.
        self.y_ratio          = 1.
        
        ### painter
        self._painter         = QPainter()
        self.mouse_x          = -999
        self.mouse_y          = -999
        
        ### drawing
        self.drawing          = False
        self.modifing_index   = -1
        self.is_mouse_pressed = False
        
        # Annotation class
        self.drawing_annot    = Annotation()
        
        self.init_canvas()
        
        self.setMouseTracking(True)
    
    def init_canvas(self):
        self.setFixedSize(*self.size)
        self.setPixmap(self._pixmap)
        self.setAlignment(Qt.AlignCenter)
    
    def is_valid_point(self, x, y):
        if self.x_offset <= x < self.size[0] - self.x_offset and \
            self.y_offset <= y < self.size[1] - self.y_offset:
                return True
        else:
            return False
    
    def is_on_annot(self, x, y):
        self.modifing_index = -1
        
        if self.drawing_annot.is_valid():
            x1, y1, x2, y2 = self.drawing_annot.get_pos()
            
            if x1 - self.click_offset < x < x1 + self.click_offset and y1 < y < y2:
                self.modifing_index = 0
            elif y1 - self.click_offset < y < y1 + self.click_offset and x1 < x < x2:
                self.modifing_index = 1
            elif x2 - self.click_offset < x < x2 + self.click_offset and y1 < y < y2:
                self.modifing_index = 2
            elif y2 - self.click_offset < y < y2 + self.click_offset and x1 < x < x2:
                self.modifing_index = 3
        
        return self.modifing_index
    
    def make_valid_point(self, x, y):
        if x < self.x_offset:
            x = self.x_offset
        elif x >= self.size[0] - self.x_offset:
            x = self.size[0] - self.x_offset - 1
            
        if y < self.y_offset:
            y = self.y_offset
        elif y >= self.size[1] - self.y_offset:
            y = self.size[1] - self.y_offset - 1
        
        return x, y
    
    def get_pixmap(self):
        return self._pixmap
    
    def paintEvent(self, ev):
        pixmap = self._pixmap.copy()
        
        p = self._painter
        p.begin(pixmap)
        
        p.translate(-self.x_offset, -self.y_offset)
        
        pen = QPen()
        if self.drawing_annot.is_valid():
            pen.setColor(QColor(*color_list[-1]))
            pen.setWidth(3)
            p.setPen(pen)
            
            if self.drawing_annot.get_draw_type() == "rect":
                x1, y1, x2, y2 = self.drawing_annot.get_pos()
                p.drawRect(x1, y1, x2-x1, y2-y1)
                
        pen.setColor(QColor(255, 255, 255, 100))
        pen.setWidth(3)
        p.setPen(pen)
        p.drawLine(self.mouse_x, -1, self.mouse_x, self.y_offset+pixmap.height()+1)
        p.drawLine(-1, self.mouse_y, self.x_offset+pixmap.width()+1, self.mouse_y)
        pen.setColor(QColor(255, 0, 0))
        pen.setWidth(1)
        p.setPen(pen)
        p.drawLine(self.mouse_x, -1, self.mouse_x, self.y_offset+pixmap.height()+1)
        p.drawLine(-1, self.mouse_y, self.x_offset+pixmap.width()+1, self.mouse_y)
        
        p.end()
        
        p.begin(self)
        p.drawPixmap(QPoint(self.x_offset, self.y_offset), pixmap, self.rect())
        p.end()
    
    def draw_annotations(self, annots):
        # pixmap = self._pixmap.copy()
        
        p = self._painter
        p.begin(self._pixmap)
        
        p.translate(-self.x_offset, -self.y_offset)
        
        pen = QPen()
        pen.setWidth(3)
        
        font = QFont()
        font.setBold(True)
        font.setPixelSize(14)
        p.setFont(font)
        
        for annot in annots.copy():
            annot.to_draw_pos(self.x_offset, self.y_offset, self.x_ratio, self.y_ratio)
            cat_id = annot.get_cat_id()
            
            pen.setColor(QColor(*color_list[cat_id]))
            p.setPen(pen)
            if annot.get_draw_type() == "rect":
                x1, y1, x2, y2 = annot.get_pos()
                p.drawRect(x1, y1, x2-x1, y2-y1)
            p.drawText(x1+4, y1+14, annot.get_cat())
                
        p.end()
        self.update()
        # super().setPixmap(pixmap)
    
    def set_annotation(self, annot):
        annot.to_draw_pos(self.x_offset, self.y_offset, self.x_ratio, self.y_ratio)
        self.drawing_annot = annot
        self.update()
    
    def reset_annotation(self):
        self.drawing_annot = Annotation()
    
    def setPixmap(self, pixmap):
        self._pixmap = pixmap.scaled(*self.size, Qt.KeepAspectRatio)
        
        self.x_offset = int(self.size[0]/2 - self._pixmap.width()/2)
        self.y_offset = int(self.size[1]/2 - self._pixmap.height()/2)
        
        self.x_ratio = pixmap.size().width() / self._pixmap.width()
        self.y_ratio = pixmap.size().height() / self._pixmap.height()
        
        self.reset_annotation()
        super().setPixmap(self._pixmap)
        
    def mousePressEvent(self, ev):
        self.is_mouse_pressed = True
        
        if ev.buttons() & Qt.LeftButton:
            if not self.drawing:
                if self.is_on_annot(ev.x(), ev.y()) != -1:
                    pass
                elif self.is_valid_point(ev.x(), ev.y()):
                    self.drawing_annot.set_pos([ev.x(), ev.y(), ev.x(), ev.y()])
                    self.drawing = True
                
        elif ev.buttons() & Qt.RightButton:
            if self.drawing:
                self.drawing = False
                self.drawing_annot.clear_pos()
            else:
                if not self.drawing_annot.is_valid():
                    self.get_clicked_pos.emit((ev.x()-self.x_offset)*self.x_ratio, (ev.y()-self.y_offset)*self.y_ratio)
                elif self.drawing_annot.is_valid():
                    self.drawing = False
                    self.drawing_annot.clear_pos()
        
        self.update()
    
    def mouseMoveEvent(self, ev):
        if self.is_valid_point(ev.x(), ev.y()):
            if self.is_mouse_pressed:
                if ev.buttons() & Qt.LeftButton:
                    if self.drawing:
                        pos = self.drawing_annot.get_pos()
                        pos[2:] = list(self.make_valid_point(ev.x(), ev.y()))
                        self.drawing_annot.set_pos(pos)
                    
                    elif self.modifing_index != -1:
                        pos = self.drawing_annot.get_pos()
                        x, y = list(self.make_valid_point(ev.x(), ev.y()))
                        pos[self.modifing_index] = x if self.modifing_index in [0, 2] else y
                        self.drawing_annot.set_pos(pos) 
            
            else:
                if self.is_on_annot(ev.x(), ev.y()) != -1:
                    if self.modifing_index in [0, 2]:
                        QApplication.setOverrideCursor(Qt.SizeHorCursor)
                    else:
                        QApplication.setOverrideCursor(Qt.SizeVerCursor)
                    self.modifing_index = -1
                else:
                    QApplication.setOverrideCursor(Qt.BlankCursor)
                    
            self.mouse_x = ev.x()
            self.mouse_y = ev.y()
        
        else:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mouse_x = -999
            self.mouse_y = -999
                 
        self.update()
    
    def mouseReleaseEvent(self, ev):
        self.is_mouse_pressed = False
        
        if ev.button() & Qt.LeftButton:
            if self.drawing:
                self.drawing_annot.sort_order()
                self.drawing = False
            elif self.modifing_index != -1:
                self.drawing_annot.sort_order()
                self.modifing_index = -1
            
            self.update()
    
    def keyPressEvent(self, ev):
        if ev.key() in [Qt.Key_Return, Qt.Key_Space]:
            if not self.drawing:
                self.drawing_annot.to_real_pos(self.x_offset, self.y_offset, self.x_ratio, self.y_ratio)
                print(type(self.drawing_annot))
                self.get_annotation.emit(self.drawing_annot)
                self.drawing_annot = Annotation()
    
    def leaveEvent(self, e):
        self.mouse_x = -999
        self.mouse_y = -999
        self.update()
        
        QApplication.setOverrideCursor(Qt.ArrowCursor)

if __name__ == "__main__":
    app = QApplication([])
    w = Canvas(None,
               size=(1280, 720),
                pixmap=QPixmap("./test.png")               )
    w.show()
    app.exec_()