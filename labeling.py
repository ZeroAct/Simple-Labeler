from PyQt5.QtWidgets import \
    QApplication, QMainWindow, QLabel, QHBoxLayout, \
    QVBoxLayout, QWidget, QPushButton, QLineEdit, \
    QFileDialog
    
from PyQt5.QtGui import \
    QPainter, QPen, QBrush, QPixmap, QColor, QFont

from PyQt5.QtCore import Qt

import os, glob, natsort

from PIL import ImageColor

GetColor = lambda c: ImageColor.getcolor(c, "RGB")

class LabelWidget(QWidget):
    def __init__(self, parent, name, color):
        super().__init__()
        
        color_w = QLabel()
        color_w.setFixedSize(20, 20)
        color_w.setStyleSheet(f"background-color: {color}")
        
        l = QHBoxLayout()
        l.addWidget(QLabel(name))
        l.addWidget(color_w)
        
        self.setLayout(l)
        
        self.mousePressEvent = lambda e: parent.SetLabel(name)

class Canvas(QLabel):
    def __init__(self, parent, size):
        super().__init__()
        
        self.Parent = parent
        
        self.Pixmap = QPixmap(*size)
        self.Pixmap.scaledToWidth(1280)
        super().setPixmap(self.Pixmap)
        
        self.setAlignment(Qt.AlignCenter)
        
        self.size = size
        self.setFixedSize(*self.size)
        self.aspect_ratio = self.size[0] / self.size[1]
        self.ratio = 1
        self.x_offset = 0
        self.y_offset = 0
        
        self.is_drawing = False
        self.x1, self.y1 = 0, 0
        
        self.label_path = "blank.txt"
        
        self.labels = []
        
        self.clear_canvas()
        
        self.setMouseTracking(True)
    
    def clear_canvas(self):
        painter = QPainter(self.Pixmap)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRect(-1, -1, self.size[0], self.size[1])
        painter.end()
        
        self.setPixmap(self.Pixmap)
    
    def mousePressEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            if e.x() < self.x_offset or e.x() >= self.size[0] - self.x_offset \
                or e.y() < self.y_offset or e.y() >= self.size[1] - self.y_offset:
                return
            
            if not self.is_drawing:
                self.x1 = e.x()
                self.y1 = e.y()
                
                self.is_drawing = True
                self.labels.append([*self.HandleOffset(e.x(), e.y(), e.x(), e.y()), self.Parent.SelectedLabel])
                
                self.DrawLabels()
        
        if e.buttons() & Qt.RightButton:
            if len(self.labels) > 0:
                self.labels.pop()
                
                self.DrawLabels()
                self.SaveLabels()
    
    def mouseMoveEvent(self, e):
        if self.is_drawing:
            x1, y1, x2, y2 = self.x1, self.y1, e.x(), e.y()
            
            self.labels[-1] = [*self.HandleOffset(x1, y1, x2, y2), self.Parent.SelectedLabel]
            self.DrawLabels()
    
    def mouseReleaseEvent(self, e):
        if self.is_drawing:
            x1, y1, x2, y2 = self.x1, self.y1, e.x(), e.y()
            
            self.labels[-1] = [*self.HandleOffset(x1, y1, x2, y2), self.Parent.SelectedLabel]
            
            self.is_drawing = False
            
            self.DrawLabels()
            self.SaveLabels()
    
    def enterEvent(self, e):
        QApplication.setOverrideCursor(Qt.CrossCursor)
    
    def leaveEvent(self, e):
        QApplication.restoreOverrideCursor()
    
    def DrawLabels(self):
        pixmap = self.Pixmap.copy()
        painter = QPainter(pixmap)
        
        font = QFont("Gothic", 15)
        font.setBold(True)
        painter.setFont(font)
        
        for label in self.labels:
            x1, y1, x2, y2, label = label
            
            painter.setPen(QPen(QColor(*GetColor(self.Parent.LabelInfos[label]["color"])), 2))
            painter.drawRect(x1, y1, x2-x1, y2-y1)
            painter.drawText(x1+2, y1+17, label)
        
        painter.end()
        
        self.setPixmap(pixmap)
        self.repaint()
    
    def HandleOffset(self, x1, y1, x2, y2):
        if x1 > x2: 
            x2, x1 = x1, x2
        if y1 > y2:
            y2, y1 = y1, y2
                
        x1 -= self.x_offset; y1 -= self.y_offset; x2 -= self.x_offset; y2 -= self.y_offset
        
        if x1 < 0:
            x1 = 0
        elif x2 >= self.Pixmap.width():
            x2 = self.Pixmap.width() - 1
        
        if y1 < 0:
            y1 = 0
        elif y2 >= self.Pixmap.height():
            y2 = self.Pixmap.height() - 1
        
        return x1, y1, x2, y2
    
    def SetCanvas(self, pixmap, label_path):
        self.Pixmap = pixmap
        
        w = pixmap.width()
        h = pixmap.height()
        
        ratio = w/h
        if self.aspect_ratio < ratio: 
            self.Pixmap = self.Pixmap.scaledToWidth(self.size[0])
            self.ratio  = self.size[0] / w
        else:
            self.Pixmap = self.Pixmap.scaledToHeight(self.size[1])
            self.ratio  = self.size[1] / h
        
        self.x_offset = self.size[0]//2 - self.Pixmap.width()//2 
        self.y_offset = self.size[1]//2 - self.Pixmap.height()//2 
        
        
        self.labels = []
        self.label_path = label_path
        
        if os.path.exists(label_path):
            with open(label_path, "r") as f:
                labels = f.readlines()
            
            for label in labels:
                x1, y1, x2, y2, label = label.strip('\n').split(',')
                x1 = int(int(x1)*self.ratio); y1 = int(int(y1)*self.ratio)
                x2 = int(int(x2)*self.ratio); y2 = int(int(y2)*self.ratio)
                
                self.labels.append([x1, y1, x2, y2, label])
        
        
        self.setPixmap(self.Pixmap)
        self.DrawLabels()
        
    def SaveLabels(self):
        with open(self.label_path, "w") as f:
            for label in self.labels:
                x1, y1, x2, y2, label = label
                x1 /= self.ratio; y1 /= self.ratio; x2 /= self.ratio; y2 /= self.ratio; 
                f.write(f"{int(x1)},{int(y1)},{int(x2)},{int(y2)},{label}\n")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.init_variables()
        self.init_widgets()
        self.init_ui()
        
        self.show()
    
    def init_variables(self):
        self.Directory     = None
        
        self.ImagePathList = []
        self.ImageIdx      = 0
        
        self.LabelInfos = {"Dog": {"color": "#ff0000"},
                           "Cat": {"color": "#0000ff"}}
        self.SelectedLabel = "Dog"
    
    def init_widgets(self):
        self.Canvas = Canvas(self, (1280, 720))
        
        self.SelectedLabelWidget = QLabel(f"선택한 레이블 : {self.SelectedLabel}")
        self.LabelWidgetList = []
        for name, info in self.LabelInfos.items():
            self.LabelWidgetList.append(
                    LabelWidget(self, name, info["color"])
                )
        
        self.BrowseBtn = QPushButton("디렉터리 선택")
        self.BrowseBtn.clicked.connect(self.OpenDirectory)
        
        self.DirectoryEdit = QLineEdit()
        self.DirectoryEdit.setReadOnly(True)
        
        self.ImageEdit = QLineEdit()
        self.ImageEdit.setReadOnly(True)
        self.ImageEdit.setFixedWidth(300)
        
        self.BeforeBtn = QPushButton("◀")
        self.BeforeBtn.setFixedWidth(100)
        self.BeforeBtn.clicked.connect(lambda x: self.MoveIndex(-1))
        
        self.NextBtn = QPushButton("▶")
        self.NextBtn.setFixedWidth(100)
        self.NextBtn.clicked.connect(lambda x: self.MoveIndex(+1))
        
    def init_ui(self):
        
        self.setStyleSheet('''
                           font-family: 'Gothic';
                           font-size: 20px; 
                           background-color:#cccccc; 
                           font-weight: bold;''')
        
        main_widget = QWidget()
        
        main_layout = QVBoxLayout()
        
        top_layout = QHBoxLayout()
        
        top_layout.addWidget(self.Canvas)
        
        label_layout = QVBoxLayout()
        label_layout.addWidget(self.SelectedLabelWidget, alignment=Qt.AlignCenter)
        for w in self.LabelWidgetList:
            label_layout.addWidget(w)
        top_layout.addItem(label_layout)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.BrowseBtn)
        bottom_layout.addWidget(self.DirectoryEdit)
        bottom_layout.addWidget(self.ImageEdit)
        
        bottom_layout.addWidget(self.BeforeBtn)
        bottom_layout.addWidget(self.NextBtn)
        
        main_layout.addItem(top_layout)
        main_layout.addItem(bottom_layout)
        
        main_widget.setLayout(main_layout)
        
        self.setCentralWidget(main_widget)
        self.show()
    
    def LoadImage(self):
        image_path = self.ImagePathList[self.ImageIdx]
        label_path = os.path.splitext(image_path)[0] + ".txt"
        
        self.ImageEdit.setText(os.path.split(image_path)[-1])
        self.Canvas.SetCanvas(QPixmap(image_path), label_path)
    
    def OpenDirectory(self):
        directory = QFileDialog.getExistingDirectory(None, 'Select a folder:', './', QFileDialog.ShowDirsOnly)
        
        print(directory)
        if directory == "": return
        
        self.DirectoryEdit.setText(directory)
        self.Directory = directory
        self.ImageIdx = 0
        
        self.ImagePathList = []
        for ext in ["*.jpg", "*.png", "*.jpeg"]:
            self.ImagePathList += natsort.natsorted(glob.glob(os.path.join(self.Directory, ext)))
        
        self.LoadImage()
    
    def MoveIndex(self, d):
        self.ImageIdx = (self.ImageIdx + d) % len(self.ImagePathList)
        self.LoadImage()
    
    def SetLabel(self, name):
        self.SelectedLabel = name
        self.SelectedLabelWidget.setText(f"선택한 레이블 : {self.SelectedLabel}")
        
if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    app.exec_()



