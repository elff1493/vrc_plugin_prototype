from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGraphicsView

from DagWidgets import UiScene, DagView, Scene
from nodes import Node, Line


class DagEditor(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.scene = Scene()
        node = Node(self.scene, title="owo")
        node.set_pos((-300, 0))
        node2 = Node(self.scene, title="UwU")
        node2.set_pos((-50, -100))
        node3 = Node(self.scene, title="nyan")
        node3.set_pos((200, 0))

        line = Line(self.scene, node.outputs[0], node2.inputs[1])
        line = Line(self.scene, node2.outputs[1], node3.inputs[1])
        self.view = DagView(self, self.scene.ui_scene)

        self.layout.addWidget(self.view)
        self.setLayout(self.layout)


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(200, 200, 800, 600)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)
        self.editor = DagEditor(self)
        self.layout.addWidget(self.editor)
        
        #self.view.setScene(self.dag)


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