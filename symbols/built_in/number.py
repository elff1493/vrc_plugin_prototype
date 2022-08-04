from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QLineEdit, QLabel

from plugs import SymbolInput
from symbols.symbols import Category


number = Category("number")



@number.register
class WholeNumber(SymbolInput):
    full_name = "Whole Number"
    op_name = "whole_num"
    default = "100"

    def init(self, text):
        self.text = QLineEdit()
        self.text.textChanged.connect(lambda: self.on_changed())
        self.text.setValidator(QIntValidator())
        lable = QLabel()
        lable.setText(text)
        lable.setGeometry(0, 100, 100, 100)
        return lable, self.text

    def get_data(self):
        a = self.text.text()
        return int(a)

    def set_data(self, data):
        self.text.setText(str(data))















