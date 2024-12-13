import sys

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.QtGui

from libs.shape import Shape
from libs.utils import distance

CURSOR_DEFAULT = Qt.ArrowCursor
CURSOR_POINT = Qt.PointingHandCursor
CURSOR_DRAW = Qt.CrossCursor
CURSOR_MOVE = Qt.ClosedHandCursor
CURSOR_GRAB = Qt.OpenHandCursor

class Canvas(QWidget):

    zoomRequest = pyqtSignal(int)
    lightRequest = pyqtSignal(int)
    scrollRequest = pyqtSignal(int, int)
    newShape = pyqtSignal()
    selectionChanged = pyqtSignal(bool)
    shapeMoved = pyqtSignal()
    drawingPolygon = pyqtSignal(bool)

    CREATE, EDIT = list(range(2))

    epsilon = 24.0

    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.hide_background = None
        self.h_vertex = None
        self.selected_shape = None
        self.verified = None
        self.selected_shape_copy = None
        self.h_shape = None
        self.visible = None
        self._hide_background = None
        self.label_font_size = None
        self.shapes = []
        self.scale = 1.0

        self.prev_point = QPointF()
        self.pixmap = QPixmap()  # 展示图像
        self._painter = QPainter()  # 绘图
        self.mode = self.CREATE
        self.current_color = QColor()
        self.current = None
        self.drawing_line_color = QColor(0, 0, 255)
        self.drawing_rect_color = QColor(0, 0, 255)
        self.line = Shape(line_color=self.drawing_line_color)
        self.draw_square = False
        self._cursor = CURSOR_DEFAULT
        self.overlay_color = None

        self.menus = (QMenu(), QMenu())


    def enterEvent(self, ev):
        self.override_cursor(self._cursor)

    def leaveEvent(self, ev):
        self.restore_cursor()

    def focusOutEvent(self, ev):
        self.restore_cursor()

    #用于检查给定的形状（shape）是否可见。
    def isVisible(self, shape):
        return self.visible.get(shape, True)

    def drawing(self):
        return self.mode == self.CREATE

    #编辑模式
    def editing(self):
        return self.mode == self.EDIT

    def set_editing(self, value=True):
        self.mode = self.EDIT if value else self.CREATE
        if not value:  # Create
            self.un_highlight()
            self.de_select_shape()
        self.prev_point = QPointF()
        self.repaint()

    def un_highlight(self, shape=None):
        if shape == None or shape == self.h_shape:
            if self.h_shape:
                self.h_shape.highlight_clear()
            self.h_vertex = self.h_shape = None

    def set_drawing_color(self, qcolor):
        self.drawing_rect_color = qcolor
        self.drawing_rect_color = qcolor

    def load_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.bboxes = []
        self.repaint()

    def selected_vertex(self):
        return self.h_vertex is not None

    def select_shape_point(self, point):
        """Select the first shape created which contains this point."""
        self.de_select_shape()
        if self.selected_vertex():  # A vertex is marked for selection.
            index, shape = self.h_vertex, self.h_shape
            shape.highlight_vertex(index, shape.MOVE_VERTEX)
            self.select_shape(shape)
            return self.h_vertex
        for shape in reversed(self.shapes):
            if self.isVisible(shape) and shape.contains_point(point):
                self.select_shape(shape)
                self.calculate_offsets(shape, point)
                return self.selected_shape
        return None


    def calculate_offsets(self, shape, point):
        rect = shape.bounding_rect()
        x1 = rect.x() - point.x()
        y1 = rect.y() - point.y()
        x2 = (rect.x() + rect.width()) - point.x()
        y2 = (rect.y() + rect.height()) - point.y()
        self.offsets = QPointF(x1, y1), QPointF(x2, y2)

    def set_hiding(self, enable=True):
        self._hide_background = self.hide_background if enable else False

    def select_shape(self, shape):
        self.de_select_shape()
        shape.selected = True
        self.selected_shape = shape
        self.set_hiding()
        self.selectionChanged.emit(True)
        self.update()

    def de_select_shape(self):
        if self.selected_shape:
            self.selected_shape.selected = False
            self.selected_shape = None
            self.set_hiding(False)
            self.selectionChanged.emit(False)
            self.update()
            
    def mousePressEvent(self , ev):
        print("mouse Press Evnet")
        pos = self.transform_pos(ev.pos())

        if ev.button() == Qt.LeftButton:
            if self.drawing():
                self.handle_drawing(pos)
            else:
                selection = self.select_shape_point(pos)
                self.prev_point = pos

                if selection is None:
                    # pan
                    QApplication.setOverrideCursor(QCursor(Qt.OpenHandCursor))
                    self.pan_initial_pos = ev.pos()

        elif ev.button() == Qt.RightButton and self.editing():
            self.select_shape_point(pos)
            self.prev_point = pos
        self.update()

    def mouseMoveEvent(self , e):
        pos = self.transform_pos(e.pos())

        if self.drawing():
            self.override_cursor(CURSOR_DRAW)
            if self.current:
                # Display annotation width and height while drawing
                current_width = abs(self.current[0].x() - pos.x())
                current_height = abs(self.current[0].y() - pos.y())
                # self.parent().window().label_coordinates.setText(
                #     'Width: %d, Height: %d / X: %d; Y: %d' % (current_width, current_height, pos.x(), pos.y()))

                color = self.drawing_line_color
                if self.out_of_pixmap(pos):
                    # Don't allow the user to draw outside the pixmap.
                    # Clip the coordinates to 0 or max,
                    # if they are outside the range [0, max]
                    size = self.pixmap.size()
                    clipped_x = min(max(0, pos.x()), size.width())
                    clipped_y = min(max(0, pos.y()), size.height())
                    pos = QPointF(clipped_x, clipped_y)
                elif len(self.current) > 1 and self.close_enough(pos, self.current[0]):
                    # Attract line to starting point and colorise to alert the
                    # user:
                    pos = self.current[0]
                    color = self.current.line_color
                    self.override_cursor(CURSOR_POINT)
                    self.current.highlight_vertex(0, Shape.NEAR_VERTEX)

                if self.draw_square:
                    init_pos = self.current[0]
                    min_x = init_pos.x()
                    min_y = init_pos.y()
                    min_size = min(abs(pos.x() - min_x), abs(pos.y() - min_y))
                    direction_x = -1 if pos.x() - min_x < 0 else 1
                    direction_y = -1 if pos.y() - min_y < 0 else 1
                    self.line[1] = QPointF(min_x + direction_x * min_size, min_y + direction_y * min_size)
                else:
                    self.line[1] = pos

                self.line.line_color = color
                self.prev_point = QPointF()
                self.current.highlight_clear()
            else:
                self.prev_point = pos
            self.repaint()
            return


    def mouseReleaseEvent(self , ev):
        if ev.button() == Qt.RightButton:
            menu = self.menus[bool(self.selected_shape_copy)]
            self.restore_cursor()
            if not menu.exec_(self.mapToGlobal(ev.pos()))\
               and self.selected_shape_copy:
                # Cancel the move by deleting the shadow copy.
                self.selected_shape_copy = None
                self.repaint()
        elif ev.button() == Qt.LeftButton and self.selected_shape:
            if self.selected_vertex():
                self.override_cursor(CURSOR_POINT)
            else:
                self.override_cursor(CURSOR_GRAB)
        elif ev.button() == Qt.LeftButton:
            pos = self.transform_pos(ev.pos())
            if self.drawing():
                self.handle_drawing(pos)
            else:
                # pan
                QApplication.restoreOverrideCursor() #PyQt 中的一个方法，用于恢复先前被覆盖的鼠标光标

    def handle_drawing(self, pos):
        if self.current and self.current.reach_max_points() is False:
            init_pos = self.current[0]
            min_x = init_pos.x()
            min_y = init_pos.y()
            target_pos = self.line[1]
            max_x = target_pos.x()
            max_y = target_pos.y()
            self.current.add_point(QPointF(max_x, min_y))
            self.current.add_point(target_pos)
            self.current.add_point(QPointF(min_x, max_y))
            self.finalise()
        elif not self.out_of_pixmap(pos):
            self.current = Shape()
            self.current.add_point(pos)
            self.line.points = [pos, pos]
            self.drawingPolygon.emit(True)
            self.update()


    def finalise(self):
        assert self.current
        if self.current.points[0] == self.current.points[-1]:
            self.current = None
            self.drawingPolygon.emit(False)
            self.update()
            return

        self.current.close()
        self.shapes.append(self.current)
        self.current = None
        self.set_hiding(False)
        self.newShape.emit()
        self.update()

    def close_enough(self, p1, p2):
        # d = distance(p1 - p2)
        # m = (p1-p2).manhattanLength()
        # print "d %.2f, m %d, %.2f" % (d, m, d - m)
        return distance(p1 - p2) < self.epsilon

    def paintEvent(self, event):
        if not self.pixmap:
            return super(Canvas, self).paintEvent(event)

        p = self._painter
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offset_to_center())

        temp = self.pixmap
        if self.overlay_color:
            temp = QPixmap(self.pixmap)
            painter = QPainter(temp)
            painter.setCompositionMode(painter.CompositionMode_Overlay)
            painter.fillRect(temp.rect(), self.overlay_color)
            painter.end()

        p.drawPixmap(0, 0, temp)

        Shape.scale = self.scale
        Shape.label_font_size = self.label_font_size
        for shape in self.shapes:
            if (shape.selected or not self._hide_background) and self.isVisible(shape):
                shape.fill = shape.selected or shape == self.h_shape
                shape.paint(p)
        if self.current:
            self.current.paint(p)
            self.line.paint(p)
        if self.selected_shape_copy:
            self.selected_shape_copy.paint(p)

        # Paint rect
        if self.current is not None and len(self.line) == 2:
            left_top = self.line[0]
            right_bottom = self.line[1]
            rect_width = right_bottom.x() - left_top.x()
            rect_height = right_bottom.y() - left_top.y()
            p.setPen(self.drawing_rect_color)
            brush = QBrush(Qt.BDiagPattern)
            p.setBrush(brush)
            p.drawRect(int(left_top.x()), int(left_top.y()), int(rect_width), int(rect_height))

        if self.drawing() and not self.prev_point.isNull() and not self.out_of_pixmap(self.prev_point):
            p.setPen(QColor(0, 0, 0))
            p.drawLine(int(self.prev_point.x()), 0, int(self.prev_point.x()), int(self.pixmap.height()))
            p.drawLine(0, int(self.prev_point.y()), int(self.pixmap.width()), int(self.prev_point.y()))

        self.setAutoFillBackground(True)
        if self.verified:
            pal = self.palette()
            pal.setColor(self.backgroundRole(), QColor(184, 239, 38, 128))
            self.setPalette(pal)
        else:
            pal = self.palette()
            pal.setColor(self.backgroundRole(), QColor(232, 232, 232, 255))
            self.setPalette(pal)

        p.end()

    def out_of_pixmap(self, p):
        w, h = self.pixmap.width(), self.pixmap.height()
        return not (0 <= p.x() <= w and 0 <= p.y() <= h)

    def restore_cursor(self):
        QApplication.restoreOverrideCursor()

    def offset_to_center(self):
        s = self.scale
        area = super(Canvas, self).size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QPointF(x, y)

    def transform_pos(self, point):
        """Convert from widget-logical coordinates to painter-logical coordinates."""
        return point / self.scale - self.offset_to_center()


    def current_cursor(self):
        cursor = QApplication.overrideCursor()
        if cursor is not None:
            cursor = cursor.shape()
        return cursor

    def override_cursor(self, cursor):
        self._cursor = cursor
        if self.current_cursor() is None:
            QApplication.setOverrideCursor(cursor)
        else:
            QApplication.changeOverrideCursor(cursor)

    def set_drawing_shape_to_square(self, status):
        self.draw_square = status



if __name__ == '__main__':
    app = QApplication(sys.argv)
    # canvas = Canvas()
    # canvas.show()
    # filename = r'E:\360MoveData\Users\qiuhao\Desktop\test\data\000001.jpg'
    # reader = QImageReader(filename)
    # image = reader.read()
    # canvas.load_pixmap(QPixmap.fromImage(image))
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
