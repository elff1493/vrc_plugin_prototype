from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QDockWidget, QMainWindow, QAction, QListWidget, \
    QListWidgetItem

from DagWidgets import DagView, Scene
from nodes import Line

from moduals.built_in.maths import *
from moduals.moduals import Module

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

        self.make_debug_nodes()

    def make_debug_nodes(self):
        node = Node(self.scene, title="owo")
        node.set_pos((-300, 0))
        node2 = Node(self.scene, title="node editor")
        node2.set_pos((-50, -100))
        node3 = Node(self.scene, title="nyan")
        node3.set_pos((200, 0))
        Line(self.scene, node.outputs[0], node2.inputs[1])
        Line(self.scene, node2.outputs[1], node3.inputs[1])


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
        print(Module.libraries)
        for lib in Module.libraries.values():
            for i in lib.nodes.values():
                self.list.add_item(i)
        self.setWidget(self.list)
        self.setFloating(False)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu = self.menuBar()
        self.menu_init()
        self.setWindowIcon(QtGui.QIcon('logo.png'))
        self.setWindowTitle("new window")
        self.setGeometry(1100, 200, 800, 600)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setWindowIcon(QtGui.QIcon('icon.ico'))
        self.setLayout(self.layout)
        self.editor = DagEditor(self)
        self.setCentralWidget(self.editor)
        self.dock = [NodeLibrary()]
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock[0])
        #self.layout.addWidget(self.editor)

    def menu_init(self):
        m = self.menuBar()
        self.file_menu = m.addMenu("&File")
        action = QAction("&Load", self)
        action.setShortcut("Ctrl+p")
        action.triggered.connect(self.load_test)

        self.file_menu = m.addMenu("&Edit")
        self.file_menu = m.addMenu("&Window")
        action = QAction("&load", self)
        action.setShortcut("Ctrl+p")

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