import win32ui
import win32gui
import win32con
import win32api

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import pywintypes
from PyQt5.QtWinExtras import QtWin

ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

SIZE = 64
cash = {}
def get_icon(path):
    if path in cash:
        return cash[path]
    all_icons = None
    try:
        if path:
            large, small = win32gui.ExtractIconEx(path, 0)
            all_icons = large + small
    except pywintypes.error as e:
        print(e, type(e), path)

    if not all_icons:
        if "" not in cash.keys():
            cash[""] = QIcon.fromTheme("text-x-generic"), False
        return cash[""]

    data = QtWin.fromHICON(all_icons[0])
    if data.width() > SIZE:
        data = data.scaled(SIZE, SIZE, transformMode=Qt.SmoothTransformation)

    for i in all_icons:
        win32gui.DestroyIcon(i)

    cash[path] = QIcon(data), True
    return cash[path]

if __name__ == '__main__':
    get_icon("D:\Program Files (x86)\osu!\osu!.exe")