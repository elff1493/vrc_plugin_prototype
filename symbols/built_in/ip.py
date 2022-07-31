from PyQt5 import Qt

from plugs import SymbolInput
from symbols.symbols import Category


ip = Category("ip")



@ip.register
class IpAddress(SymbolInput):
    full_name = "ip address"
    op_name = "ip_add"
    default = "127.0.0.1"
    qml_url = "resources/qml/ip_symbol.qml"

    def get_data(self):
        root = self.qml.rootObject().children()
        out = [str(i.property("currentIndex")) for i in root[2:9:2]]
        print(".".join(out))
        return ".".join(out)

    def set_data(self, data):

        root = self.qml.rootObject()
        root = root.children()
        nums = data.split(".")
        root[2].setProperty("currentIndex", nums[0])
        root[4].setProperty("currentIndex", nums[1])
        root[6].setProperty("currentIndex", nums[2])
        root[8].setProperty("currentIndex", nums[3])
