from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QDockWidget, QMainWindow, QAction, QListWidget, \
    QListWidgetItem, QMenu, QTableWidget, QTableWidgetItem, QLabel

from DagWidgets import DagView, Scene
from portscan import get_scan

from wires import Line

from moduals.built_in.maths import *
from moduals.built_in.events import *
from moduals.moduals import Module
from moduals.built_in.debug import *
from moduals.built_in.vrc_osc import *

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
                n.set_pos((p.x(), p.y())) # todo set mouse pos
        super(DagEditor, self).contextMenuEvent(a0)



class NodeLibraryList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setFlow(QListWidget.LeftToRight)

    def add_item(self, node):
        item = QListWidgetItem(node.full_name, self)
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled)
        item.setData(Qt.UserRole + 1, node.op_name)


class NodeLibrary(QDockWidget):
    def __init__(self):
        super(NodeLibrary, self).__init__("node library")
        self.list = NodeLibraryList()
        for lib in Module.libraries.values():
            for i in lib.nodes.values():
                self.list.add_item(i)
        self.setWidget(self.list)
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
        #header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        #header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)


        self.table.setHorizontalHeaderLabels(["app", "app name", "port", "address", "status", "is local"])
        for i, s in enumerate(scan):
            #icon = QTableWidgetItem()
            #icon.setIcon(s.icon)
            lab = QLabel();
            lab.setPixmap(s.icon.pixmap(QSize(64, 64)))
            lab.setAlignment(Qt.AlignHCenter)
            self.table.setCellWidget(i, 0, lab)
            #self.table.setItem(i, 0, icon)
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