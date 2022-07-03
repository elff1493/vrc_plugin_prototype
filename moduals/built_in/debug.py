from nodes import Node
from moduals.moduals import Module
from evaluator import Result
debug = Module("debug")


@debug.register
class Print(Node):
    full_name = "print"
    op_name = "print"
    inputs = ("data",)
    outputs = ()
    description = "print input to consle"

    def eval(self, data):
        print(data["data"])
        return Result()


@debug.register
class SymbolTest(Node):
    full_name = "symbol tester"
    op_name = "symbol_test"
    inputs = ("data1", "data2", "data3")
    input_slot = {
        "data1":"test.test"
    }
    outputs = ("output1", "output2")
    description = "tests symbol input"

    def eval(self, data):
        print(data.data1, data.data2, data.data3, "data inputs")
        out = Result()
        out.output1 = data.data1 + data.data2 + data.data3
        out.output2 = "output2"
        return out

@debug.register
class SymbolToNode(Node):
    full_name = "symbol to node"
    op_name = "symbol_to_node"
    inputs = ("symbol",)
    input_slots = {
        "symbol":"test.test"
    }
    outputs = ("output",)
    description = "tests geting sybol data"

    def eval(self, data):
        return Result(output=data.symbol)



