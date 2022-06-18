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




