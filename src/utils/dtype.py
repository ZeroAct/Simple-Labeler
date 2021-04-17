
class Annotation(object):
    def __init__(self, 
                 draw_type: str = "rect",
                 cat_id: int = 0,
                 cat: str = "default",
                 pos: list = []):
        
        self.draw_type = draw_type
        
        self.cat_id = cat_id
        self.cat = cat
        
        self.pos = pos
        
        self.valid = False
        
        self.get_draw_type = lambda: self.draw_type
        self.get_cat_id = lambda: self.cat_id
        self.get_cat = lambda: self.cat
        self.get_pos = lambda: self.pos
        self.is_valid = lambda: self.valid
        
    def set_pos(self, pos):
        self.pos   = pos
        self.valid = True
    
    def set_cat_id(self, cat_id):
        self.cat_id = cat_id
    
    def set_cat(self, cat):
        self.cat = cat
    
    def clear_pos(self):
        self.pos = []
        self.valid = False
        
    def sort_order(self):
        if self.draw_type == "rect":
            x1, y1, x2, y2 = self.pos
            
            if x1 > x2:
                x1, x2 = x2, x1
            if y1 > y2:
                y1, y2 = y2, y1
            
            self.set_pos([x1, y1, x2, y2])
    
    def to_real_pos(self, x_offset, y_offset, x_ratio, y_ratio):
        if self.draw_type == "rect":
            for i in range(len(self.pos) // 2):
                self.pos[2*i] -= x_offset
                self.pos[2*i] *= x_ratio
                self.pos[2*i+1] -= y_offset
                self.pos[2*i+1] *= y_ratio
    
    def to_draw_pos(self, x_offset, y_offset, x_ratio, y_ratio):
        if self.draw_type == "rect":
            for i in range(len(self.pos) // 2):
                self.pos[2*i] /= x_ratio
                self.pos[2*i] += x_offset
                self.pos[2*i+1] /= y_ratio
                self.pos[2*i+1] += y_offset
            # self.pos = list(map(int, self.pos))
    
    def has_point(self, x, y):
        x1, y1, x2, y2 = self.pos
        
        if x1 <= x < x2 and y1 <= y < y2:
            return True
        else:
            return False
    
    def __str__(self):
        return f"{self.cat},{','.join(map(str,self.pos))}"