import math
from collections import OrderedDict

from PyQt5 import QtGui
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QPainterPath, QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsPathItem

from serialize import SerializeJson


class Line(SerializeJson):
    def __init__(self, scene, start, end):
        super(Line, self).__init__()
        scene.wires.append(self)
        start.next_plug = end
        end.next_plug = start
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
            self.start.next_plug = None

        if self.end:
            self.end.line = None
            self.end.next_plug = None

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

