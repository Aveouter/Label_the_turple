import json
import sys
import os
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QScrollArea
from PyQt5.QtGui import QImageReader
from PyQt5.QtCore import QPointF


import libs.labelFile
from libs.shape import Shape
from libs.combobox import ComboBox
from libs.ustr import ustr
from libs.utils import *
from libs.constants import *
from libs.convert import *
from libs.canvas import Canvas
from libs.labelDialog import LabelDialog
from libs.hashableQListWidgetItem import HashableQListWidgetItem
from libs.labelFile import LabelFile, LabelFileError
from libs.relationship import Relationship
from libs.convert import *

import argparse
import logging

__appname__ = 'application'

class MainWindow(QMainWindow):
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = list(range(3))

    def __init__(self, args ,parent=None):
        super(MainWindow, self).__init__(parent)  # 调用父类的构造函数以初始化子类
        self.logger = logging.getLogger(__name__) 

        screen_size = QDesktopWidget().screenGeometry()  # 获取屏幕尺寸
        self.setObjectName("MainWindow")  # 设置主窗口的对象名称
        self.setGeometry(0, 0, int(screen_size.width()*0.6), int(screen_size.height()*0.6)) # 设置主窗口的大小为全屏
        self.centralwidget = QtWidgets.QWidget()  # 创建中心部件
        self.centralwidget.setObjectName("centralwidget")  # 设置中心部件的对象名称
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)  # 在中心部件内创建一个垂直布局部件
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(2000, 0, 261, 1151))  # 设置垂直布局部件的几何形状
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")  # 设置垂直布局部件的对象名称
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)  # 为垂直布局部件创建一个垂直布局
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)  # 设置垂直布局的内容边距
        self.verticalLayout.setObjectName("verticalLayout")  # 设置垂直布局的对象名称
        self.objects_label = QtWidgets.QLabel(self.verticalLayoutWidget)  # 在垂直布局部件内创建一个标签，用于显示对象
        self.objects_label.setObjectName("objects_label")  # 设置对象标签的对象名称
        self.verticalLayout.addWidget(self.objects_label)  # 将对象标签添加到垂直布局中
        self.objs_list_widget = QtWidgets.QListWidget(self.verticalLayoutWidget)  # 在垂直布局部件内创建一个列表部件，用于显示对象列表
        self.objs_list_widget.setObjectName("objs_list_widget")  # 设置对象列表部件的对象名称
        self.verticalLayout.addWidget(self.objs_list_widget)  # 将对象列表添加到垂直布局中
        self.relations_label = QtWidgets.QLabel(self.verticalLayoutWidget)  # 在垂直布局部件内创建一个标签，用于显示关系
        self.relations_label.setObjectName("relations_label")  # 设置关系标签的对象名称
        self.verticalLayout.addWidget(self.relations_label)  # 将关系标签添加到垂直布局中
        self.rels_list_widget = QtWidgets.QListWidget(self.verticalLayoutWidget)  # 在垂直布局部件内创建一个列表部件，用于显示关系列表
        self.rels_list_widget.setObjectName("rels_list_widget")  # 设置关系列表部件的对象名称
        self.verticalLayout.addWidget(self.rels_list_widget)  # 将关系列表添加到垂直布局中
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)  # 在中心部件内创建一个网格布局部件
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 20, 281, 341))  # 设置网格布局部件的几何形状
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")  # 设置网格布局部件的对象名称
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)  # 为网格布局部件创建一个网格布局
        self.gridLayout.setContentsMargins(0, 0, 0, 0)  # 设置网格布局的内容边距
        self.gridLayout.setHorizontalSpacing(7)  # 设置网格布局的水平间距
        self.gridLayout.setObjectName("gridLayout")  # 设置网格布局的对象名称
        self.prev_button = QtWidgets.QPushButton(self.gridLayoutWidget)  # 在网格布局部件内创建一个按钮，用于上一步操作
        self.prev_button.setObjectName("prev_button")  # 设置上一步按钮的对象名称
        self.gridLayout.addWidget(self.prev_button, 1, 1, 1, 1)  # 将上一步按钮添加到网格布局中
        self.open_dir = QtWidgets.QPushButton(self.gridLayoutWidget)  # 在网格布局部件内创建一个按钮，用于打开目录
        self.open_dir.setObjectName("open_dir")  # 设置打开目录按钮的对象名称
        self.gridLayout.addWidget(self.open_dir, 0, 1, 1, 1)  # 将打开目录按钮添加到网格布局中
        self.next_button = QtWidgets.QPushButton(self.gridLayoutWidget)  # 在网格布局部件内创建一个按钮，用于下一步操作
        self.next_button.setObjectName("next_button")  # 设置下一步按钮的对象名称
        self.gridLayout.addWidget(self.next_button, 1, 2, 1, 1)  # 将下一步按钮添加到网格布局中
        self.open_anno_dir = QtWidgets.QPushButton(self.gridLayoutWidget)  # 在网格布局部件内创建一个按钮，用于打开注释目录
        self.open_anno_dir.setObjectName("open_anno_dir")  # 设置打开注释目录按钮的对象名称
        self.gridLayout.addWidget(self.open_anno_dir, 0, 2, 1, 1)  # 将打开注释目录按钮添加到网格布局中
        self.anno_res = QtWidgets.QPushButton(self.gridLayoutWidget)  # 在网格布局部件内创建一个按钮，用于注释结果
        self.anno_res.setObjectName("anno_res")  # 设置注释结果按钮的对象名称
        self.gridLayout.addWidget(self.anno_res, 2, 2, 1, 1)  # 将注释结果按钮添加到网格布局中
        self.anno_obj = QtWidgets.QPushButton(self.gridLayoutWidget)  # 在网格布局部件内创建一个按钮，用于注释对象
        self.anno_obj.setObjectName("anno_obj")  # 设置注释对象按钮的对象名称
        self.anno_attr = QtWidgets.QPushButton(self.gridLayoutWidget)  # 在网格布局部件内创建一个按钮，用于注释属性
        self.anno_res.setObjectName("anno_attr")  # 设置注释属性按钮的对象名称
        self.gridLayout.addWidget(self.anno_attr, 3, 1, 1, 1)  # 将注释属性按钮添加到网格布局中

        self.anno_obj.setEnabled(False)  # 禁用注释对象按钮
        self.anno_res.setEnabled(False)  # 禁用注释结果按钮
        self.anno_attr.setEnabled(False)  # 禁用注释属性按钮
        self.gridLayout.addWidget(self.anno_obj, 2, 1, 1, 1)  # 将注释对象按钮添加到网格布局中
        
        # self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)  # 注释掉的代码，用于创建一个图形视图组件
        # self.graphicsView.setGeometry(QtCore.QRect(295, 1, 1701, 1151))  # 设置图形视图组件的几何形状
        # self.graphicsView.setObjectName("graphicsView")  # 设置图形视图组件的对象名称
        self.save_button = QtWidgets.QPushButton(self.gridLayoutWidget)  # 在网格布局部件内创建一个按钮，用于保存操作
        self.save_button.setObjectName("save_button")  # 设置保存按钮的对象名称
        self.save_button.setEnabled(False)  # 禁用保存按钮
        self.gridLayout.addWidget(self.save_button, 4, 2, 1, 1)  # 将保存按钮添加到网格布局中
        self.del_button = QtWidgets.QPushButton(self.gridLayoutWidget)  # 在网格布局部件内创建一个按钮，用于删除操作
        self.del_button.setObjectName("del_button")  # 设置删除按钮的对象名称
        self.gridLayout.addWidget(self.del_button, 4, 1, 1, 1)  # 将删除按钮添加到网格布局中

        self.canvas = Canvas(parent=self)  # 创建一个自定义的画布组件
        self.scroll = QScrollArea(self.centralwidget)  # 创建一个滚动区域
        self.scroll.setWidget(self.canvas)  # 将画布组件设置为滚动区域的子部件
        self.scroll.setWidgetResizable(True)  # 设置滚动区域的子部件可调整大小
        self.scroll_bars = {  # 创建一个包含垂直和水平滚动条的字典
            Qt.Vertical: self.scroll.verticalScrollBar(),  # 获取垂直滚动条
            Qt.Horizontal: self.scroll.horizontalScrollBar()  # 获取水平滚动条
        }
        self.scroll.setGeometry(QtCore.QRect(300, 26, 1690, 1153))  # 设置滚动区域的几何形状
        self.canvas.set_drawing_shape_to_square(False)  # 设置画布的绘图形状为非正方形

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)  # 在中心部件内创建第二个垂直布局部件
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(0, 860, 291, 291))  # 设置第二个垂直布局部件的几何形状
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")  # 设置第二个垂直布局部件的对象名称
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)  # 为第二个垂直布局部件创建一个垂直布局
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)  # 设置第二个垂直布局的内容边距
        self.verticalLayout_2.setObjectName("verticalLayout_2")  # 设置第二个垂直布局的对象名称
        self.imgs_label = QtWidgets.QLabel(self.verticalLayoutWidget_2)  # 在第二个垂直布局部件内创建一个标签，用于显示图像
        self.imgs_label.setObjectName("imgs_label")  # 设置图像标签的对象名称
        self.verticalLayout_2.addWidget(self.imgs_label)  # 将图像标签添加到第二个  
        self.image_list_widget = QtWidgets.QListWidget(self.verticalLayoutWidget_2)  # 在第二个垂直布局部件内创建一个列表部件，用于显示图像列表
        self.image_list_widget.setObjectName("image_list_widget")  # 设置图像列表部件的对象名称
        self.verticalLayout_2.addWidget(self.image_list_widget)  # 将图像列表添加到第二个垂直布局中

        self.setCentralWidget(self.centralwidget)  # 将中心部件设置为主窗口的中心部件
        self.menubar = QtWidgets.QMenuBar()  # 创建一个菜单栏
        self.menubar.setGeometry(QtCore.QRect(0, 0, 2242, 26))  # 设置菜单栏的几何形状
        self.menubar.setObjectName("menubar")  # 设置菜单栏的对象名称
        self.menu = QtWidgets.QMenu(self.menubar)  # 在菜单栏中创建一个菜单
        self.menu.setObjectName("menu")  # 设置菜单的对象名称
        self.setMenuBar(self.menubar)  # 将菜单栏设置为主窗口的菜单栏
        self.statusBar = QtWidgets.QStatusBar()  # 创建一个状态栏
        self.statusBar.setObjectName("statusBar")  # 设置状态栏的对象名称
        self.setStatusBar(self.statusBar)  # 将状态栏设置为主窗口的状态栏
        self.action = QtWidgets.QAction(self)  # 创建一个动作
        self.action.setObjectName("action")  # 设置动作的对象名称
        self.action_2 = QtWidgets.QAction(self)  # 创建另一个动作
        self.action_2.setObjectName("action_2")  # 设置另一个动作的对象名称
        self.action_3 = QtWidgets.QAction(self)  # 创建另一个动作
        self.action_3.setObjectName("action_3")  # 设置另一个动作的对象名称
        self.menu.addAction(self.action)  # 将动作添加到菜单中
        self.menu.addAction(self.action_2)  # 将另一个动作添加到菜单中
        self.menu.addAction(self.action_3)  # 将另一个动作添加到菜单中
        self.menubar.addAction(self.menu.menuAction())  # 将菜单添加到菜单栏中
        self.label_coordinates = QLabel('')  # 创建一个用于显示坐标的标签

        self.os_path = os.getcwd()  # 获取当前工作目录的路径
        self.file_path = args.dir_name # 初始化文件路径变量
        self.last_open_dir = args.dir_name # 上次打开的目录
        self.default_save_dir = None  # 默认的保存目录
        self.m_img_list = []  # 初始化图像列表
        self.img_count = 0  # 初始化图像计数器
        self.cur_img_idx = None  # 当前图像索引
        self.image_data = None  # 初始化图像数据
        self.dir_name = args.dir_name  # 初始化目录名称
        self.last_anno_dir = args.last_anno_dir  # 上次打开的注释目录
        self.anno_save_dir = args.anno_save_dir # args.anno_save_dir # 注释保存目录
        self.img_meta_json_file = None # args.img_meta_json_file  # 图像元数据JSON文件路径
        self.objects_json_file = None # args.objects_json_file  # 对象JSON文件路径
        self.rela_json_file = None # args.rela_json_file  # 关系JSON文件路径
        self.image = None  # 初始化图像变量
        self.image_dict = None

        self.image_dict = None
        self._beginner = True  # 初学者模式标志
        self.dirty = False  # 标记是否有未保存的更改
        self.objects_labels_list = []  # 对象标签列表
        self.relations_labels_list = []  # 关系标签列表
        self.objects_labels_list, self.relations_labels_list = self.load_predefined_label()  # 加载预定义的标签
        self.prev_label_text = ''  # 上一个标签文本
        self.prev_predicate_text = ''  # 上一个谓词文本
        self.lastLabel = None  # 上一个标签
        self.lastPredicate = None  # 上一个谓词
        self.items_to_shapes = {}  # 项目到形状的映射
        self.item_to_relationship = {}  # 项目到关系的映射
        self.shapes_to_items = {}  # 形状到项目的映射
        self.relationship_to_item = {}  # 关系到项目的映射
        self.label_file = None  # 注释文件
        self.label_dialog = LabelDialog(parent=self, list_item=self.objects_labels_list)  # 创建对象标签对话框  ## MIM error
        self.predicate_dialog = LabelDialog(parent=self, list_item=self.relations_labels_list)  # 创建关系标签对话框
        self.retranslateUi()  # 重新翻译用户界面
        QtCore.QMetaObject.connectSlotsByName(self)  # 连接信号和槽
        self.init_widget()  # 初始化窗口部件

    def open_dir_dialog(self, dir_path=None, silent=False):
        """ 弹出文件夹选择对话框，或使用默认目录 """
        default_open_dir_path = dir_path if dir_path else '.'
        if self.last_open_dir and os.path.exists(self.last_open_dir):
            default_open_dir_path = self.last_open_dir
        else:
            default_open_dir_path = os.path.dirname(self.file_path) if self.file_path else '.'
        if silent != True:
            target_dir_path = ustr(QFileDialog.getExistingDirectory(self,
                                                                    '%s - Open Directory' % __appname__,
                                                                    default_open_dir_path,
                                                                    QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        else:
            target_dir_path = ustr(default_open_dir_path)
        self.last_open_dir = target_dir_path
        self.default_save_dir = target_dir_path
        self.import_dir_images(target_dir_path)
        ## save
        self.img_meta_json_file = os.path.join(self.default_save_dir, 'image_data.json') if self.img_meta_json_file is None else self.img_meta_json_file
        self.objects_json_file = os.path.join(self.default_save_dir, 'objects.json') if self.objects_json_file is None else self.objects_json_file

    def import_dir_images(self, dir_path):
        """ 导入目录中的图像，并加载元数据 """
        if not dir_path:
            logging.error("错误的目录路径")
            return "Error:错误的目录"
        
        self.last_open_dir = dir_path
        self.dir_name = dir_path
        self.file_path = None
        self.image_list_widget.clear()

        try:
            self.m_img_list = self.scan_all_images(dir_path)
            logging.info(f"找到 {len(self.m_img_list)} 张图像")
            if not self.m_img_list:
                logging.warning(f"目录 '{dir_path}' 中没有找到任何图像。")
                return
        except Exception as e:
            logging.error(f"扫描目录时出错: {e}")
            return "Error:扫描错误"

        self.img_count = len(self.m_img_list)
        logging.debug(f"图像数量: {self.img_count}")

        try:
            self.open_image()
        except Exception as e:
            logging.error(f"打开图像时出错: {e}")

        for imgPath in self.m_img_list:
            try:
                item = QListWidgetItem(imgPath)
                self.image_list_widget.addItem(item)
            except Exception as e:
                logging.error(f"添加图像 '{imgPath}' 出错: {e}")

        logging.info("图像导入完成")

    def scan_all_images(self, folder_path):
        """ 扫描所有支持的图像文件 """
        extensions = ['.%s' % fmt.data().decode("ascii").lower() for fmt in QImageReader.supportedImageFormats()]
        images = []

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relative_path = os.path.join(root, file)
                    path = ustr(os.path.abspath(relative_path))
                    images.append(path)
        natural_sort(images, key=lambda x: x.lower())
        return images

    def open_image(self, direction = 'next'):
        if self.default_save_dir is not None:
            if self.dirty is True:
                self.save_file()
                self.open_anno_dir_dialog(self.last_anno_dir,True)

        """ 根据方向加载图像，可以是 'next' 或 'prev' """
        if self.img_count <= 0:
            logging.warning("没有图像可供操作")
            return

        if self.file_path is None:
            if self.cur_img_idx == None:
                self.cur_img_idx = -1
            else:
                logging.warning("文件路径未设置")
                return

        if direction == 'prev' and self.cur_img_idx <= 0:
            logging.debug("已经是第一张图像，无法加载上一张")
            return

        if direction == 'next' and self.cur_img_idx + 1 >= self.img_count:
            logging.warning("已经是最后一张图像，无法继续向前")
            return

        if direction == 'prev':
            self.cur_img_idx -= 1
        elif direction == 'next':
            self.cur_img_idx += 1

        filename = self.m_img_list[self.cur_img_idx]
        # print(filename)
        if filename:
            logging.info(f"加载图像: {filename}")
            self.load_file(filename)
            if self.image_dict and os.path.basename(filename) in self.image_dict:
                image_id = self.image_dict[os.path.basename(filename)]
                image_annotations = [annotation for annotation in self.objects_data if annotation["image_id"] == image_id ]
                relationship_annotations = [annotation for annotation in self.relationships_data if annotation["image_id"] == image_id]
                # print(image_annotations)
                shapes = self.load_labels(image_annotations) ## 加载已保存的标签数据，并将其恢复到画布上
                # for shape in shapes:
                #     print(f"Shape ID: {shape.shape_id}")
                self.load_relationships(relationship_annotations,shapes)
        else:
            logging.error("图像文件名无效")
            
    def _save_file(self, annotation_file_path):
        if annotation_file_path and self.save_labels(annotation_file_path):
            self.set_clean()
            self.status('Saved to  %s' % annotation_file_path)
            self.statusBar.show()

    def save_file(self):
        if self.default_save_dir is not None and len(ustr(self.default_save_dir)):
            if self.file_path:
                if self.last_anno_dir :
                    self._save_file(self.last_anno_dir)
                elif self.anno_save_dir :
                    self._save_file(self.anno_save_dir)
                else:
                    exit()
                    image_file_name = os.path.basename(self.file_path)
                    saved_file_name = os.path.splitext(image_file_name)[0]
                    saved_path = os.path.join(ustr(self.default_save_dir), saved_file_name)
                    self._save_file(saved_path)

    # 12/19 - 23pm
    def save_labels(self, annotation_file_path):
        annotation_file_path = ustr(annotation_file_path)
        if self.label_file is None:
            self.label_file = LabelFile()

        def format_shape(s):
           return dict(label=s.label,
                  line_color=s.line_color.getRgb(),
                  fill_color=s.fill_color.getRgb(),
                  points=[(p.x(), p.y()) for p in s.points],
                  object_id=s.shape_id,
                  difficult=s.difficult)

        def format_relation(r):
            return dict(
                predicate=r.predicate,
                rel_id=r.rel_id,
                subject=format_shape(r.sub),
                object=format_shape(r.obj)
            )

        shapes = []
        for idx, shape in enumerate(self.canvas.shapes):
            if isinstance(shape , Shape):
                # shape.shape_unique_id = idx
                shapes.append(format_shape(shape))


        relationships = []
        for r in self.canvas.relationships:
            if isinstance(r, Relationship):
                relationships.append(format_relation(r))

        # print(self.img_meta_json_file)
        # print(self.objects_json_file)
        # print(self.rela_json_file)
        try:
            self.label_file.save_image_mate_format(self.img_meta_json_file, self.file_path, self.cur_img_idx)
            self.label_file.save_object_anno_format(self.objects_json_file, self.file_path, self.cur_img_idx, shapes)
            self.label_file.save_relationship_anno_format(self.rela_json_file, self.file_path, self.cur_img_idx,
                                                          relationships)
            print('Image:{0} -> Annotation:{1}'.format(self.file_path, annotation_file_path))
            return True
        except LabelFileError as e:
            self.show_message(ERROR, "Error saving label data")
            return False

    def load_file(self, file_path=None):  # 加载图像文件
        """加载图像文件并显示在界面上"""
        self.reset_state() 
        self.canvas.setEnabled(False)
        if file_path is None:
            return
        file_path = ustr(file_path)
        unicode_file_path = ustr(file_path)
        unicode_file_path = os.path.abspath(unicode_file_path)
        if unicode_file_path and self.image_list_widget.count() > 0:
            if unicode_file_path in self.m_img_list:
                index = self.m_img_list.index(unicode_file_path)
                file_widget_item = self.image_list_widget.item(index)
                file_widget_item.setSelected(True)
            else:
                self.image_list_widget.clear()
                self.m_img_list.clear()

        if unicode_file_path and os.path.exists(unicode_file_path):
            self.image_data = read(unicode_file_path, None)

        if isinstance(self.image_data, QImage):
            image = self.image_data
        else:
            image = QImage.fromData(self.image_data)

        if image.isNull():
            self.show_message(ERROR, u"<p>Make sure <i>%s</i> is a valid image file." % unicode_file_path)
            self.status("Error reading %s" % unicode_file_path)
            return False
        self.status("Loaded %s" % os.path.basename(unicode_file_path))
        self.image = image
        self.file_path = unicode_file_path
        # print(unicode_file_path)
        self.canvas.load_pixmap(QPixmap.fromImage(image))

        self.canvas.setEnabled(True)
        self.anno_obj.setEnabled(True)
        self.anno_res.setEnabled(True)

    def open_anno_dir_dialog(self, dir_path=None, silent=False):
        # 默认目录
        default_anno_dir = dir_path
        if self.last_anno_dir and os.path.exists(self.last_anno_dir):
            default_anno_dir = self.last_anno_dir
            # logging.info(f"使用上次选择的目录: {self.last_anno_dir}")
        else:
            logging.info("没有找到上次的目录，使用默认路径")
            default_anno_dir = None

        # 弹出目录选择对话框
        if silent != True:
            target_anno_dir = ustr(QFileDialog.getExistingDirectory(self,
                                                                    '%s - Open Directory' % __appname__,
                                                                    default_anno_dir,
                                                                    QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        else:
            target_anno_dir = ustr(default_anno_dir)

        # 如果选择了目录，更新相关变量
        if target_anno_dir:
            # logging.info(f"选择了注释目录: {target_anno_dir}")
            self.last_anno_dir = target_anno_dir
            self.anno_save_dir = target_anno_dir
            self.load_anno_file(target_anno_dir)
            
            # 更新文件路径
            self.img_meta_json_file = os.path.join(self.anno_save_dir, 'image_data.json')
            self.objects_json_file = os.path.join(self.anno_save_dir, 'objects.json')
            self.rela_json_file = os.path.join(self.anno_save_dir, 'relationships.json')
            self.attr_json_file = os.path.join(self.anno_save_dir, 'attributes.json')
            
            # logging.info(f"注释文件路径已更新: {self.img_meta_json_file}, {self.objects_json_file}, {self.rela_json_file}, {self.attr_json_file}")
        else:
            logging.warning("没有选择目录，无法加载注释文件")
            self.show_message(ERROR, "标注文件夹路径为空")

    def load_anno_file(self, anno_dir):
        """
        加载注释目录中的 JSON 文件。
        """
        # logging.info(f"加载注释文件从目录: {anno_dir}")

        # 确保目录有效
        if not os.path.isdir(anno_dir):
            logging.error(f"目录无效: {anno_dir}")
            return

        # 使用一个通用函数加载文件
        def load_json_file(file_path):
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    try:
                        return json.load(f)
                    except json.JSONDecodeError:
                        logging.error(f"JSON 文件解析失败: {file_path}")
                        return None
            else:
                logging.warning(f"未找到文件: {file_path}")
                return None

        # 加载各个 JSON 文件
        self.image_data = load_json_file(os.path.join(anno_dir, 'image_data.json'))
        if self.image_data:
            self.image_dict = {item["image_name"]: item["image_id"] for item in self.image_data}
        self.objects_data = load_json_file(os.path.join(anno_dir, 'objects.json'))
        self.relationships_data = load_json_file(os.path.join(anno_dir, 'relationships.json'))
        self.attributes_data = load_json_file(os.path.join(anno_dir, 'attributes.json'))

    def load_bounding_box_from_annotation_json(self, json_file):
        """
        从给定的 JSON 文件中加载边界框数据
        """
        if not json_file or not os.path.isfile(json_file):
            logging.error(f"文件路径无效: {json_file}")
            return None

        if not json_file.lower().endswith('.json'):
            logging.error(f"文件不是有效的 JSON 文件: {json_file}")
            return None

        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            bounding_boxes = []
            for image in data:
                image_id = image.get('image_id')
                if not image_id:
                    logging.warning(f"图像 ID 丢失，跳过此图像")
                    continue

                for obj in image.get('objects', []):
                    x, y, w, h = obj.get('x'), obj.get('y'), obj.get('w'), obj.get('h')
                    if None in [x, y, w, h]:
                        logging.warning(f"对象 {obj.get('object_id')} 的边界框数据不完整")
                        continue

                    # 转换为 [x_min, y_min, x_max, y_max] 格式
                    bounding_boxes.append((x, y, x + w, y + h))

            logging.info(f"成功加载 {len(bounding_boxes)} 个边界框")
            return bounding_boxes
        except Exception as e:
            logging.error(f"加载边界框数据时发生错误: {e}")
            return None

###############################################################################
    def new_shape(self):
        """创建新标签形状并更新画布和列表"""
        self.label_dialog = LabelDialog(parent=self, list_item=self.objects_labels_list)
        text = self.label_dialog.pop_up(text=self.prev_label_text)
        self.lastLabel = text

        if text:
            self._add_label_and_shape(text)
            if self.Editor():  # 切换到编辑模式
                self.canvas.set_editing(True)
        else:
            self.canvas.reset_all_lines()

        self.anno_obj.setEnabled(True)

    def new_relation(self, relationship):
        """创建新关系并更新画布和列表"""
        self.predicate_dialog = LabelDialog(parent=self, list_item=self.relations_labels_list)
        text = self.predicate_dialog.pop_up(text=self.prev_predicate_text)
        self.lastPredicate = text

        if text:
            self._add_predicate(relationship, text)
            if self.Editor():  # 切换到关联模式
                self.canvas.set_relating(True)
        else:
            self.canvas.prev_shape = None

    def _add_label_and_shape(self, text):
        """将标签添加到列表并绘制形状"""
        generate_color = generate_color_by_text(text)
        shape = self.canvas.set_last_label(text, generate_color, generate_color)
        self.add_label(shape)

        # 更新列表
        if text not in self.objects_labels_list:
            self.objects_labels_list.append(text)
        self.set_dirty()

    def _add_predicate(self, relationship, text):  ## 添加谓词
        """添加谓词到关系列表"""
        relationship.predicate = text
        self.add_predicate_item(relationship)

        # 更新列表
        if text not in self.relations_labels_list:
            self.relations_labels_list.append(text)
        self.set_dirty()

    def add_predicate_item(self, relationship):
        """将谓词项添加到列表视图"""
        predicate_label = relationship.show_rel()
        if predicate_label:
            item = HashableQListWidgetItem(predicate_label)
            item.setBackground(generate_color_by_text(relationship.predicate))
            self.item_to_relationship[item] = relationship
            self.relationship_to_item[relationship] = item
            self.rels_list_widget.addItem(item)

    def add_label(self, shape):
        """将标签形状添加到列表视图"""
        shape.paint_label = True
        item = HashableQListWidgetItem(shape.label)
        item.setCheckState(Qt.Checked)
        item.setBackground(generate_color_by_text(shape.label))
        self.items_to_shapes[item] = shape
        self.shapes_to_items[shape] = item
        self.objs_list_widget.addItem(item)

    def create_shape(self):
        assert self.Editor()
        self.canvas.set_relating(False)
        self.canvas.set_editing(False)
        self.anno_obj.setEnabled(False)
        self.anno_res.setEnabled(True)

    def create_relation(self):
        assert self.Editor()
        self.canvas.set_relating(True)
        self.anno_res.setEnabled(False)
        self.anno_obj.setEnabled(True)

####################################################################################################################################################
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.objects_label.setText(_translate("MainWindow", "objects"))
        self.relations_label.setText(_translate("MainWindow", "relations"))
        self.prev_button.setText(_translate("MainWindow", "上一张"))
        self.open_dir.setText(_translate("MainWindow", "打开文件夹"))
        self.next_button.setText(_translate("MainWindow", "下一张"))
        self.open_anno_dir.setText(_translate("MainWindow", "选择标注文件夹"))
        self.anno_res.setText(_translate("MainWindow", "标注关系"))
        self.anno_obj.setText(_translate("MainWindow", "标注对象"))
        self.anno_attr.setText(_translate("MainWindow", "标注属性"))
        self.imgs_label.setText(_translate("MainWindow", "图片"))
        self.menu.setTitle(_translate("MainWindow", "文件"))
        self.action.setText(_translate("MainWindow", "打开图片文件夹"))
        self.action_2.setText(_translate("MainWindow", "选择保存路径"))
        self.action_3.setText(_translate("MainWindow", "重置"))
        self.save_button.setText(_translate("MainWindow", "保存"))
        self.del_button.setText(_translate("MainWindow", "清除"))

    def init_widget(self):

        if self.last_anno_dir != None:
            self.open_anno_dir_dialog(self.last_anno_dir,True)
        if self.open_dir != None:
            self.open_dir_dialog(self.dir_name,True)
        self.open_dir.clicked.connect(self.open_dir_dialog)
        self.open_anno_dir.clicked.connect(self.open_anno_dir_dialog)
        self.next_button.clicked.connect(lambda: self.open_image('next'))
        self.prev_button.clicked.connect(lambda: self.open_image('prev'))
        self.anno_obj.clicked.connect(self.create_shape)
        self.canvas.newShape.connect(self.new_shape)
        self.anno_res.clicked.connect(self.create_relation)
        self.canvas.annotateRelation.connect(self.new_relation)

        self.action_3.triggered.connect(self.reset_state)
            # 连接删除按钮到删除关系的方法
        self.del_button.clicked.connect(self.delete_selected_relationships)

    def load_predefined_label(self):
        # 定义对象标签和关系标签文件路径
        objects_txt = os.path.join(self.os_path, OBJECTS_TXT)
        relations_txt = os.path.join(self.os_path, RELATIONS_TXT)

        # 处理对象标签文件
        if os.path.exists(objects_txt):
            # logging.info(f"对象标签文件 '{objects_txt}' 已找到，正在加载...")
            with open(objects_txt, 'r') as otxt:
                obj_txt_lines = otxt.readlines()
                obj_txt_lines = [line.strip() for line in obj_txt_lines]
            logging.info(f"对象标签文件加载完毕，共 {len(obj_txt_lines)} 个标签。")
        else:
            logging.warning(f"对象标签文件 '{objects_txt}' 未找到，正在创建并写入默认标签...")
            with open(objects_txt, 'w') as otxt:
                otxt.write("\n".join(self.objects_labels_list))
                obj_txt_lines = []
            logging.info(f"对象标签文件已创建并写入 {len(self.objects_labels_list)} 个默认标签。")

        # 处理关系标签文件
        if os.path.exists(relations_txt):
            # logging.info(f"关系标签文件 '{relations_txt}' 已找到，正在加载...")
            with open(relations_txt, 'r') as rtxt:
                rel_txt_lines = rtxt.readlines()
                rel_txt_lines = [line.strip() for line in rel_txt_lines]
            logging.info(f"关系标签文件加载完毕，共 {len(rel_txt_lines)} 个标签。")
        else:
            logging.warning(f"关系标签文件 '{relations_txt}' 未找到，正在创建并写入默认标签...")
            with open(relations_txt, 'w') as rtxt:
                rtxt.write("\n".join(self.relations_labels_list))
                rel_txt_lines = []
            logging.info(f"关系标签文件已创建并写入 {len(self.relations_labels_list)} 个默认标签。")

        return obj_txt_lines, rel_txt_lines

    def show_message(self, title, msg):
        reply = QMessageBox.information(None, title, msg, QMessageBox.Yes)

    def status(self, message, delay=5000):
        self.statusBar.showMessage(message, delay)

    def Editor(self):
        return self._beginner

    def set_dirty(self):
        # 设置“脏”标志为True
        self.dirty = True
        # 启用保存按钮
        self.save_button.setEnabled(True)
        # 记录设置脏标志后的状态
        logging.debug("Dirty state set to True. Save button enabled: %s", self.save_button.isEnabled())

    def set_clean(self):
        self.dirty = False
        self.save_button.setEnabled(False)
######################################################################################################################################################
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            print('ctrl press')
            self.canvas.set_drawing_shape_to_square(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            print('ctrl unpress')
            # Draw rectangle if Ctrl is pressed
            self.canvas.set_drawing_shape_to_square(True)
        elif event.key() == Qt.Key_Delete:
            self.delete_selected_relationships()  # **新增：监听 Delete 键进行删除关系**
        else:
            super(MainWindow, self).keyPressEvent(event)

    def delete_selected_relationships(self):
        """ 删除选中的关系 """
        selected_rels = self.rels_list_widget.selectedItems()

        if not selected_rels:
            self.status("未选择任何关系进行删除")
            return

        reply = QMessageBox.question(
            self,
            '确认删除',
            f"确定要删除选中的 {len(selected_rels)} 个关系吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.No:
            return

        # 删除关系列表中的选中项
        for item in selected_rels:
            relationship = self.item_to_relationship.get(item)
            if relationship:
                self.canvas.remove_relationship(relationship)  # 从画布上移除关系
                del self.item_to_relationship[item]  # 从映射中删除
                del self.relationship_to_item[relationship]
            row = self.rels_list_widget.row(item)
            self.rels_list_widget.takeItem(row)  # 从列表控件中移除

        # 标记为脏数据并启用保存按钮
        if selected_rels:
            self.set_dirty()
            self.status("选中的关系已删除")
        else:
            self.status("未选择任何关系进行删除")
            
########################################################################################################################################################
    def reset_state(self):  ## 重置标注工具的状态，将所有相关的状态数据清除，确保工具回到初始状态
        self.items_to_shapes.clear()
        self.shapes_to_items.clear()
        self.item_to_relationship.clear()
        self.relationship_to_item.clear()
        self.objs_list_widget.clear()
        self.rels_list_widget.clear()
        self.file_path = None
        self.image_data = None
        self.canvas.reset_state()
        self.label_coordinates.clear()

    def closeEvent(self, e):  ## 函数在应用程序关闭时被触发，用于保存当前的对象标签和关系标签到文本文件
        objects_txt = os.path.join(self.os_path, OBJECTS_TXT)
        relations_txt = os.path.join(self.os_path, RELATIONS_TXT)

        with open(objects_txt, 'w') as objtxt:
            for label in self.objects_labels_list:
                objtxt.write(str(label) + '\n')

        with open(relations_txt, 'w') as reltxt:
            for label in self.relations_labels_list:
                reltxt.write(str(label) + '\n')

    def paint_canvas(self):
        # 确保图片有效
        assert not self.image.isNull(), "无法绘制空图像"

        # 设置画布字体大小，基于图片大小的 2%（此处假设字体相对图片尺寸）
        self.canvas.label_font_size = int(0.02 * max(self.image.width(), self.image.height()))

        # 调整画布尺寸，确保适配图片
        self.canvas.adjustSize()

        # 刷新画布
        self.canvas.update()

    def load_labels(self, image_annotations):
        """
        加载已保存的标签数据，并将其恢复到画布上。
        :param shapes: 包含标签数据的列表，每个元素为形状元组
        """
        shapes = convert_to_shape(image_annotations)

        restored_shapes = []
        
        for shape_tuple in shapes:
            if len(shape_tuple) != 6:
                logging.debug("无效的形状数据：预期 6 个元素。")
                continue  # 如果形状数据不合法，则跳过当前元素
            
            label, points, line_color, fill_color, difficult, _ = shape_tuple
            
            # 修正点的坐标，确保其在画布内
            points = self._snap_points_to_canvas(points)

            # 创建形状对象
            shape = turple2shape(label, points, line_color, fill_color, difficult, points[0][0], points[0][1],_)
            restored_shapes.append(shape)

            # 添加标签
            self.add_label(shape)

        self.update_combo_box("label")
        self.canvas.load_shapes(restored_shapes)

        return restored_shapes

    def _snap_points_to_canvas(self, points):
        """
        确保所有点都在画布内，如果超出边界则修正坐标。
        :param points: 形状的点列表
        :return: 修正后的点列表
        """
        snapped_points = []
        for i, (x, y) in enumerate(points):
            x, y, snapped = self.canvas.snap_point_to_canvas(x, y)
            if snapped:
                self.set_dirty()  # 标记为脏数据
            snapped_points.append([x, y])
        return snapped_points

    def load_relationships(self, relationship_annotations,shapes):
        """
        加载现有的关系，并将其标签显示在列表中。
        :param relationships: 一个包含多个关系对象的列表
        """
        ## To class relationships
        relationships = convert_to_relationship(relationship_annotations, shapes)

        for relationship in relationships:
            # self.add_predicate(relationship)
            self.canvas.add_relationships(relationship)
            self.add_predicate_item(relationship)
        # self.canvas.load_relationship()
        self.update_combo_box("relationship")

    def update_combo_box(self, signal):
        """
        更新下拉框内容，显示唯一的标签或关系。
        :param signal: 信号类型，"label" 或 "relationship"
        """
        if signal == "label":
            widget = self.objs_list_widget
        elif signal == "relationship":
            widget = self.rels_list_widget
        else:
            logging.debug("错误的 signal 参数：只能是 'label' 或 'relationship'")
            return

        # 获取并去重所有条目的文本
        unique_text_list = sorted(set(str(widget.item(i).text()) for i in range(widget.count())))
        
        # 为了显示所有标签，添加一个空行
        unique_text_list.append("")

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    parser = argparse.ArgumentParser(description="Initialize variables with command-line arguments.")
    
    parser.add_argument('--file_path', type=str, help="文件路径")
    parser.add_argument('--last_open_dir', type=str, help="上次打开的目录")
    parser.add_argument('--default_save_dir', type=str, help="默认保存目录")
    parser.add_argument('--m_img_list', type=str, nargs='*', help="图像列表")
    parser.add_argument('--img_count', type=int, help="图像计数器")
    parser.add_argument('--cur_img_idx', type=int, help="当前图像索引")
    parser.add_argument('--image_data', type=str,  help="图像数据")
    parser.add_argument('--dir_name', type=str,default= "D:/CIGIT/SenceGraphGenerationInOpenSurgery/tool/visual-genome-annotator-main/data_sources/images", help="目录名称")
    parser.add_argument('--last_anno_dir', type=str, default= "D:/CIGIT/SenceGraphGenerationInOpenSurgery/tool/visual-genome-annotator-main/data_sources/rel", help="上次打开的注释目录")
    parser.add_argument('--anno_save_dir', type=str, default= "D:/CIGIT/SenceGraphGenerationInOpenSurgery/tool/visual-genome-annotator-main/data_sources/rel", help="注释保存目录")
    parser.add_argument('--img_meta_json_file', type=str, default = "D:/CIGIT/SenceGraphGenerationInOpenSurgery/tool/visual-genome-annotator-main/data_sources/rel\image_data.json",help="图像元数据JSON文件路径")
    parser.add_argument('--objects_json_file', type=str, default = "D:/CIGIT/SenceGraphGenerationInOpenSurgery/tool/visual-genome-annotator-main/data_sources/rel\objects.json",help="对象JSON文件路径")
    parser.add_argument('--rela_json_file', type=str, default="D:/CIGIT/SenceGraphGenerationInOpenSurgery/tool/visual-genome-annotator-main/data_sources/rel\relationships.json" ,help="关系JSON文件路径")
    args = parser.parse_args() # 解析命令行参数

    app = QApplication(sys.argv)
    win = MainWindow(args)
    win.show()
    sys.exit(app.exec_())