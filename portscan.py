import psutil
import os

from PyQt5.QtGui import QIcon

import get_icon
from dataclasses import dataclass

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