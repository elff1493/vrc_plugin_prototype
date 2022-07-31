import sys

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
from asyncqt import QEventLoop
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio



class MainApp(QApplication):
    def __init__(self):
        super().__init__([])



        self.window = QMainWindow(None)

        self.butt = QPushButton(self.window)
        self.butt.clicked.connect(self.go)
        self.window.setGeometry(1100, 200, 800, 600)
        self.window.show()

    def go(self):
        print("server made")
        make_server()

def main():
    app = MainApp()
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        sys.exit(loop.run_forever())

def filter_handler(address, *args):
    print(f"{address}: {args}")


def make_server():
    ip = "127.0.0.1"
    port = 6000

    dispatcher = Dispatcher()
    dispatcher.map("/*", filter_handler)

    server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
    end = server.create_serve_endpoint()  # Create datagram endpoint and start serving
    asyncio.ensure_future(end, loop=asyncio.get_event_loop())

main()






