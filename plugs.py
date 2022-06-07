from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QColor, QPen, QBrush, QTransform
from PyQt5.QtWidgets import QGraphicsItem

import nodes


class Plug:
    IN = 0
    OUT = 1
    def __init__(self, node, inout=0, index=0, name="unknown plug", _type=None):
        self.node = node
        self.inout = inout
        self.ui_plug = None
        self.type = _type
        self.name = name
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
                    l = nodes.Line(self.plug.node.scene, l.plug, p.plug)
                else:
                    l = nodes.Line(self.plug.node.scene, p.plug, l.plug)
                if not l.test_valid():
                    l.remove()
