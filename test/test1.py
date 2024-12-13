import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QPixmap


class Canvas(QWidget):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Pixmap Example')
        self.image = QPixmap(r'E:\360MoveData\Users\qiuhao\Desktop\test\data\000001.jpg')  # 替换为你的图片路径

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.image)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    canvas = Canvas()
    canvas.show()
    sys.exit(app.exec_())
