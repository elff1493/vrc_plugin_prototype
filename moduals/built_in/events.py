from PyQt5.QtCore import QTimer, QTime

from nodes import Node
from moduals.moduals import Module
from evaluator import Result
events = Module("events")


@events.register
class OnClick(Node):
    full_name = "on click"
    op_name = "click"
    inputs = ("do_tick",)
    outputs = ("tick",)
    input_slots = {"do_tick": "bools.toggle"
                   }
    description = "even node click eval the node dag (debuging node)"
    tick = 0

    def eval(self, data):
        if data.do_tick:
            self.tick += 1
        else:
            self.tick = 0

        return Result(tick=self.tick)

    def click(self):
        self.e.eval(self)

@events.register
class Tick(Node):
    full_name = "on tick"
    op_name = "tick"
    inputs = ("toggle",)
    outputs = ("tick",)
    input_slots = {
        "toggle":"bools.toggle"
    }
    description = "even node click eval the node dag (debuging node)"
    tick = 0

    def __init__(self, *args, showroom=False, **kwargs):
        super(Tick, self).__init__(*args, showroom=showroom, **kwargs)
        self.timer = None
        if not showroom:
            timer = QTimer()
            timer.setInterval(100)
            timer.timeout.connect(self.spawn_event)
            timer.start()
            self.timer = timer

    def spawn_event(self):
        self.e.eval(self)

    def eval(self, data):
        if data.toggle:
            if not self.timer.isActive():
                self.timer.start()
            self.tick += 1
        else:
            self.timer.stop()
        return Result(tick=self.tick)
