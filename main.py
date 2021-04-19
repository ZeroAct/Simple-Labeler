import os, sys, glob, natsort
from PyQt5.QtWidgets import \
    QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget, \
    QAction, QFileDialog, QSlider

from PyQt5.QtGui import \
    QPixmap, QPainter, QColor, QPen, QIcon
6
from PyQt5.QtCore import \
    Qt, QPoint, pyqtSignal

from src.widgets.help_widget import HelpWidget
from src.widgets.canvas import Canvas
from src.widgets.hint_slider import HintSlider
from src.widgets.category_list import CatListView, CatObject

from src.utils.color import color_list
from src.utils.dtype import Annotation
from src.utils.utils import load_stylesheet, get_image_name, save_annotations, load_annotations, load_cat_id

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.init_widgets()
        self.init_layout()
        self.init_variables()
    
    def init_widgets(self):
        self.setStyleSheet(load_stylesheet('css/global.css'))
        
        # menu
        self.menu = self.menuBar()
        self.menu.setStyleSheet(load_stylesheet('css/menu.css'))
        
        file_menu = self.menu.addMenu('&File')
        
        open_dir_act = QAction(QIcon(), '&Open Directory', self)
        open_dir_act.triggered.connect(self.open_dir)
        
        file_menu.addAction(open_dir_act)
        
        # status bar
        self.status_label = QLabel()
        self.status_label.setStyleSheet(load_stylesheet('css/status_label.css'))
        
        self.status_bar = self.statusBar()
        self.status_bar.addWidget(self.status_label)
        self.status_bar.setStyleSheet(load_stylesheet('css/status_bar.css'))
        self.set_status_bar("데이터 경로를 선택하세요.")
        
        # canvas
        self.canvas = Canvas(self, (1280, 720), QPixmap("src/default_pixmap.png"))
        self.canvas.get_annotation.connect(self.get_annotation)
        self.canvas.get_clicked_pos.connect(self.select_annotation)
        
        self.slider = HintSlider(Qt.Horizontal, self)
        self.slider.setStyleSheet(load_stylesheet('css/slider.css'))
        self.slider.update_canvas.connect(self.move_frame_idx)
        
        # category
        self.category_listw = CatListView(parent=self)
        self.category_listw.setStyleSheet(load_stylesheet('css/listview.css'))
        self.category_listw.get_selected_cat.connect(self.selected_cat_changed)
        
        # help
        self.help_widget = HelpWidget()
        self.help_widget.setStyleSheet(load_stylesheet('css/help_widget.css'))
    
    def init_layout(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.canvas)
        canvas_layout.addWidget(self.slider)
        
        cat_layout = QVBoxLayout()
        cat_layout.addWidget(self.category_listw)
        cat_layout.addWidget(self.help_widget)
        
        main_layout.addItem(canvas_layout)
        main_layout.addItem(cat_layout)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def init_variables(self):
        self.data_path         = ""
        self.frame_root_path   = ""
        self.frame_path_list   = []
        self.frame_idx         = 0
        
        self.label_root_path   = ""
        self.cat_id_path       = ""
        self.cat_id            = {}
        self.id_cat            = {}
        self.selected_cat_id   = 0
        
        self.annotations       = []
    
    def get_annotation(self, annot):
        # 현재 선택된 카테고리로 변경
        annot.set_cat_id(self.selected_cat_id)
        annot.set_cat(self.id_cat[self.selected_cat_id])
        
        # annotation 추가
        self.annotations.append(annot)
        
        # annotation 저장
        save_annotations(self.annotations, self.annotation_path)
        
        # 추가된 annotation 그리기
        self.canvas.draw_annotations([annot])
    
    def get_image_path(self, frame_idx):
        return self.frame_path_list[frame_idx] if len(self.frame_path_list) > 0 else None
    
    def select_annotation(self, x, y):
        for i, annot in list(enumerate(self.annotations))[::-1]:
            if annot.has_point(x, y):
                annot = self.annotations.pop(i)
                
                save_annotations(self.annotations, self.annotation_path)
                self.move_frame_idx(self.frame_idx)
                self.canvas.set_annotation(annot)
                break
    
    def open_dir(self):
        path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if path != "":
            self.data_path = path
            self.frame_root_path = os.path.join(self.data_path, "frames")
            self.frame_path_list = \
                glob.glob(os.path.join(self.frame_root_path, "*.png")) + \
                glob.glob(os.path.join(self.frame_root_path, "*.jpg"))
            
            if len(self.frame_path_list) == 0:
                self.set_status_bar(f"{path}/frames에 이미지가 없거나 올바르지 않은 경로입니다.")
                return
            
            self.frame_path_list = natsort.natsorted(self.frame_path_list)
            self.frame_idx = 0
            
            # 레이블링 결과 저장 경로
            self.label_root_path = os.path.join(self.data_path, "labels")
            if not os.path.isdir(self.label_root_path):
                os.mkdir(self.label_root_path)
            
            # 카테고리 정보
            self.cat_id_path  = os.path.join(self.data_path, "cat_id.txt")
            if not os.path.isfile(self.cat_id_path):
                with open(self.cat_id_path, "w") as f:
                    f.write("0,example")
            self.cat_id = load_cat_id(self.cat_id_path)
            self.id_cat = {v: k for k, v in self.cat_id.items()}
            
            # 카테고리 선택창 세팅
            self.category_listw.clear()
            for cat, id_ in self.cat_id.items():
                print(cat, id_)
                self.category_listw.addCatObject(CatObject(cat, color_list[id_]))
            
            # 프레임 이동 slider 세팅
            self.slider.setRange(0, len(self.frame_path_list)-1)
            self.move_frame_idx(0)
    
    def move_frame_idx(self, frame_idx=0, direction=None):
        if len(self.frame_path_list) == 0:
            return
        
        # a, s 프레임 앞뒤로 이동
        if direction is not None:
            self.frame_idx = (self.frame_idx + direction + len(self.frame_path_list)) % len(self.frame_path_list)
            self.slider.setValue(self.frame_idx)
        # slider로 프레임 이동
        else:
            self.frame_idx = frame_idx
        
        # canvas에 원본 이미지 그림
        self.canvas.setPixmap(QPixmap(self.frame_path_list[self.frame_idx]))
        
        # annotation 불러오기
        image_name = get_image_name(self.frame_path_list[self.frame_idx])
        
        self.annotation_path = os.path.join(self.label_root_path, image_name+".txt")
        self.annotations = load_annotations(self.annotation_path)
        for annotation in self.annotations:
            annotation.set_cat_id(self.cat_id[annotation.get_cat()])
        
        # annotation 그리기
        self.canvas.draw_annotations(self.annotations)
        
        # 상태바에 프레임 인덱스 출력
        self.set_status_bar(f"{self.frame_idx+1} / {len(self.frame_path_list)}")
    
    def selected_cat_changed(self, cat):
        self.selected_cat_id = self.cat_id[cat]
    
    def set_status_bar(self, string):
        self.status_label.setText(string)
    
    def keyPressEvent(self, ev):
        if ev.key() in [ord('a'), ord('A')]:
            self.move_frame_idx(direction=-1)
        elif ev.key() in [ord('s'), ord('S')]:
            self.move_frame_idx(direction=+1)
        else:
            self.canvas.keyPressEvent(ev)

if __name__ == "__main__":
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec_()


