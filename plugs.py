from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QRectF, Qt, QMimeData, QByteArray, QDataStream, QIODevice, pyqtProperty, QUrl, QObject
from PyQt5.QtGui import QColor, QPen, QBrush, QTransform, QDrag
from PyQt5.QtQml import QQmlContext
from PyQt5.QtQuick import QQuickView
from PyQt5.QtQuickWidgets import QQuickWidget
from PyQt5.QtWidgets import QGraphicsItem, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QLayout

from symbols.symbols import Category
from wires import Line


class Plug:
    IN = 0
    OUT = 1
    def __init__(self, node, inout=0, index=0, name="unknown plug", _type=None, interface=""):
        self.node = node
        self.inout = inout
        self.ui_plug = UiPlug(self.node.ui_node, self)

        self.type = _type
        self.name = name

        self.padding = 20
        self.index = index
        self.next_plug = None
        self.line = None
        self.symbol = None
        if inout:
            symbol = node.__class__.output_slots.get(name, "")
        else:
            symbol = node.__class__.input_slots.get(name, "")

        self.ui_symbol_slot = PlugSlot(self.node.ui_node.content, self, inout=inout, content=symbol)
        self.node.ui_node.add_ui_plug(self.ui_plug, self.ui_symbol_slot)

    def set_line(self, line=None):
        if self.line:
            self.line.remove()
        self.line = line

    def get_pos(self):
        return self.ui_plug.scenePos()


class PlugSlot(QFrame):
    IN = 0
    OUT = 1
    def __init__(self, parent, plug, inout=IN, content=""):
        super(PlugSlot, self).__init__()
        self.layout = QVBoxLayout()
        self.layout.setSizeConstraint(QLayout.SetFixedSize)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.stretch(10)
        self._inout = inout
        self.inout = inout
        self.setLayout(self.layout)
        self.plug = plug
        self.name = plug.name
        self.contents = None

        if content:
            sym = Category.get_symbol(content)
            if sym:
                self.set_content(sym(self, plug.name))
                if not (sym.default is None):
                    self.contents.set_data(sym.default)
            else:
                self.set_content(SymbolInput(self, plug.name) if not inout else SymbolOutput(self, plug.name))
        else:
            self.set_content(SymbolInput(self, plug.name) if not inout else SymbolOutput(self, plug.name))
        self.layout.addWidget(self.contents)
        self.setAutoFillBackground(True)
        self.setAcceptDrops(True)

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
        self.layout.removeWidget(self.contents)
        self.contents = content
        self.layout.addWidget(content)

    def update_plug_pos(self, w):
        x = w
        y = abs(self.pos().y() + self.plug.node.ui_node.proxy.pos().y())
        self.plug.ui_plug.setPos(x if self._inout else 0, y)



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

            self.qml.rootContext().setContextProperty("symbol_name", self.name)
            self.qml.setResizeMode(1)
            self.qml.setSource(QUrl(self.qml_url))
            if self.qml.errors():
                raise Exception(self.qml.errors()[0].toString())
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

        #self.plug.node.ui_node.plugs.append(self)
        # self.anchor = anchor
        # self.setPos(*anchor)
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
            p: UiPlug = self.scene().itemAt(*p, QTransform())
            if type(p) is UiPlug:
                if l.plug.inout:
                    l = Line(self.plug.node.scene, l.plug, p.plug)
                else:
                    l = Line(self.plug.node.scene, p.plug, l.plug)
                if not l.test_valid():
                    l.remove()
                    print("remove line")
