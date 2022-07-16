from PyQt5.QtGui import QIntValidator
from PyQt5.QtQuick import QQuickView
from PyQt5.QtWidgets import QLineEdit

from symbols.symbols import Category, SymbolInput

bools = Category("bools")



@bools.register
class Toggle(SymbolInput):
    full_name = "port input"
    op_name = "toggle"
    default = "0"
    qml_url = "resources/qml/toggle_symbol.qml"

    def get_data(self):
        return self.qml.rootObject().property("position") > 0.5
    def set_data(self, data):
        self.qml.rootObject().setProperty("position", float(data))

