from PyQt5.QtWidgets import QLineEdit

from symbols.symbols import Category
from plugs import PSymbolInput
test = Category("test")

@test.register
class Test(PSymbolInput):
    full_name = "test input"
    op_name = "test"
    def init(self):
        self.text = QLineEdit()
        return self.text

    def get_data(self):
        return self.text.text()
