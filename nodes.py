import math

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QPointF
from collections import OrderedDict
from PyQt5.QtGui import QFont, QColor, QPainterPath, QPen, QBrush
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, QGraphicsTextItem, QWidget, QVBoxLayout, QLabel

from evaluator import Evaluator
from plugs import Plug, UiPlug
from serialize import SerializeJson


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


class PlugSlot(QWidget):
    def __init__(self):
        super(PlugSlot, self).__init__()
        

class NodeInside(QWidget):
    def __init__(self):
        super().__init__()
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)


class UiNodeBace(QGraphicsItem):
    defult_pen = QPen(QColor("#303030"))
    defult_brush = QBrush(QColor("#ff414141"))
    dark_brush = QBrush(QColor("#ff313131"))
    selected_pen = QPen(QColor("#ffa540"))

    def __init__(self, node,  parent=None, showroom=False):
        super().__init__(parent)

        self.node = node
        self.content = NodeInside()
        self._text_offset = 5
        self.width = 112

        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = node
        self.title_item.setFont(QFont("Ubuntu", 10))
        self.title_item.setDefaultTextColor(QColor("white"))
        self.title_item.setPlainText(self.node.title)
        self.title_item.setPos(self._text_offset, 0)
        self.title_item.setTextWidth(self.width-2*self._text_offset)
        self.title_h = 24
        self.height = 90
        self.edge_w = 10

        if not showroom:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        #self.setAcceptHoverEvents(True)

        #addsockets

        #add content
        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.geometryChanged.connect(self.resized)
        self.proxy.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.content.setGeometry(self.edge_w, self.title_h+4,#+ self.edge_w,
                              self.width-2*self.edge_w, self.height-2*self.edge_w-self.title_h)
        self.proxy.setWidget(self.content)
        self.inputs = []
        self.outputs = []

        offset = 0
        for x, i in enumerate(self.node.inputs):

            anchor = 0, self.height - (2*self.edge_w+offset)
            offset += i.padding
            i.ui_plug = UiPlug(self, i, anchor)  # todo add a gui init
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

    def resized(self):
        p = self.proxy.boundingRect()
        print(p)
        self.width = max(p.width(), self.width)
        self.height = p.height() + self.title_h + self.edge_w

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

    def mousePressEvent(self, event):
        super(UiNodeBace, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            #todo remove, debug
            lable = QLabel("osc debug")
            lable.setGeometry(0, 100, 100, 100)
            self.content.layout.addWidget(lable)
            #====
            self.node.click()


class Node(SerializeJson):
    full_name = "invalid node"
    op_name = "null node"
    inputs = ()
    outputs = ()
    description = "invalid node, somethings gone wrong :)"
    e = Evaluator()

    def __init__(self, scene, inputs=None, outputs=None, title=None, showroom=False):
        super(Node, self).__init__()
        inputs = inputs or enumerate(self.__class__.inputs)
        outputs = outputs or enumerate( self.__class__.outputs)
        self.scene = scene
        self._title = None
        self.showroom = showroom

        self.scene.add_node(self)

        self.inputs = [Plug(self, index=index, name=i) for index, i in inputs]
        self.outputs = [Plug(self, index=index, name=i, inout=Plug.OUT) for index, i in outputs]

        #self.inputs = [Plug(self, index=0), Plug(self, index=1)]
        #self.outputs = [Plug(self, inout=Plug.OUT, index=0), Plug(self, inout=Plug.OUT, index=1)]
        self.init_gui(showroom)

        self.title = title or self.full_name

    def set_flag(self, name):
        print(self, name)

    def init_gui(self, showroom):

        self.ui_node = UiNodeBace(self, showroom=showroom)

        self.scene.ui_scene.addItem(self.ui_node)

    def set_pos(self, pos):
        self.ui_node.setPos(*pos)

    def eval(self, data):
        pass

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

    def click(self):
        pass
