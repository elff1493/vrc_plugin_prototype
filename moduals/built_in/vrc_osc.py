from nodes import Node
from moduals.moduals import Module, Result
osc = Module("vrc_osc")


@osc.register
class Send(Node):
    op_name = "send"
    inputs = ("data", "address")
    outputs = ()
    description = "send data to the given address "

    def eval(self, data):
        out = data["a"] + data["b"]
        return Result()


@osc.register
class Receive(Node):
    op_name = "receive"
    inputs = ("address",)
    outputs = ("data",)
    description = "receive osc data from default osc connection "

    def eval(self, data):
        out = data["a"] + data["b"]
        return Result(data=out)

    def update(self):
        pass