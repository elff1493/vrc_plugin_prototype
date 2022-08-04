

from nodes import Node
from moduals.moduals import Module
from evaluator import Result
import time as t
import datetime as dt

time = Module("time")


@time.register
class TimeStamp(Node):
    full_name = "time stamp now"
    op_name = "timestamp"
    inputs = ()
    outputs = ("timestamp", )
    description = "get the current timestamp"

    def eval(self, data):

        return Result(timestamp=dt.datetime.today().timestamp())


@time.register
class DtToday(Node):
    full_name = "date today"
    op_name = "dt_today"
    inputs = ()
    outputs = ("microsecond", "second", "hour", "minute", "day", "month", "year")
    description = "gets the date and time of the current moment"

    def eval(self, data):
        today = dt.datetime.today()
        return Result(
            microsecond=today.microsecond,
            second=today.second,
            hour=today.hour,
            minute=today.minute,
            day=today.day,
            month=today.month,
            year=today.year
                      )


@time.register
class DtFromStamp(Node):
    full_name = "timestamp to units"
    op_name = "dt_ts"
    inputs = ("timestamp",)
    outputs = ("microsecond", "second", "hour", "minute", "day", "month", "year")
    description = "gets the date and time of the current moment"

    def eval(self, data):
        today = dt.datetime.fromtimestamp(data.timestamp)
        return Result(
            microsecond=today.microsecond,
            second=today.second,
            hour=today.hour,
            minute=today.minute,
            day=today.day,
            month=today.month,
            year=today.year
                      )


@time.register
class DtToStamp(Node):
    full_name = "timestamp from time units"
    op_name = "ts_dt"
    inputs = ("microsecond", "second", "hour", "minute", "day", "month", "year")
    outputs = ("timestamp",)
    description = "get a timestamp from its components"

    def eval(self, data):
        timestamp = dt.datetime(
            microsecond=data.microsecond,
            second=data.second,
            hour=data.hour,
            minute=data.minute,
            day=data.day,
            month=data.month,
            year=data.year).timestamp()

        return Result(timestamp=timestamp)
