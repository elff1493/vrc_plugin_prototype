import math

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QRectF, QPointF
from collections import OrderedDict
from PyQt5.QtGui import QFont, QColor, QPainterPath, QPen, QBrush, QTransform
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, QGraphicsTextItem, QWidget, QVBoxLayout, QLabel, \
    QTextEdit, QGraphicsPathItem

def make_curve(pos1, pos2, inout=0):
    s = pos1
    d = pos2
    dist = (d[0] - s[0]) * 0.5

    cpx_s = +dist
    cpx_d = -dist
    cpy_s = 0
    cpy_d = 0
    EDGE_CP_ROUNDNESS = 100

    ssout = 1
    ssin = not ssout

    if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
        cpx_d *= -1
        cpx_s *= -1

        cpy_d = (
                        (s[1] - d[1]) / math.fabs(
                    (s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001
                )
                ) * EDGE_CP_ROUNDNESS
        cpy_s = (
                        (d[1] - s[1]) / math.fabs(
                    (d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001
                )
                ) * EDGE_CP_ROUNDNESS

    path = QPainterPath(QPointF(pos1[0], pos1[1]))
    path.cubicTo(s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, pos2[0],
                 pos2[1])

    return path


class SerializeJson:
    def __init__(self):
        self.id = id(self)

    def to_json(self) -> dict:
        raise NotImplemented()

    def from_json(self, data, hashs=[]):
        raise NotImplemented()


class Line(SerializeJson):
    def __init__(self, scene, start, end):
        super(Line, self).__init__()
        scene.wires.append(self)
        self.scene = scene
        self.start = start
        if start.line:
            start.line.remove()
        if end.line:
            end.line.remove()

        start.line = self
        if end:
            end.line = self
        self.end = end
        self.ui_line = UiLine(self)
        scene.ui_scene.addItem(self.ui_line)

    def remove_from_plugs(self):
        if self.start:
            self.start.line = None
        if self.end:
            self.end.line = None

    def remove(self):
        self.remove_from_plugs()
        self.scene.ui_scene.removeItem(self.ui_line)
        self.ui_line = None
        self.scene.remove_line(self)

    def test_valid(self):
        if not self.start and self.end:
            return False
        if not self.start.inout:
            return False
        if self.end.inout:
            return False
        if self.start is self.end:
            return False
        return True

    def to_json(self):
        return OrderedDict((
            ("id", self.id),
            ("start", self.start.index),
            ("end", self.end.index),
            ("start_node", self.start.node.id),
            ("end_node", self.end.node.id)
        ))
    @classmethod
    def json_init(cls, scene, data, hashs):
        start, end = hashs[data["start_node"]], hashs[data["end_node"]]
        start, end = start.outputs[data["start"]], end.inputs[data["end"]]
        l = Line(scene, start, end)
    def from_json(self, data, hashs=[]):
        pass

class UiLine(QGraphicsPathItem):
    def __init__(self, line, parent=None):
        super().__init__(parent)
        self._pen = QPen(QColor("#000000"), 2)
        self.line = line
        self.setZValue(-1)

        self.pos1 = (0, 0)
        self.pos2 = (0, 0)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.update_pos()

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        self.update_path()

        painter.setPen(QPen(QColor("#11aa22"), 2) if self.isSelected() else self._pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def update_path(self): # todo use the funtion vvers
        # borrowed this from pavel krupala, idk how half of it works
        s = self.pos1
        d = self.pos2
        dist = (d[0] - s[0]) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0
        EDGE_CP_ROUNDNESS = 100
        if self.line.start is not None:
            ssout = self.line.start.inout
            ssin = not ssout

            if (s[0] > d[0] and ssout) or (s[0] < d[0] and ssin):
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = (
                                (s[1] - d[1]) / math.fabs(
                            (s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001
                        )
                        ) * EDGE_CP_ROUNDNESS
                cpy_s = (
                                (d[1] - s[1]) / math.fabs(
                            (d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001
                        )
                        ) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPointF(self.pos1[0], self.pos1[1]))
        path.cubicTo(s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.pos2[0],
                     self.pos2[1])

        self.setPath(path)
    #def update_path(self):
     #   path = QPainterPath(QPointF(*self.pos1))
    #    path.lineTo(*self.pos2)
      #  self.setPath(path)

    def update_pos(self):
        if self.line.start:
            self.pos1 = self.line.start.get_pos()
            self.pos1 = self.pos1.x(), self.pos1.y()
        if self.line.end:
            self.pos2 = self.line.end.get_pos()
            self.pos2 = self.pos2.x(), self.pos2.y()

class Plug:
    IN = 0
    OUT = 1
    def __init__(self, node:"Node", inout=0, index=0):
        self.node = node
        self.inout = inout
        self.ui_plug = None
        self.type = None
        self.name = "unknown socket"
        self.anchor = 0, 0
        self.padding = 20
        self.index = index
        self.line = None

    def set_line(self, line=None):
        if self.line:
            self.line.remove()
        self.line = line

    def get_pos(self):
        return self.ui_plug.scenePos()


class UiPlug(QGraphicsItem):
    def __init__(self, parent=None, plug=None , anchor=(0,0)):
        super().__init__(parent)
        self.radius = 6
        self.plug = plug
        self.bg_color = QColor("#ffff7700")
        self.outline = QColor("#ff000000")
        self._pen = QPen(self.outline, 1)
        self._brush = QBrush(self.bg_color)
        self.anchor = anchor
        self.setPos(*anchor)
        self.setFlag(QGraphicsItem.ItemIsSelectable)


    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)

    def boundingRect(self) -> QtCore.QRectF:
        return QRectF(
            -self.radius, -self.radius, 2*self.radius, 2*self.radius
        )
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mousePressEvent(event)
        if event.button() != Qt.LeftButton:
            return
        if self.plug.line:
            self.plug.set_line()
        self.plug.node.scene.current_line = self

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseReleaseEvent(event)
        l = self.plug.node.scene.current_line
        if l:
            self.plug.node.scene.current_line = None
            p = event.scenePos()
            p = p.x(), p.y()
            p = self.scene().itemAt(*p, QTransform())
            if type(p) is UiPlug:
                if l.plug.inout:
                    l = Line(self.plug.node.scene, l.plug, p.plug)
                else:
                    l =Line(self.plug.node.scene, p.plug, l.plug)
                if not l.test_valid():
                    l.remove()



class NodeInside(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        #test content
        self.lable = QLabel("owo")
        self.layout.addWidget(self.lable)
        self.layout.addWidget(QTextEdit("bar"))


class UiNodeBace(QGraphicsItem):
    defult_pen = QPen(QColor("#303030"))
    defult_brush = QBrush(QColor("#ff414141"))
    dark_brush = QBrush(QColor("#ff313131"))
    selected_pen = QPen(QColor("#ffa540"))

    def __init__(self, node, content: NodeInside = None, parent=None):
        super().__init__(parent)

        self.node = node
        self.content = content
        self._text_offset = 5
        self.width = 180

        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = node
        self.title_item.setFont(QFont("Ubuntu", 10))
        self.title_item.setDefaultTextColor(QColor("white"))
        self.title_item.setPlainText(self.node.title)
        self.title_item.setPos(self._text_offset, 0)
        self.title_item.setTextWidth(self.width-2*self._text_offset)
        self.title_h = 24
        self.height = 240
        self.edge_w = 10

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        #self.setAcceptHoverEvents(True)

        #addsockets

        #add content
        self.proxy = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.edge_w, self.title_h + self.edge_w,
                               self.width-2*self.edge_w, self.height-2*self.edge_w-self.title_h)
        self.proxy.setWidget(self.content)
        self.inputs = []
        self.outputs = []

        offset = 0
        for x, i in enumerate(self.node.inputs):

            anchor = 0, self.height - (2*self.edge_w+offset)
            offset += i.padding
            i.ui_plug = UiPlug(self, i, anchor)
            self.inputs.append(i.ui_plug)

        offset = 0
        for x, i in enumerate(self.node.outputs):

            anchor = self.width, self.height - (2*self.edge_w + offset)
            offset += i.padding
            i.ui_plug = UiPlug(self, i, anchor)
            self.outputs.append(i.ui_plug)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseMoveEvent(event)
        self.node.scene.ui_scene.update_selected()

    def update_lines(self):
        for i in self.node.inputs + self.node.outputs:
            if i.line:
                i.line.ui_line.update_pos()

    def title(self, t):
        self.title_item.setPlainText(t)

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        outline_t = QPainterPath()
        outline_t.setFillRule(Qt.WindingFill)
        outline_t.addRoundedRect(0, 0, self.width, self.title_h, self.edge_w, self.edge_w)
        outline_t.addRect(0, self.title_h - self.edge_w, self.edge_w, self.edge_w)
        outline_t.addRect(self.width-self.edge_w, self.title_h - self.edge_w, self.edge_w, self.edge_w)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.defult_brush)
        painter.drawPath(outline_t)


        path_bg = QPainterPath()
        path_bg.setFillRule(Qt.WindingFill)
        path_bg.addRoundedRect(0, self.title_h, self.width, self.height - self.title_h, self.edge_w, self.edge_w)
        path_bg.addRect(0, self.title_h, self.edge_w, self.edge_w)
        path_bg.addRect(self.width - self.edge_w, self.title_h, self.edge_w, self.edge_w)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.dark_brush)
        painter.drawPath(path_bg.simplified())

        outline = QPainterPath()
        outline.addRoundedRect(0, 0, self.width, self.height, self.edge_w, self.edge_w)

        painter.setPen(self.defult_pen if not self.isSelected() else self.selected_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(outline.simplified())

    def boundingRect(self) -> QtCore.QRectF:

        return QtCore.QRectF(0, 0, self.width, self.height).normalized()


class Node(SerializeJson):
    def __init__(self, scene, inputs=None, outputs=None, title="unknown node"):
        super(Node, self).__init__()
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.scene = scene
        self._title = title
        content = NodeInside()

        self.scene.add_node(self)

        self.inputs = [Plug(self, index=0), Plug(self, index=1)]
        self.outputs = [Plug(self, inout=Plug.OUT, index=0), Plug(self, inout=Plug.OUT, index=1)]

        self.ui_node = UiNodeBace(self, content)
        self.title = title
        self.scene.ui_scene.addItem(self.ui_node)
    def set_pos(self, pos):
        self.ui_node.setPos(*pos)
    def remove(self):
        self.scene.remove_node(self)
        for i in self.inputs + self.outputs:
            i.set_line()
        self.scene.ui_scene.removeItem(self.ui_node)
        self.ui_node = None

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, t):
        self._title = t
        self.ui_node.title(t)

    def to_json(self):

        return OrderedDict((
            ("id", self.id),
            ("title", self._title),
            ("x", self.ui_node.scenePos().x()),
            ("y", self.ui_node.scenePos().y())
        ))
    def from_json(self, data, hashs=None):
        self.id = data["id"]
        hashs[self.id] = self
        self.title = data["title"]
        self.ui_node.setPos(data["x"], data["y"])
