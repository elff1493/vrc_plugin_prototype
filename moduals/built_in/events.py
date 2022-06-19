from PyQt5.QtCore import QTimer, QTime

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

    def click(self):
        print("click")
        self.e.eval(self)

@events.register
class Tick(Node):
    full_name = "on tick"
    op_name = "tick"
    inputs = ()
    outputs = ("tick",)
    description = "even node click eval the node dag (debuging node)"
    tick = 0
    def __init__(self, *args, **kwargs):
        super(Tick, self).__init__(*args, **kwargs)
        timer = QTimer()
        timer.setInterval(100)
        timer.timeout.connect(self.spawn_event)
        timer.start()
        self.timer = timer

    def spawn_event(self):
        self.e.eval(self)

    def eval(self, data):
        self.tick += 1
        return Result(tick=self.tick)
