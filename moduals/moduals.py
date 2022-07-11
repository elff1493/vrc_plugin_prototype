

class DuplicateNodeError(Exception):
    pass


class Module:
    libraries = {}

    def __init__(self, name: str):
        if name in Module.libraries:
            raise DuplicateNodeError()
        self.libraries[name] = self
        self.name = name
        self.nodes = {}

    def register(self, node):
        """decrator for class register"""
        if type(node.inputs) is not tuple:
            raise TypeError("node.inputs is not tuple. try ('name',) instead of ('name')")
        if type(node.outputs) is not tuple:
            raise TypeError("")

        if node in self.nodes.values() or node.op_name in self.nodes:
            raise DuplicateNodeError()
        self.nodes[node.op_name] = node
        return node

    def sub_modual(self, name):
        pass # todo add

    @classmethod
    def get_node(cls, full_op_code):
        path = full_op_code.split(".")
        root = Module.libraries
        for i in path:
            root = root[i]
        print(root, full_op_code)
        return root

    def __getitem__(self, item):
        return self.nodes[item]
