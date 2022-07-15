from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDockWidget, QTabWidget, QFrame, QVBoxLayout, QGraphicsView, QGraphicsScene

from moduals.moduals import Module
from symbols.symbols import Category


class NodeLibrary(QDockWidget):
    def __init__(self):
        super(NodeLibrary, self).__init__("node library")
        self.nodes = QTabWidget()
        self.vars = QTabWidget()
        self.tabs = QTabWidget(self)
        self.tabs.addTab(self.nodes, "nodes")
        self.tabs.addTab(self.vars, "vars")


        for name, lib in Module.libraries.items():
            display = NodeLibraryList()
            self.nodes.addTab(display, name)
            for i in lib.nodes.values():
                display.add_item(i)

        for name, syb in Category.group.items():
            display = SymbolList()
            self.vars.addTab(display, name)
            for i in syb.symbols.values():
                display.add_item(i)


        self.tabs.setTabPosition(QTabWidget.West)
        self.setWidget(self.tabs)
        self.setFloating(False)
        self.setVisible(False)


class PickNodeScene(QGraphicsScene):
    def __init__(self):
        super(PickNodeScene, self).__init__()
        self.setBackgroundBrush(QColor("#ddddff"))
        self.nodes = []

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super(PickNodeScene, self).drawBackground(painter, rect)

    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None: #todo fix jank

        offset = [0, 0 + 20]
        row_index = 0
        row_height = 0

        ypad = 10
        abs_height = 10 + ypad
        padding = 20
        for i, node in enumerate(self.nodes):
            w, h = node.ui_node.width, node.ui_node.height
            row_height = max(h, row_height)

            offset[0] += padding
            if offset[0] + w + padding > rect.width():
                row_index += 1
                abs_height += row_height + ypad
                offset = [padding, abs_height]
                node.set_pos(offset)
                offset[0] += w

            else:

                node.set_pos(offset)
                offset[0] += w

        super(PickNodeScene, self).drawForeground(painter, rect)

class NodeLibraryList(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.ui_scene = PickNodeScene()
        self.setScene(self.ui_scene)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        #self.nodes = []

        #self.setDragEnabled(True)
        #self.setFlow(QListWidget.LeftToRight)
    def add_node(self, node):
        self.ui_scene.nodes.append(node)

    def add_item(self, node):
        n = node(self, showroom=True)
        #n.set_pos((len(self.nodes)*100, 100))
        #item = QListWidgetItem(node.full_name, self)
        #item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled)
        #item.setData(Qt.UserRole + 1, node.op_name)


class SymbolList(QFrame):
    def __init__(self):
        super(SymbolList, self).__init__()
        self.layout = QVBoxLayout()

    def add_item(self, item):
        item = item(self, "input", showroom=True)
        self.layout.addWidget(item)



