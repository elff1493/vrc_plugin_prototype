from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF, Qt, QMimeData, QByteArray, QDataStream, QIODevice, pyqtProperty, QUrl, QObject
from PyQt5.QtGui import QColor, QPen, QBrush, QTransform, QDrag
from PyQt5.QtQml import QQmlContext
from PyQt5.QtQuick import QQuickView
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import QGraphicsItem, QLabel, QVBoxLayout, QFrame, QHBoxLayout

from wires import Line


class Plug:
    IN = 0
    OUT = 1
    def __init__(self, node, inout=0, index=0, name="unknown plug", _type=None):
        self.node = node
        self.inout = inout
        self.ui_plug = None
        self.ui_symbol_slot = None
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
        self.layout.stretch(10)
        self._inout = 0
        self.inout = inout
        self.setLayout(self.layout)
        self.name = name
        self.contents = None
        self.contents = SymbolInput(self, name)  if not inout else SymbolOutput(self, name)
        self.layout.addWidget(self.contents)
        self.setAutoFillBackground(True)
        self.setAcceptDrops(True)
        #self.show()

    @pyqtProperty(int)
    def inout(self):
        return self._inout

    @inout.setter
    def inout(self, x):
        self._inout = x

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        event.accept()
        super(PlugSlot, self).dragEnterEvent(event)
        print("drag entert")

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent) -> None:
        if event.mimeData().hasFormat("application/x-plug-content"):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, a0: QtGui.QDragLeaveEvent) -> None:
        pass

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        self.contents.setParent(None)
        self.contents: PlugContent = event.source().__class__(self, self.name)
        self.layout.addWidget(self.contents)
        #p = self.mapToScene(event.pos())
        #n.set_pos((p.x(), p.y()))

    def set_content(self, content):
        #self.layout.removeWidget(self.contents)
        self.layout.addWidget(content)


class PlugContent(QFrame):
    full_name = ""
    op_name = ""
    default = None
    qml_url = ""


    def __init__(self, parent, name, showroom=False):
        super(PlugContent, self).__init__(parent=parent)
        self.name = name
        self.showroom = showroom
        self.inside_of = parent
        self.qml = None

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.stretch(10)
        self.setLayout(self.layout)
        w = self.init(self.name)
        self.setAcceptDrops(True)

        if type(w) is not tuple:
            w = (w,)
        for i in w:
            self.layout.addWidget(i)
        if showroom:
            self.setMouseTracking(True)
        if not showroom:
            parent.set_content(self)

    def init(self, text):
        if self.qml_url:
            self.qml = QQuickWidget(self)
            self.qml.setSource(QUrl(self.qml_url))
            return self.qml
        lable = QLabel(self.name)
        lable.setGeometry(0, 100, 100, 100)
        return lable

    def get_data(self):
        raise NotImplementedError()

    def set_data(self, data):
        raise NotImplementedError()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        super(PlugContent, self).mousePressEvent(event)
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

            drag.setHotSpot(event.pos())
            drag.exec_(Qt.MoveAction)
            #paint.end()


class SymbolInput(PlugContent):
    pass


class SymbolOutput(PlugContent):
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
                if l.plug.inout:
                    l = Line(self.plug.node.scene, l.plug, p.plug)
                else:
                    l = Line(self.plug.node.scene, p.plug, l.plug)
                if not l.test_valid():
                    l.remove()
                    print("remove line")
