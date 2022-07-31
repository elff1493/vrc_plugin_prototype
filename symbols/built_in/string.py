from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QCompleter

from plugs import SymbolInput
from symbols.symbols import Category

text = Category("text")

@text.register
class TextBasic(SymbolInput):
    full_name = "text line"
    op_name = "text_line"
    default = "test"
    def init(self, text):
        self.text = QLineEdit()
        lable = QLabel()
        lable.setText(text)
        lable.setGeometry(0, 100, 100, 100)
        return lable, self.text

    def get_data(self):

        return self.text.text()

    def set_data(self, data):
        self.text.setText(str(data))


@text.register
class PortNumber(SymbolInput):
    full_name = "port input"
    op_name = "port"
    default = "6000"
    def init(self, text):

        self.text = QLineEdit()
        self.text.textChanged.connect(lambda: self.on_changed())
        self.text.setValidator(QIntValidator(0, 65535))
        lable = QLabel()
        lable.setText(text)
        lable.setGeometry(0, 100, 100, 100)
        return lable, self.text

    def get_data(self):
        return self.text.text()

    def set_data(self, data):
        self.text.setText(data)


@text.register
class TextNumber(SymbolInput):
    full_name = "number input"
    op_name = "line_num"
    default = "0"

    def init(self, text):
        self.text = QLineEdit()
        self.text.textChanged.connect(lambda: self.on_changed())
        self.text.setValidator(QDoubleValidator())
        lable = QLabel()
        lable.setText(text)
        lable.setGeometry(0, 100, 100, 100)
        return lable, self.text

    def get_data(self):
        return float(self.text.text())

    def set_data(self, data):
        self.text.setText(data)

input_osc_endpoints = [
    "/input/MoveForward",
    "/input/MoveBackward",
    "/input/MoveLeft",
    "/input/MoveRight",
    "/input/LookLeft",
    "/input/LookRight",
    "/input/LookDown",
    "/input/LookUp",
    "/input/Jump",
    "/input/Run",
    "/input/Back",
    "/input/Menu",
    "/input/ComfortLeft",
    "/input/ComfortRight",
    "/input/DropRight",
    "/input/UseRight",
    "/input/GrabRight",
    "/input/DropLeft",
    "/input/UseLeft",
    "/input/UseRight",
    "/input/GrabLeft",
    "/input/PanicButton",
    "/input/QuickMenuToggleLeft",
    "/input/QuickMenuToggleRight",
    "/input/ToggleSitStand",
    "/input/AFKToggle"
]
class LineEdit(QLineEdit):
    def __init__(self, callback):
        super(LineEdit, self).__init__()
        self.textChanged.connect(lambda: self.test())
@text.register
class OscPath(SymbolInput):
    full_name = "osc path"
    op_name = "osc_path"
    default = "/"

    def init(self, text):
        self.text = QLineEdit()
        self.text.textChanged.connect(lambda: self.on_changed())
        comp = QCompleter(input_osc_endpoints, self.text)
        self.text.setWindowFlags(Qt.BypassGraphicsProxyWidget)  # sets the right suggestion pos
        self.text.setCompleter(comp)
        lable = QLabel()
        lable.setText(text)
        lable.setGeometry(0, 100, 100, 100)
        return lable, self.text

    def get_data(self):
        return self.text.text()

    def set_data(self, data):
        self.text.setText(data)


