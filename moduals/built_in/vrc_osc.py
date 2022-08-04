import re

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer, AsyncIOOSCUDPServer

from evaluator import Result
from nodes import Node
from moduals.moduals import Module

import psutil
from os import getenv
from pathlib import Path
import json
import asyncio
import pythonosc

from pythonosc.udp_client import SimpleUDPClient

osc = Module("vrc_osc")


class OscManager:
    obj = None

    def __init__(self):
        self.servers = {}  # key : (addr, port)
        self.clients = {}
        self.nodes = {}

    @classmethod
    def instance(cls):
        if cls.obj:
            return cls.obj
        cls.obj = OscManager()
        return cls.obj

    def get_default_address(self):  # todo untested
        vrc = filter(lambda p: p.name == "vrchat.exe", psutil.process_iter())

    def add_lissner(self, addr, port):
        pass

    def send(self, type, add, ip, port, data):
        if (ip, port) not in self.servers:
            c = SimpleUDPClient(ip, int(port))
            self.clients[(ip, port)] = c
        c = self.clients[(ip, port)]
        c.send_message(add, float(data) if type == "f" else int(data))

    def handler(self, addr, args, *data):
        print("called")
        node, ip, port = args
        server = self.servers.get((ip, port))
        if not server:
            return

        nodes = None
        escaped_address_pattern = re.escape(addr)
        pattern = escaped_address_pattern.replace('\\?', '\\w?')

        pattern = pattern.replace('\\*', '[\w|\+]*')
        pattern = pattern + '$'
        patterncompiled = re.compile(pattern)

        for ad, val in server[2].items():
            if (patterncompiled.match(ad) or (('*' in ad) and re.match(ad.replace('*', '[^/]*?/*'), addr))):
                nodes = val
                break
        if not nodes:
            return
        for i in nodes:
            i.buffer = data[0]
        if nodes:
            nodes[0].e.eval(nodes[0]) # todo add multi eval to evaluator

    def register(self, node, addr, ip, port):
        port = int(port)
        print("regitser")
        if not addr:
            return
        if node in self.nodes:
            d, h, _ = self.nodes[node]
            if h.args == (node, ip, port):
                return
            else:
                print("unmap", h)
                d.unmap(self.nodes[node][2], h)

        if not ip or not port:
            print("no ip or port")
            return


        if (ip, port) not in self.servers:
            print("start serve")
            dispatcher = Dispatcher()
            #dispatcher.set_default_handler(lambda: print("defult test"))
            loop = asyncio.get_event_loop()
            server = AsyncIOOSCUDPServer((ip, port), dispatcher, loop)
            self.servers[(ip, port)] = (dispatcher, server, {}) # k:v, addr:[node]

            asyncio.ensure_future(server.create_serve_endpoint(), loop=loop)

            print("serving")

        dispatcher, server, conn = self.servers[(ip, port)]

        hand = dispatcher.map(addr, self.handler, node, ip, port)

        print(addr, "mapped")

        self.nodes[node] = (dispatcher, hand, addr)

        if addr not in conn:
            conn[addr] = []

        conn[addr].append(node)



class AvatarParm:
    def __init__(self, name,
                 input_address=None, output_address=None,
                 output_type=None, input_type=None):

        self.name = name
        self.input_address = input_address
        self.output_address = output_address
        self.output_type = output_type
        self.input_type = input_type

    @classmethod
    def from_json(cls, data):
        name = data["name"]
        kargs = {}
        if "input" in data:
            kargs["input_address"] = data["input"]["address"]
            kargs["input_type"] = data["input"]["type"]
        if "output" in data:
            kargs["output_address"] = data["output"]["address"]
            kargs["output_type"] = data["output"]["type"]

        return AvatarParm(name, **kargs)


class VrcAvatar:
    def __init__(self, _id, name, parameters):
        self.name = name
        self.parameters = parameters
        self.id = _id

    @classmethod
    def from_path(cls, path):
        with open(path, "r", encoding='utf-8-sig') as file:
            data = json.load(file)

        par = data["parameters"]
        return VrcAvatar(data["id"], data["name"], [AvatarParm.from_json(i) for i in par])


def get_avatars():
    output = []
    p = Path(getenv('APPDATA')).parents[0] / "LocalLow\VRChat\VRChat\OSC"
    if not p.exists():
        print("osc not init")
    for f in p.iterdir():
        first_user = f
        break
    else:
        return
    for f in (first_user / "Avatars").iterdir():
        print("avatatr", f)
        output.append(VrcAvatar.from_path(f))
    return output



@osc.register
class SendF(Node):
    full_name = " send float"
    op_name = "sendf"
    inputs = ("data", "address", "ip", "port")
    outputs = ()
    input_slots = {"address": "text.osc_path",
                   "port": "text.port",
                   "ip": "ip.ip_add"
                   }
    description = "send float to the given address "
    osc: OscManager = OscManager

    def eval(self, data):
        self.osc.instance().send("f", data["address"], data["ip"], data["port"], data["data"])

        return Result()


@osc.register
class SendI(Node):
    full_name = "send int"
    op_name = "sendi"
    inputs = ("data", "address", "ip", "port")
    outputs = ()
    input_slots = {"address": "text.osc_path",
                   "port": "text.port",
                   "ip": "ip.ip_add"
                   }
    description = "send integer to the given address "

    def eval(self, data):
        self.osc.instance().send("i", data["address"], data["ip"], data["port"], int(data["data"]))

        return Result()


@osc.register
class ReceiveI(Node):
    full_name = "receive integer"
    op_name = "receivei"
    inputs = ("address", "ip", "port")
    outputs = ("data",)
    input_slots = {"address": "text.osc_path",
                   "port": "text.port",
                   "ip": "ip.ip_add"
                   }
    description = "receive osc int from default osc connection "
    osc: OscManager = OscManager

    def __init__(self, *args, **kwargs):
        super(ReceiveI, self).__init__(*args, **kwargs)
        self.buffer = 0

    def eval(self, data):
        return Result(data=self.buffer)

    def symbol_changed(self):
        o = self.osc.instance()
        if type(self.inputs[0]) is not str:
            o.register(self,
                       *(self.inputs[i].ui_symbol_slot.contents.get_data() or self.inputs[i].last_data for i in range(3)))

    def update(self):
        pass


@osc.register
class ReceiveF(Node):
    full_name = "receive float"
    op_name = "receivef"
    inputs = ("address", "ip", "port")
    outputs = ()
    input_slots = {"address": "text.osc_path",
                   "port": "text.port",
                   "ip": "ip.ip_add"
                   }
    description = "receive osc float from default osc connection "
    osc: OscManager = OscManager

    def __init__(self, *args, **kwargs):
        super(ReceiveF, self).__init__(*args, **kwargs)
        self.buffer = 0

    def eval(self, data):
        return Result(data=self.buffer)

    def symbol_changed(self):
        o = self.osc.instance()
        if type(self.inputs[0]) is not str:
            o.register(self,
                       *(self.inputs[i].ui_symbol_slot.contents.get_data() or self.inputs[i].last_data for i in
                         range(3)))
    def update(self):
        pass


if __name__ == "__main__":
    get_avatars()
