

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
        if node in self.nodes.values() or node.op_name in self.nodes:
            raise DuplicateNodeError()
        self.nodes[node.op_name] = node
        return node

    def sub_modual(self, name):
        pass # todo add


class Result:
    def __init__(self, *args, exception=False, **kwargs):
        self.output = kwargs
        self.exception = exception
