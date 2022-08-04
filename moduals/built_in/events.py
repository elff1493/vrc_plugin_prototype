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
    inputs = ("toggle", "rate")
    outputs = ("tick",)
    input_slots = {
        "toggle":"bools.toggle",
        "rate": "number.whole_num"
    }
    description = "even node click eval the node dag (debuging node)"
    tick = 0

    def __init__(self, *args, showroom=False, **kwargs):
        self.timer = QTimer()
        super(Tick, self).__init__(*args, showroom=showroom, **kwargs)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.spawn_event)
        #timer.start()

        if showroom:
            self.timer.disconnect()

    def spawn_event(self):
        self.e.eval(self)

    def symbol_changed(self):
        print(self.get_symbol_data(0), self.get_symbol_data(1))
        self.timer.setInterval(int(self.get_symbol_data(1) or 100))
        if self.get_symbol_data(0):
            self.timer.start()
        else:
            self.timer.stop()

    def eval(self, data):
        if data.toggle:
            if not self.timer.isActive():
                self.timer.start()
            self.tick += 1
        else:
            self.timer.stop()
        return Result(tick=self.tick)
