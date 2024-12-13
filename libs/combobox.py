'''
创建一个带有下拉选择框的小部件
'''

import sys
try:
    from PyQt5.QtWidgets import QWidget, QHBoxLayout, QComboBox
except ImportError:
    if sys.version_info.major >= 3:
        import sip
        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import QWidget, QHBoxLayout, QComboBox


class ComboBox(QWidget): 
    def __init__(self, parent=None, items=[]):
        super(ComboBox, self).__init__(parent)

        layout = QHBoxLayout()
        self.cb = QComboBox()
        self.items = items
        self.cb.addItems(self.items)

        self.cb.currentIndexChanged.connect(parent.combo_selection_changed)

        layout.addWidget(self.cb)
        self.setLayout(layout)

    def update_items(self, items):
        self.items = items
        self.cb.clear()
        self.cb.addItems(self.items)
