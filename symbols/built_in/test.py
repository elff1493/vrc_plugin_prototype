from PyQt5.QtWidgets import QLineEdit, QLabel

from symbols.symbols import Category
from plugs import SymbolInput
test = Category("test")

@test.register
class Test(SymbolInput):
    full_name = "test input"
    op_name = "test"

    def init(self, text):
        self.text = QLineEdit()
        lable = QLabel()
        lable.setText("banaa")
        return self.text, lable

    def get_data(self):
        return self.text.text()
