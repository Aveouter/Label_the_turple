import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window , self).__init__(parent)
        self.resize(400, 300)
        self.text = ""

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.text = "press leftbutton"
        if event.button() == Qt.RightButton:
            self.text = "press rightbutton"

        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.begin(self)

        if self.text:
            painter.drawText(self.rect() , Qt.AlignBottom | Qt.AlignCenter , self.text)
            self.clearMessage()
            self.update()

    def clearMessage(self):
        self.text = ""


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = Window()
    dialog.show()
    app.exec_()
