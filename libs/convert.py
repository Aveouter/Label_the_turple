
from PyQt5.QtCore import QPointF
from libs.relationship import Relationship
from libs.shape import Shape
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QImageReader

from libs.utils import generate_color_by_text

def turple2shape(label, points, line_color, fill_color,difficult,x,y,_):
        # # 创建 Shape 对象
    shape = Shape(label=label, difficult=difficult, paint_label=False,shape_id=_)  # 根据需要设置 paint_label
    shape.line_color = line_color
    shape.fill_color = fill_color
    shape.fill = fill_color is not None  # 或根据 'fill' 标志设
    for x,y in points:
        shape.add_point(QPointF(x, y)) 
    shape.difficult = difficult
    shape.close()
    return shape

def read(filename, default=None):
    try:
        reader = QImageReader(filename)
        reader.setAutoTransform(True)
        return reader.read()
    except:
        return default


def convert_to_shape(annotations):
    shapes = []
    
    # 遍历每个标注对象
    for annotation in annotations:
        image_id = annotation["image_id"]
        objects = annotation["objects"]
        
        for obj in objects:
            # 获取 object 的属性
            object_id = obj["object_id"]
            # print(f"convert_to_shape:{object_id}")
            label = obj["names"][0]  # 取第一个标签名称
            # print(f"label:{label}")
            x, y = obj["x"], obj["y"]
            w, h = obj["w"], obj["h"]
            x1 = x
            y1 = y
            x2 = x + w
            y2 = y
            x3 = x + w
            y3 = y + h
            x4 = x
            y4 = y + h
            
            generate_color = generate_color_by_text(label)
            difficult  = False
            # 生成 shape 对象
            shape = (
                label,                          # 标签
                [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],  # 点的坐标
                generate_color,                 # 线条颜色
                generate_color,                 # 填充颜色
                difficult,                       # 难度标志
                object_id
            )
            ## 这里只是一个turple

            shapes.append(shape)
    return shapes

def convert_to_relationship(annotations, shapes):

    def point2position(points):
        x1, y1 = points[0].x(), points[0].y()
        x2, y2 = points[2].x(), points[2].y()       
        width = x2 - x1
        height = y2 - y1
        goal = [x1, y1, width, height]
        # 返回 (x, y, w, h)，即左上角坐标和宽高
        return goal  
    
    def find_shape_by_id(shapes, object_id,ano):
        # 遍历 shapes 列表，找到 object_id 匹配的元素
        for shape in shapes:
            goal_position = point2position(shape.points)
            # print(f"当前 shape_id: {shape.shape_id}, 目标 object_id: {object_id}")          
            # 检查 shape 的 object_id 和 goal_position 是否匹配
            if shape.shape_id == object_id and goal_position == ano:
                # print("匹配")
                return shape      
            # # 如果不匹配，记录不匹配的原因
            # if shape.shape_id != object_id:
            #     print(f"不匹配的原因: shape_id 不相等, 当前 shape_id: {shape.shape_id}, 目标 object_id: {object_id}")
            # if goal_position != ano:
            #     print(f"不匹配的原因: goal_position 不相等, 当前 goal_position: {goal_position}, 目标 ano: {ano}")
        return None  # 如果找不到匹配的 object_id，返回 None 
    
    relationships = []
    for rel in annotations[0]["relationships"]:
        sub_data = rel['subject']
        obj_data = rel['object']
        x,y,w,h = sub_data['x'] , sub_data['y'],sub_data['w'],sub_data['h']
        ano = [x,y,w,h]
        sub_shape = find_shape_by_id(shapes, sub_data["object_id"],ano)
        x,y,w,h = obj_data['x'] , obj_data['y'],obj_data['w'],obj_data['h']
        ano = [x,y,w,h]
        obj_shape = find_shape_by_id(shapes, obj_data["object_id"],ano)   
        if sub_shape is None or obj_shape is None                                                                                                                                                                                                                                                is None:
            print(f"Error: Could not find shapes for {sub_data['object_id']} or {obj_data['object_id']}")
            continue  # 跳过这个关系，或者你可以抛出异常
        relationship = Relationship(sub_shape, obj_shape,rel['relationship_id'],rel['predicate'])
        relationships.append(relationship)
    return relationships
