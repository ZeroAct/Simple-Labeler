import os
from src.utils.dtype import Annotation

def load_stylesheet(path):
    with open(path,'r') as f:
        return f.read()
    
def get_image_name(path):
    return os.path.splitext(os.path.split(path)[-1])[0]

def save_annotations(annots, path):
    with open(path, 'w') as f:
        for annot in annots:
            f.write(str(annot)+"\n")

def load_annotations(path):
    annotations = []
    
    if os.path.isfile(path):
        with open(path, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            cat, x1, y1, x2, y2 = line.rstrip().split(',')
            
            annotation = Annotation()
            annotation.set_pos(list(map(float, [x1, y1, x2, y2])))
            annotation.set_cat(cat)
            
            annotations.append(annotation)
        
    return annotations

def load_cat_id(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    
    cat_id = {}
    for line in lines:
        _id, cat = line.rstrip().split(',')
        cat_id[cat] = int(_id)
        
    return cat_id
    