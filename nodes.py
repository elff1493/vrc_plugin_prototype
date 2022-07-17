import math

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QPointF, QMimeData, QDataStream, QByteArray, QIODevice
from collections import OrderedDict
from PyQt5.QtGui import QFont, QColor, QPainterPath, QPen, QBrush, QDrag, QPixmap, QPainter
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, QGraphicsTextItem,  QVBoxLayout,  \
    QStyleOptionGraphicsItem, QFrame

from evaluator import Evaluator
from plugs import Plug, UiPlug, PlugSlot
from serialize import SerializeJson
from symbols.symbols import Category


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


class NodeInside(QFrame):
    def __init__(self, node):
        super().__init__()
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        #self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.node = node
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        self.setLayout(self.layout)
        # self.slots = []

        # slot = node.node.__class__.input_slots
        # for i in node.inputs:
        #     n = PlugSlot(self, i.plug, inout=PlugSlot.IN, )
        #     i.plug.ui_symbol_slot = n
        #     if i.plug.name in slot:
        #         sym = Category.get_symbol(slot[i.plug.name])
        #         if sym:
        #             n.contents.setParent(None)
        #             n.contents = sym(n, i.plug.name)
        #             if not (sym.default is None):
        #                 n.contents.set_data(sym.default)
        #         else:
        #             print("symbol not found")
        #     self.layout.addWidget(n)
        #     self.slots.append(n)
        #
        # slot = node.node.__class__.output_slots
        # for i in node.outputs:
        #     n = PlugSlot(self, i.plug, inout=PlugSlot.OUT)
        #     i.plug.ui_symbol_slot = n
        #     if i.plug.name in slot:
        #         sym = Category.get_symbol(i.plug.op_code)
        #         if sym:
        #             n.contents.setParent(None)
        #             n.contents = sym(n, i.plug.name)
        #     self.layout.addWidget(n)
        #     self.slots.append(n)


class UiNodeBace(QGraphicsItem):
    defult_pen = QPen(QColor("#303030"))
    defult_brush = QBrush(QColor("#ff414141"))
    dark_brush = QBrush(QColor("#ff313131"))
    selected_pen = QPen(QColor("#ffa540"))

    def __init__(self, node,  parent=None, showroom=False):
        super().__init__(parent)

        self.node = node

        self._text_offset = 5
        self.width = 112
        self.showroom = showroom

        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = node
        self.title_item.setFont(QFont("Ubuntu", 10))
        self.title_item.setDefaultTextColor(QColor("white"))
        self.title_item.setPlainText(self.node.title)
        self.title_item.setPos(self._text_offset, 0)
        #self.title_item.setTextWidth(self.width-2*self._text_offset)
        self.width = max((self.width, self.title_item.boundingRect().width() + self._text_offset*2))
        self.title_h = 24
        self.height = 90
        self.edge_w = 10

        if not showroom:
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        else:
            pass
        #self.setAcceptHoverEvents(True)

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.geometryChanged.connect(self.resized)
        self.proxy.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.plugs = []
        # self.inputs = []
        # self.outputs = []

        # offset = 0
        # for x, i in enumerate(self.node.inputs):
        #
        #     anchor = 0, self.height - (2*self.edge_w+offset)
        #     offset += i.padding
        #     i.ui_plug = UiPlug(self, i, anchor)  # todo add a gui init
        #     self.inputs.append(i.ui_plug)
        #
        # offset = 0
        # for x, i in enumerate(self.node.outputs):
        #
        #     anchor = self.width, self.height - (2*self.edge_w + offset)
        #     offset += i.padding
        #     i.ui_plug = UiPlug(self, i, anchor)
        #     self.outputs.append(i.ui_plug)

        self.content = NodeInside(self)
        self.content.setGeometry(self.edge_w, self.title_h + 4,  # + self.edge_w,
                                 self.width - 2 * self.edge_w, self.height - 2 * self.edge_w - self.title_h)
        self.proxy.setWidget(self.content)
        self.resized()

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        super().mouseMoveEvent(event)
        self.node.scene.ui_scene.update_selected()

    def resized(self):
        p = self.proxy.boundingRect()
        self.width = max((p.width(), self.title_item.boundingRect().width() + 2*self._text_offset)) + 2*self.edge_w
        self.height = p.height() + self.title_h + self.edge_w
        self.plugs_pos(self.width)

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
        if event.buttons() == Qt.LeftButton and self.showroom:
            drag = QDrag(self.content)
            mime = QMimeData()
            data = QByteArray()
            streem = QDataStream(data, QIODevice.WriteOnly)#todo add importan data to strem

            mime.setData("application/x-node", data)
            drag.setMimeData(mime)

            image = QPixmap(self.boundingRect().size().toSize())
            paint = QPainter()
            paint.begin(image)
            self.paint(paint, QStyleOptionGraphicsItem())
            for i in self.childItems(): #todo make sure it works after the node content is redone
                i.paint(paint, QStyleOptionGraphicsItem(), None)
            drag.setPixmap(image)
            drag.setHotSpot(event.pos().toPoint()) # todo make placement work with hotspot (mime data?)
            drag.exec_(Qt.MoveAction)
            paint.end()
            return
        if event.button() == Qt.LeftButton:
            self.node.click()

    def plugs_pos(self, w):
        for i in self.plugs:
            i.plug.ui_symbol_slot.update_plug_pos(w)

    def add_ui_plug(self, plug, symbol):
        self.plugs.append(plug)
        self.content.layout.addWidget(symbol)


class Node(SerializeJson):
    full_name = "invalid node"  # display name of the node
    op_name = "null_node"  # internal name of the node
    inputs = ()  # list of name of input to the node
    input_slots = {}  # key is name of input and value is op code of what symbol is...
    # the default for that input type if key exist a default will be provided
    outputs = ()   # same for outputs
    output_slots = {}
    description = "invalid node, somethings gone wrong :)"
    e = Evaluator()

    def __init__(self, scene, inputs=None, outputs=None, title=None, showroom=False):
        super(Node, self).__init__()
        inputs = inputs or enumerate(self.__class__.inputs)
        outputs = outputs or enumerate(self.__class__.outputs)
        self.scene = scene
        self._title = None
        self.showroom = showroom

        self.scene.add_node(self)

        self.init_gui(showroom)

        self.inputs = [Plug(self, index=index, name=i) for index, i in inputs]
        self.outputs = [Plug(self, index=index, name=i, inout=Plug.OUT) for index, i in outputs]

        self.ui_node.resized()
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
