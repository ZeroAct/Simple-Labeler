import sys
from PyQt5.QtGui import QPixmap, QColor, QIcon, QStandardItemModel
from PyQt5.QtWidgets import\
    QApplication, QWidget, QListWidget, QLabel, QHBoxLayout, QListWidgetItem, \
    QListWidgetItem, QListView, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QModelIndex
from collections import OrderedDict

class CatObject(QWidget):
    get_cat_signal = pyqtSignal(str)
    def __init__(self, cat, color, parent=None):
        
        super().__init__(parent=parent)
        
        self.color_pixmap = QPixmap(30, 30)
        self.color_pixmap.fill(QColor(*color))
        self.cat = cat
        
        self.color_label = QLabel()
        self.color_label.setPixmap(self.color_pixmap)
        self.cat_label = QLabel(cat)
        
        self.selected = False
        self.selected_label = QLabel("▶")
        self.selected_label.hide()
        
        l = QHBoxLayout()
        l.addWidget(self.selected_label, alignment=Qt.AlignLeft)
        l.addWidget(self.color_label, alignment=Qt.AlignLeft)
        l.addStretch(1)
        l.addWidget(self.cat_label, alignment=Qt.AlignLeft)
        l.addStretch(1)
        
        self.setLayout(l)
        self.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        
    def mousePressEvent(self, ev):
        if ev.buttons() & Qt.LeftButton:
            self.get_cat_signal.emit(self.cat)
    
    def select(self):
        if not self.selected:
            self.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: #14274e;")
            self.selected_label.show()
        else:
            self.selected_label.hide()
            self.setStyleSheet("color: white; font-size: 20px; font-weight: bold; background: #36496e;")
        
        self.selected = not self.selected
        
    def keyPressEvent(self, ev):
        print(3)
        
class CatListView(QListWidget):
    get_selected_cat = pyqtSignal(str)
    
    def __init__(self, items:list = [], parent=None):
        super(CatListView,self).__init__(parent)
        
        self.items = OrderedDict()
        self.selected_cat = ""
        
            
    def get_cat_signal(self, cat):
        if self.selected_cat != "":
            self.items[self.selected_cat][1].select()
        
        self.selected_cat = cat
        self.setCurrentIndex(self.items[self.selected_cat][0])
        self.items[self.selected_cat][1].select()
        
        self.get_selected_cat.emit(self.selected_cat)
    
    def addCatObject(self, catobj):
        assert "CatObject" in str(type(catobj))
        
        item = QListWidgetItem(self)
        self.addItem(item)
        
        row = catobj
        item.setSizeHint(row.minimumSizeHint())
        
        self.setItemWidget(item, row)
        
        catobj.get_cat_signal.connect(self.get_cat_signal)
        
        index = self.model().index(len(self.items), 0)
        self.items[catobj.cat] = [index, catobj]

    def keyPressEvent(self, ev):
        if self.parent is not None:
            self.parent().keyPressEvent(ev)
        else:
            super().keyPressEvent(ev)
        
if __name__ == '__main__':
    app=QApplication(sys.argv)
    m=CatListView()
    
    for item in [CatObject("1", (243, 223, 113)), CatObject("2", (205, 119, 213)),CatObject("3", (243, 223, 113)), CatObject("4", (205, 119, 213)),CatObject("5", (243, 223, 113)), CatObject("6", (205, 119, 213)),CatObject("7", (243, 223, 113)), CatObject("8", (205, 119, 213)),CatObject("9", (243, 223, 113))]:
        m.addCatObject(item)
    
    m.show()
    # w = CatObject("1", (22,22,22))
    # w.setStyleSheet("background-color: red")
    # w.show()
    sys.exit(app.exec_())