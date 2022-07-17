from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QLabel, QLineEdit

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
        lable.setText(text + " test")
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
        self.text.setValidator(QDoubleValidator())
        lable = QLabel()
        lable.setText(text)
        lable.setGeometry(0, 100, 100, 100)
        return lable, self.text

    def get_data(self):
        return float(self.text.text())

    def set_data(self, data):
        self.text.setText(data)









