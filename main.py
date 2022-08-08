from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QMainWindow, QAction, QMenu, QFileDialog

from asyncqt import QEventLoop

from DagWidgets import DagView, Scene

import moduals.built_in as node_moduals
import symbols.built_in as node_symbols

from util_docks.node_libray import NodeLibrary
from util_docks.port_scan import PortScan
from util_docks.console import Console
import asyncio
import sys


class DagEditor(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scene = Scene()

        self.view = DagView(self, self.scene.ui_scene)

        self.layout.addWidget(self.view)
        self.setLayout(self.layout)
        self.debug_count = 0
        self.rmenu = QMenu(self)
        for i in node_moduals.Module.libraries.values():
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
                n = node_moduals.Module.get_node(op_code)
                n = n(self.scene)
                p = self.scene.ui_scene.view.mapToScene(a0.pos())
                n.set_pos((p.x(), p.y()))
        super(DagEditor, self).contextMenuEvent(a0)

    def keyPressEvent(self, event):
        super(DagEditor, self).keyPressEvent(event)
        return
        if event.key() == QtCore.Qt.Key_Q:
            self.debug_spawn()
        event.accept()

    def debug_spawn(self):
        print(self.debug_count)
        self.debug_count += 1
        n = node_moduals.Module.get_node("time.seconds_epoc")
        n = n(self.scene)
        p = self.scene.ui_scene.view.mapToScene(self.mapFromGlobal( QCursor.pos()))
        n.set_pos((p.x(), p.y()))


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.menu = self.menuBar()
        self.menu_init()
        self.setWindowIcon(QtGui.QIcon('resources/images/logo.png'))
        self.setWindowTitle("new window")
        self.setGeometry(1100, 200, 800, 600)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.editor = DagEditor(self)
        self.setCentralWidget(self.editor)
        self.init_docks()

    def init_docks(self):
        self.dock = [NodeLibrary(), PortScan(), Console()]
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock[0])
        a = self.dock[0].toggleViewAction()
        a.setText("&Nodes")
        self.window_menu.addAction(a)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock[1])
        a = self.dock[1].toggleViewAction()
        a.setText("&Port scanner")
        self.window_menu.addAction(a)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dock[2])
        a = self.dock[2].toggleViewAction()
        a.setText("&Console")
        self.window_menu.addAction(a) # todo make loop

    def open_file(self):
        file = QFileDialog.getOpenFileName(caption="open file")
        if file[0]:
            self.editor.scene.load_file(file[0])

    def save(self):
        if not self.editor.scene.save():
            self.save_as()

    def save_as(self):
        file = QFileDialog.getSaveFileName(caption="save file")
        if file[0]:
            self.editor.scene.save_to_file(file[0])

    def menu_init(self):
        m = self.menuBar()

        self.file_menu = m.addMenu("&File")
        action = QAction("&Open", self)
        action.triggered.connect(self.open_file)
        self.file_menu.addAction(action)

        action = QAction("&Save", self)
        action.triggered.connect(self.save)
        self.file_menu.addAction(action)

        action = QAction("&Save as", self)
        action.triggered.connect(self.save_as)
        self.file_menu.addAction(action)

        self.edit_menu = m.addMenu("&Edit")
        self.window_menu = m.addMenu("&Window")

        self.debug_menu = m.addMenu("&Debug")
        action = QAction("&Test program", self)
        action.setShortcut("")
        action.triggered.connect(self.load_test)
        self.debug_menu.addAction(action)

        self.dock_actions_menu = []

    def show_docked(self, index):
        self.dock[index].setVisible(not self.dock[index].isVisible())

    def load_test(self):
        self.editor.scene.load_file("example_programs/gettime.node")


class MainApp(QApplication):
    def __init__(self):
        super().__init__([])
        qss = "resources/qss/stylesheet.qss"
        with open(qss, "r") as f:
            self.setStyleSheet(f.read())

        self.window = MainWindow(None)
        self.window.show()

    def start(self):
        self.exec()


def main():
    app = MainApp()
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        sys.exit(loop.run_forever())



if __name__ == "__main__":
    main()