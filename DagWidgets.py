import math

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, pyqtProperty
from PyQt5.QtGui import QColor, QPainter, QPen, QMouseEvent, QWheelEvent, QFont, QTransform
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsTextItem
from nodes import make_curve, SerializeJson, Node
import json
from collections import OrderedDict
from wires import Line, UiLine
from moduals.moduals import Module

class Scene(SerializeJson):
    def __init__(self):
        super(Scene, self).__init__()
        self.nodes = []
        self.wires = []
        self.file = ""
        self.size = 10000, 10000
        self.current_line = None
        self.ui_scene = UiScene(self, parent=None)
        self.ui_scene.set_size(*self.size)

    def add_node(self, node):
        self.nodes.append(node)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)

    def add_line(self, line):
        pass

    def remove_line(self, line):
        if line in self.wires:
            self.wires.remove(line)

    def save_to_file(self, file):
        with open(file, "w") as file:
            json.dump(self.to_json(), file, indent=3)

    def save(self):
        if self.file:
            self.save_to_file(self.file)
            return True
        return False

    def load_file(self, file):
        self.file = file
        self.clear()
        with open(file, "r") as file:
            d = json.load(file)
            self.from_json(d)

    def clear(self):
        for i in self.nodes.copy():
            i.remove()
        for i in self.wires.copy():
            i.remove()

    def to_json(self) -> dict:
        nodes, lines = [], []
        for i in self.nodes:
            nodes.append(i.to_json())
        for i in self.wires:
            lines.append(i.to_json())
        return OrderedDict((
            ("id", self.id),
             ("width", self.size[0]),
             ("height", self.size[1]),
            ("nodes", nodes),
            ("wires", lines)
        ))

    def from_json(self, data, hashs=None):
        hashs = {}
        self.size = data["width"], data["height"]
        for i in data["nodes"]:

            node = Module.get_node(i["type"])
            node(self).from_json(i, hashs)
        for i in data["wires"]:
            Line.json_init(self, i, hashs)


class DagView(QGraphicsView):
    def __init__(self, parent, dag_display):
        self.dag_display = dag_display

        super().__init__(parent)
        self.setScene(dag_display)
        self.dag_display.view = self
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.zoom = 10
        self.setAcceptDrops(True)


    @pyqtProperty(QColor)
    def bg_color(self):
        return self.dag_display._bg_color

    @bg_color.setter
    def bg_color(self, x):
        self.dag_display.setBackgroundBrush(x)
        self.dag_display._bg_color = x

    @pyqtProperty(QColor)
    def bg_line_color(self):
        return self.dag_display._bg_line_C

    @bg_line_color.setter
    def bg_line_color(self, x):
        self.dag_display._bg_line_C = x

    @pyqtProperty(int)
    def bg_spacing(self):
        return self.dag_display._bg_spacing

    @bg_spacing.setter
    def bg_spacing(self, x):
        self.dag_display._bg_spacing = x

    @pyqtProperty(int)
    def bg_thick_spacing(self):
        return self.dag_display._bg_thicc_spacing

    @bg_thick_spacing.setter
    def bg_thick_spacing(self, x):
        self.dag_display._bg_thicc_spacing = x



    def mousePressEvent(self, event):

        if event.button() != Qt.MiddleButton:
            if event.button() == Qt.LeftButton:
                self.l_mouse_press(event)


            super().mousePressEvent(event)
            return

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        super().mousePressEvent(QMouseEvent(event.type(), event.localPos(), event.screenPos()
                                           ,Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers()))

    def l_mouse_press(self, event):
        item = self.itemAt(event.pos())
        if event.modifiers() & Qt.ControlModifier:
            self.setDragMode(QGraphicsView.RubberBandDrag)
        else:
            self.setDragMode(QGraphicsView.NoDrag)

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("application/x-node"):
            event.accept()
        else:
            event.ignore()
            super(DagView, self).dragEnterEvent(event)

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasFormat("application/x-node"):
            event.accept()
        else:
            event.ignore()
            super(DagView, self).dragMoveEvent(event)

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if event.mimeData().hasFormat("application/x-node"):
            n: Node = event.source().node.node.__class__(self.dag_display.scene)
            p = self.mapToScene(event.pos())
            n.set_pos((p.x(), p.y()))
        else:
            event.ignore()
            super(DagView, self).dropEvent(event)


    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.setDragMode(QGraphicsView.NoDrag)
        if event.button() != Qt.MiddleButton:
            super().mouseReleaseEvent(event)
            return

    def wheelEvent(self, event: QWheelEvent) -> None: #todo test still works with mouse
        zoom = 1.25
        zoom_max = 11
        zoom_min = 0.1
        if abs(event.angleDelta().y()) != 120:
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - event.angleDelta().x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - event.angleDelta().y())
            return
        elif event.angleDelta().y() < 0:
            zoom = 1/zoom
        self.scale(zoom, zoom)
        if self.transform().m11() >= zoom_max:
            self.set_scale(zoom_max)
        elif self.transform().m11() <= zoom_min:
            self.set_scale(zoom_min)

    def set_scale(self, zoom):
        mat = QTransform().fromScale(zoom, zoom)
        mat = mat * QTransform.fromTranslate(self.transform().dx(), self.transform().dy())
        self.setTransform(mat)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            for i in self.dag_display.selectedItems():
                if isinstance(i, UiLine):
                    i.line.remove()
                elif hasattr(i, "node"):
                    i.node.remove()
        if event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
            self.dag_display.scene.save_to_file("test.txt")
        if event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:

            self.dag_display.scene.load_file("test.txt")
        super().keyPressEvent(event)


class UiScene(QGraphicsScene):
    def __init__(self, scene, parent):
        self.scene = scene
        self.view = None
        self._bg_line_C = QColor("#101010")
        self._bg_spacing = 20
        self._bg_thicc_spacing = 5
        self._bg_color = QColor("#a0a0a0")
        self.m_pos = 0, 0
        super().__init__(parent)

        self.setBackgroundBrush(self._bg_color)

    def set_size(self, w, h):
        self.setSceneRect(-w//2, -h//2, w, h)

    def update_selected(self):
        for i in self.selectedItems():
            if hasattr(i, "update_lines"):
                i.update_lines()

    def drawBackground(self, painter: QPainter, rect: QtCore.QRectF) -> None:
        super(UiScene, self).drawBackground(painter, rect)
        space = self._bg_spacing
        a1 = int(math.floor(rect.left()))
        a2 = int(math.ceil(rect.right()))
        a3 = int(math.floor(rect.top()))
        a4 = int(math.ceil(rect.bottom()))

        painter.setPen(QPen(self._bg_line_C, 1))

        start_x = a1 - (a1 % space)
        start_y = a3 - (a3 % space)
        painter.drawLines(*(QtCore.QLine(x, a3, x, a4) for x in range(start_x, a2, space)),
                          *(QtCore.QLine(a1, y, a2, y) for y in range(start_y, a4, space)))

        painter.setPen(QPen(self._bg_line_C, 2))

        start_x = a1 - (a1 % (space*self._bg_thicc_spacing))
        start_y = a3 - (a3 % (space*self._bg_thicc_spacing))
        painter.drawLines(*(QtCore.QLine(x, a3, x, a4) for x in range(start_x, a2, space*self._bg_thicc_spacing)),
                          *(QtCore.QLine(a1, y, a2, y) for y in range(start_y, a4, space*self._bg_thicc_spacing)))

        if self.scene.current_line:
            p = self.scene.current_line.scenePos()
            p = p.x(), p.y()
            pen = QPen(QColor("#ff0011dd"), 2)
            pen.setStyle(Qt.DashDotDotLine)
            painter.setPen(pen)
            painter.drawPath(make_curve(p, self.m_pos))

    def dragEnterEvent(self, e):
        #e.accept()
        e.ignore()
        super(UiScene, self).dragEnterEvent(e)
        item = self.itemAt(e.scenePos(), self.views()[0].transform())
        print("item enter,", item)
        

    def dropEvent(self, e):
        # find item at these coordinates
        e.ignore()
        super(UiScene, self).dropEvent(e)
        item = self.itemAt(e.scenePos(), self.views()[0].transform())

        print("item drop,", item)

    def dragMoveEvent(self, e):
        e.ignore()
        super(UiScene, self).dragMoveEvent(e)
        item = self.itemAt(e.scenePos(), self.views()[0].transform())
        #e.accept()

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mousePressEvent(event)
        self.update()

        self.m_pos = event.scenePos().x(), event.scenePos().y()

