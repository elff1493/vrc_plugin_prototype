from nodes import Node
from moduals.moduals import Module
from evaluator import Result
events = Module("events")


@events.register
class OnClick(Node):
    full_name = "on click"
    op_name = "click"
    inputs = ()
    outputs = ("tick",)
    description = "even node click eval the node dag (debuging node)"
    tick = 0

    def eval(self, data):
        self.tick += 1
        return Result(tick=self.tick)




