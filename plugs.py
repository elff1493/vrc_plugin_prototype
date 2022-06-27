from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF, Qt, QMimeData, QByteArray, QDataStream, QIODevice, pyqtProperty
from PyQt5.QtGui import QColor, QPen, QBrush, QTransform, QDrag, QPixmap, QPainter
from PyQt5.QtWidgets import QGraphicsItem, QWidget, QStyleOptionGraphicsItem, QLabel, QVBoxLayout, QFrame

from wires import Line


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
        self.next_plug = None
        self.line = None
        self.symbol = None

    def set_line(self, line=None):
        if self.line:
            self.line.remove()
        self.line = line

    def get_pos(self):
        return self.ui_plug.scenePos()


class PlugSlot(QFrame):
    IN = 0
    OUT = 1
    def __init__(self, parent, name, inout=IN):
        super(PlugSlot, self).__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self._inout = 0
        self.inout = inout
        self.setLayout(self.layout)
        self.contents = PSymbolInput(self, name)  if not inout else PSymbolOutput(self, name)
        self.layout.addWidget(self.contents)
        self.setAutoFillBackground(True)
        #self.show()

    @pyqtProperty(int)
    def inout(self):
        return self._inout

    @inout.setter
    def inout(self, x):
        self._inout = x

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        event.accept()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasFormat("application/x-plug-content"):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, a0: QtGui.QDragLeaveEvent) -> None:
        pass

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        n: PlugContent = event.source().__class__()
        #p = self.mapToScene(event.pos())
        #n.set_pos((p.x(), p.y()))


class PlugContent(QWidget):
    full_name = ""
    op_name = ""
    def __init__(self, parent, name, showroom=False):
        super(PlugContent, self).__init__(parent=parent)
        self.name = name
        self.showroom = showroom
        self.inside_of = parent
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        w = self.init()
        self.layout.addWidget(w)

    def init(self):
        lable = QLabel(self.name)
        lable.setGeometry(0, 100, 100, 100)
        return lable

    def get_data(self):
        return ""

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super(PlugContent, self).mousePressEvent(event)
        print("clickd")
        if event.button() == Qt.LeftButton and self.showroom:
            print("drag start")
            drag = QDrag(self)
            mime = QMimeData()
            data = QByteArray()
            streem = QDataStream(data, QIODevice.WriteOnly)  # todo add importan data to strem

            mime.setData("application/x-plug-content", data)
            drag.setMimeData(mime)

            #image = QPixmap(self.boundingRect().size().toSize())
            #paint = QPainter()
            #paint.begin(image)
            #self.paint(paint, QStyleOptionGraphicsItem()) #todo add icon
            #for i in self.childItems():
            #    i.paint(paint, QStyleOptionGraphicsItem(), None)
            #drag.setPixmap(image)
            drag.setHotSpot(event.pos().toPoint())
            drag.exec_(Qt.MoveAction)
            #paint.end()


class SymbolInput(PlugContent):
    pass


class PSymbolInput(SymbolInput):
    pass


class SymbolOutput(PlugContent):
    pass

class PSymbolOutput(PlugContent):
    pass


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
                print("line")
                if l.plug.inout:
                    l = Line(self.plug.node.scene, l.plug, p.plug)
                else:
                    l = Line(self.plug.node.scene, p.plug, l.plug)
                if not l.test_valid():
                    l.remove()
                    print("remove line")
