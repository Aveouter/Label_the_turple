import os
import json
from pathlib import Path
from libs.constants import *

ENCODE_METHOD = DEFAULT_ENCODING


class ImgDataWriter():
    def __init__(self ,output_file ,image_path, image_id, image_name , width , height):
        self.image_path = image_path
        self.image_id = image_id
        self.image_name = image_name
        self.width = width
        self.height = height
        self.output_json_file = output_file

    def write(self):
        if os.path.isfile(self.output_json_file):
            with open(self.output_json_file  , 'r') as file:
                input_data = file.read()
                output_dict = json.loads(input_data)

        else:
            output_dict = []

        output_image_dict={
            "image_id" : self.image_id,
            "url" : "",
            "image_name" : self.image_name,
            "width" : self.width,
            "height" : self.height,
            "coco_id" : None,
            "flickr_id" : None
        }

        exists = False
        for i in range(0 , len(output_dict)):
            if output_dict[i]['image_id'] == output_image_dict["image_id"]:
                exists = True
                output_dict[i] = output_image_dict
                break
        if not exists:
            output_dict.append(output_image_dict)
        Path(self.output_json_file).write_text(json.dumps(output_dict) , ENCODE_METHOD)

class ObjAnnoWriter():
    def __init__(self, output_file , filename ,image_id , shapes):
        self.image_id = image_id
        self.shapes = shapes
        self.output_json_file = output_file
        self.filename = filename

    def write(self):
        if os.path.isfile(self.output_json_file):
            with open(self.output_json_file, "r") as file:
                input_data = file.read()
                output_dict = json.loads(input_data)
        else:
            output_dict = []

        output_object_dict = {
            "image_id": self.image_id,
            "image_url": '',
            "objects": []
        }
        objects_list = []

        for shape in self.shapes:

            points = shape["points"]
            x1 = points[0][0]
            y1 = points[0][1]
            x2 = points[1][0]
            y2 = points[2][1]

            object_id = shape["object_id"]
            names = [shape["label"]]

            height, width, x, y = self.calculate_coordinates(x1, x2, y1, y2)

            shape_anno_dict = {
                "names" : names,
                "synsets": [],
                "object_id" : object_id,
                "merged_object_ids":[],
                "w" : width,
                "h" : height,
                "x" : x,
                "y" : y
            }
            objects_list.append(shape_anno_dict)

        output_object_dict['objects'] = objects_list
        exists = False
        for i  in range(0 , len(output_dict)):
            if output_dict[i]['image_id'] == output_object_dict['image_id']:
                exists = True
                output_dict[i] = output_object_dict
                break
        if not exists:
            output_dict.append(output_object_dict)

        Path(self.output_json_file).write_text(json.dumps(output_dict) , ENCODE_METHOD)


    def calculate_coordinates(self, x1, x2, y1, y2):
        if x1 < x2:
            x_min = x1
            x_max = x2
        else:
            x_min = x2
            x_max = x1
        if y1 < y2:
            y_min = y1
            y_max = y2
        else:
            y_min = y2
            y_max = y1
        width = x_max - x_min
        if width < 0:
            width = width * -1
        height = y_max - y_min
        # x and y from center of rect
        x = x_min
        y = y_min
        return height, width, x, y

class RelAnnoWriter():

    def __init__(self , output_file , filename ,  image_id , relationships):
        self.image_id = image_id
        self.relationships = relationships
        self.output_json_file = output_file
        self.filename = filename

    def writer(self):
        if os.path.isfile(self.output_json_file):
            with open(self.output_json_file, "r") as file:
                input_data = file.read()
                output_dict = json.loads(input_data)
        else:
            output_dict = []

        output_relation_dict = {
            "image_id": self.image_id,
            "relationships": []
        }

        relationship_list = []
        for relationship in self.relationships:
            predicate = relationship['predicate']
            sub = relationship['subject']
            obj = relationship['object']
            rel_id = relationship['rel_id']

            subject = self.get_obj_dict(sub)
            object = self.get_obj_dict(obj)

            relationship_anno_dict ={
                "relationship_id" : rel_id,
                "predicate" : predicate,
                "subject" : subject,
                "object" : object
            }
            relationship_list.append(relationship_anno_dict)

        output_relation_dict['relationships'] = relationship_list
        exists = False
        for i  in range(0 , len(output_dict)):
            if output_dict[i]['image_id'] == output_relation_dict['image_id']:
                exists = True
                output_dict[i] = output_relation_dict
                break
        if not exists:
            output_dict.append(output_relation_dict)

        Path(self.output_json_file).write_text(json.dumps(output_dict) , ENCODE_METHOD)

    def get_obj_dict(self, obj ):

        points = obj['points']
        x1 = points[0][0]
        y1 = points[0][1]
        x2 = points[1][0]
        y2 = points[2][1]

        object_id = obj['object_id']
        name = obj['label']

        height, width, x, y = self.calculate_coordinates(x1, x2, y1, y2)

        obj_dict = {
            "object_id": object_id,
            "x": x,
            "y": y,
            "w": width,
            "h": height,
            "name": name,
            "synsets": []
        }
        return obj_dict

    def calculate_coordinates(self, x1, x2, y1, y2):
        if x1 < x2:
            x_min = x1
            x_max = x2
        else:
            x_min = x2
            x_max = x1
        if y1 < y2:
            y_min = y1
            y_max = y2
        else:
            y_min = y2
            y_max = y1
        width = x_max - x_min
        if width < 0:
            width = width * -1
        height = y_max - y_min
        # x and y from center of rect
        x = x_min
        y = y_min
        return height, width, x, y

class AnnoReader():
    def __init__(self, json_path , ):
        self.json_path = json_path
        self.objects = []
        self.relations = []

        try:
            self.parse_json()
        except ValueError:
            print("JSON decoding failed")

    def parse_json(self):
        with open(self.json_path, "r") as file:
            input_data = file.read()

        output_list = json.loads(input_data)

        if len(self.objects) > 0:
            self.shapes = []
        for image in output_list:
            for object in image['objects']:
                self.add_objects(object)


    def add_objects(self, object):
        label = object['name']
        object_id = object['object_id']
        x = object['x']
        y = object['y']
        w = object['w']
        h = object['h']
        x_min = x
        y_min = y
        x_max = x + w
        y_max = y + h
        rect = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        self.objects.append((object_id, label, rect))

    def get_objects(self):
        return self.objects

    def add_relations(self, relationship):
        relationship_id = relationship['relationship_id']
        predicate = relationship['predicate']
        subject = relationship['subject']
        object = relationship['object']
        self.relations.append((relationship_id , predicate , subject , object))

    def get_relations(self):
        return self.relations


if __name__ == '__main__':
    annoReader = AnnoReader(r"D:\project\pythonProject\annotatorv1\test\img_annotation.json",r"D:\project\pythonProject\annotatorv1\test\img_annotation.json")
    objects = annoReader.get_objects()
    relations = annoReader.get_relations()
    print(objects)
    print(relations)
