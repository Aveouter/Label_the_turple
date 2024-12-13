# Copyright (c) 2016 Tzutalin
# Create by TzuTaLin <tzu.ta.lin@gmail.com>

try:
    from PyQt5.QtGui import QImage
except ImportError:
    from PyQt4.QtGui import QImage

import os.path
from enum import Enum

# from libs.create_ml_io import CreateMLWriter
# from libs.pascal_voc_io import PascalVocWriter
# from libs.pascal_voc_io import XML_EXT
# from libs.yolo_io import YOLOWriter
from libs.anno_io import ObjAnnoWriter , ImgDataWriter , RelAnnoWriter

XML_EXT = '.json'

class LabelFileFormat(Enum):
    PASCAL_VOC = 1
    YOLO = 2
    CREATE_ML = 3

class LabelFileError(Exception):
    pass

class LabelFile(object):
    # It might be changed as window creates. By default, using XML ext
    # suffix = '.lif'
    suffix = XML_EXT

    def __init__(self, filename=None):
        self.shapes = ()
        self.image_path = None
        self.image_data = None
        self.verified = False

    def save_object_anno_format(self, output_file,  filename, image_id, shapes):
        img_file_name =  os.path.basename(filename)

        image = QImage()
        image.load(self.image_data)
        writer = ObjAnnoWriter(output_file ,filename, image_id ,shapes)
        writer.write()

    def save_image_mate_format(self, out_json_file,  image_path, image_id ):
        img_folder_name = os.path.basename(os.path.dirname(image_path))
        img_file_name = os.path.basename(image_path)

        image = QImage()
        image.load(image_path)
        width = image.width()
        height = image.height()

        writer = ImgDataWriter(out_json_file ,  image_path , image_id , img_file_name,  width , height)
        writer.write()

    def save_relationship_anno_format(self , out_json_file , filename , image_id , relationships ):
        img_file_name = os.path.basename(filename)
        writer = RelAnnoWriter(out_json_file , filename , image_id , relationships)
        writer.writer()

    def toggle_verify(self):
        self.verified = not self.verified

    ''' ttf is disable
    def load(self, filename):
        import json
        with open(filename, 'rb') as f:
                data = json.load(f)
                imagePath = data['imagePath']
                imageData = b64decode(data['imageData'])
                lineColor = data['lineColor']
                fillColor = data['fillColor']
                shapes = ((s['label'], s['points'], s['line_color'], s['fill_color'])\
                        for s in data['shapes'])
                # Only replace data after everything is loaded.
                self.shapes = shapes
                self.imagePath = imagePath
                self.imageData = imageData
                self.lineColor = lineColor
                self.fillColor = fillColor

    def save(self, filename, shapes, imagePath, imageData, lineColor=None, fillColor=None):
        import json
        with open(filename, 'wb') as f:
                json.dump(dict(
                    shapes=shapes,
                    lineColor=lineColor, fillColor=fillColor,
                    imagePath=imagePath,
                    imageData=b64encode(imageData)),
                    f, ensure_ascii=True, indent=2)
    '''

    @staticmethod
    def is_label_file(filename):
        file_suffix = os.path.splitext(filename)[1].lower()
        return file_suffix == LabelFile.suffix

    @staticmethod
    def convert_points_to_bnd_box(points):
        x_min = float('inf')
        y_min = float('inf')
        x_max = float('-inf')
        y_max = float('-inf')
        for p in points:
            x = p[0]
            y = p[1]
            x_min = min(x, x_min)
            y_min = min(y, y_min)
            x_max = max(x, x_max)
            y_max = max(y, y_max)

        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        if x_min < 1:
            x_min = 1

        if y_min < 1:
            y_min = 1

        return int(x_min), int(y_min), int(x_max), int(y_max)
