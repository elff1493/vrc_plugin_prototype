from nodes import Node
from moduals.moduals import Module
from evaluator import Result

const = Module("consts")


@const.register
class Const(Node):
    full_name = "symbol const"
    op_name = "sym_const"
    inputs = ("symbol",)
    input_slot = {
        "data1": "text.text_line"
    }
    outputs = ("value", )
    description = "when you want a node input instead of a symbol"

    def eval(self, data):

        return Result(value=data.symbol)


@const.register
class Split(Node): # todo have nodes do this by defult , but for now, this
    full_name = "data Split"
    op_name = "data_split"
    inputs = ("data", )

    outputs = ("output1", "output2")
    description = "takes an input and duplicates it"

    def eval(self, data):
        return Result(output1=data.data, output2=data.data)
