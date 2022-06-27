from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QDockWidget, QMainWindow, QAction, QListWidget, \
    QListWidgetItem, QMenu, QTableWidget, QTableWidgetItem, QLabel, QTabWidget, QTabBar, QGraphicsView, QGraphicsScene, \
    QFrame

from DagWidgets import DagView, Scene
from portscan import get_scan

from moduals.built_in.maths import *
from moduals.built_in.events import *
from moduals.moduals import Module
from moduals.built_in.debug import *
from moduals.built_in.vrc_osc import *

from symbols.symbols import Category
from symbols.built_in.test import *

import ctypes
myappid = 'mycompany.myproduct.subproduct.version'  # fix for icon
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class DagEditor(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scene = Scene()

        self.view = DagView(self, self.scene.ui_scene)

        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

        #self.make_debug_nodes()

        self.rmenu = QMenu(self)
        for i in Module.libraries.values():
            m = self.rmenu.addMenu(i.name)
            for n in i.nodes.values():
                action = QAction(n.full_name, self)
                action.setData(i.name + "." + n.op_name)
                m.addAction(action)

    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        action = self.rmenu.exec_(self.mapToGlobal(a0.pos()))
        if type(action) is QAction:
            op_code = action.data()
            if op_code:
                n = Module.get_node(op_code)
                n = n(self.scene)
                p = self.scene.ui_scene.view.mapToScene(a0.pos())
                n.set_pos((p.x(), p.y()))
        super(DagEditor, self).contextMenuEvent(a0)


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

            print(offset)
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
        print("ITEM ADD")
        item = item(self, "input", showroom=True)
        self.layout.addWidget(item)


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


class PortScan(QDockWidget):
    def __init__(self):
        super(PortScan, self).__init__("port scan")
        self.table = QTableWidget()
        self.setWidget(self.table)
        self.setFloating(False)
        self.setVisible(False)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.reset()

    def reset(self):
        scan = get_scan()
        scan = sorted(scan, key=lambda x: x.custom_icon, reverse=True)
        self.table.setRowCount(len(scan))
        self.table.setColumnCount(6)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.table.setHorizontalHeaderLabels(["app", "app name", "port", "address", "status", "is local"])

        for i, s in enumerate(scan):
            lab = QLabel()
            lab.setPixmap(s.icon.pixmap(QSize(64, 64)))
            lab.setAlignment(Qt.AlignHCenter)
            self.table.setCellWidget(i, 0, lab)
            self.table.setItem(i, 1, QTableWidgetItem(s.name))
            self.table.setItem(i, 2, QTableWidgetItem(str(s.port)))
            self.table.setItem(i, 3, QTableWidgetItem(s.addr))
            self.table.setItem(i, 4, QTableWidgetItem(s.status))
            self.table.setItem(i, 5, QTableWidgetItem("local" if s.local else "remote"))


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu = self.menuBar()
        self.menu_init()
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        self.setWindowTitle("new window")
        self.setGeometry(1100, 200, 800, 600)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)        #self.setWindowIcon(QtGui.QIcon('icon.ico'))x
        self.setLayout(self.layout)
        self.editor = DagEditor(self)
        self.setCentralWidget(self.editor)
        self.init_docks()
        #self.layout.addWidget(self.editor)

    def init_docks(self):
        self.dock = [NodeLibrary(), PortScan()]
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock[0])
        a = self.dock[0].toggleViewAction()
        a.setText("&Nodes")
        self.window_menu.addAction(a)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock[1])
        a = self.dock[1].toggleViewAction()
        a.setText("&Port scanner")
        self.window_menu.addAction(a)

    def menu_init(self):
        m = self.menuBar()
        self.file_menu = m.addMenu("&File")
        action = QAction("&Load", self)
        action.setShortcut("Ctrl+p")
        action.triggered.connect(self.load_test)
        self.file_menu.addAction(action)

        self.edit_menu = m.addMenu("&Edit")
        self.window_menu = m.addMenu("&Window")

        self.dock_actions_menu = []

    def show_docked(self, index):
        self.dock[index].setVisible(not self.dock[index].isVisible())

    def load_test(self):
        print("test")
        self.editor.scene.load_file("test.txt")


class MainApp(QApplication):
    def __init__(self):
        super().__init__([])
        qss = "stylesheet.qss"
        with open(qss, "r") as f:
            self.setStyleSheet(f.read())

        self.window = MainWindow(None)
        self.window.show()

    def start(self):
        self.exec()


def main():
    app = MainApp()
    app.start()


if __name__ == "__main__":
    main()