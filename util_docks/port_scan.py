from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QDockWidget, QTableWidget, QLabel, QTableWidgetItem

import psutil

from PyQt5.QtGui import QIcon

import get_icon
from dataclasses import dataclass

import ctypes
myappid = 'mycompany.myproduct.subproduct.version'  # fix for icon
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

@dataclass
class NetworkItem:
    custom_icon: bool
    name: str
    icon: QIcon
    port: int
    addr: str
    local: bool
    status: str


def get_scan():
    output = []
    for i in psutil.net_connections():
        try:
            prosses = psutil.Process(i.pid)
            icon, is_custom = get_icon.get_icon(prosses.exe())
            data = NetworkItem(name=prosses.name(),
                               icon=icon,
                               custom_icon=is_custom,
                               addr=i.laddr[0],
                               port=i.laddr[1],
                               local=bool(i.raddr),
                               status=i.status
                               )
        except psutil.AccessDenied:
            data = NetworkItem(name="unknown",
                               custom_icon=False,
                               icon=get_icon.get_icon("")[0],
                               addr=i.laddr[0],
                               port=i.laddr[1],
                               local=bool(i.raddr),
                               status=i.status
                               )
        output.append(data)
    return output


class PortScan(QDockWidget):
    def __init__(self):
        super(PortScan, self).__init__("port scan")
        self.table = QTableWidget()
        self.setWidget(self.table)
        self.setFloating(False)
        self.setVisible(False)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.reset()

    def reset(self):
        scan = get_scan()
        scan = sorted(scan, key=lambda x: x.custom_icon, reverse=True)
        self.table.setRowCount(len(scan))
        self.table.setColumnCount(6)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.table.setHorizontalHeaderLabels(["app", "app name", "port", "address", "status", "is local"])

        for i, s in enumerate(scan):
            lab = QLabel()
            lab.setPixmap(s.icon.pixmap(QSize(64, 64)))
            lab.setAlignment(Qt.AlignHCenter)
            self.table.setCellWidget(i, 0, lab)
            self.table.setItem(i, 1, QTableWidgetItem(s.name))
            self.table.setItem(i, 2, QTableWidgetItem(str(s.port)))
            self.table.setItem(i, 3, QTableWidgetItem(s.addr))
            self.table.setItem(i, 4, QTableWidgetItem(s.status))
            self.table.setItem(i, 5, QTableWidgetItem("local" if s.local else "remote"))
