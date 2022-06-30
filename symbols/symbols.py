

class DuplicateSymbolError(Exception):
    pass


class Category:
    group = {}

    def __init__(self, name: str):
        if name in Category.group:
            raise DuplicateSymbolError()
        self.group[name] = self
        self.name = name
        self.symbols = {}

    def register(self, symbol):
        """decrator for class register"""
        if symbol in self.symbols.values() or symbol.op_name in self.symbols:
            raise DuplicateSymbolError()
        self.symbols[symbol.op_name] = symbol
        return symbol

    def sub_group(self, name):
        pass # todo add

    @classmethod
    def get_symbol(cls, full_op_code):
        path = full_op_code.split(".")
        root = Category.group
        for i in path:
            if i not in root:
                return None
            root = root[i]
        #print(root, full_op_code)
        return root
    def __contains__(self, item):
        return item in self.group
    def __getitem__(self, item):
        return self.symbols[item]
