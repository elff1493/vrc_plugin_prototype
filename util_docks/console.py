
from PyQt5.QtWidgets import QDockWidget, QLabel, QScrollArea


class ConsoleContent(QScrollArea):
    def __init__(self):
        super(ConsoleContent, self).__init__()
        self.text = QLabel()
        self.setWidget(self.text)
        self.setWidgetResizable(True)


class Console(QDockWidget):
    default = None

    def __init__(self):
        super(Console, self).__init__("Console")
        if not self.__class__.default:
            self.__class__.default = self

        self.content = ConsoleContent()
        self.setWidget(self.content)

        self.setFloating(False)
        self.setVisible(False)

    def print(self, text, end="\n"):
        self.content.text.setText(self.content.text.text() + str(text) + end)
        self.content.text.update()
        self.content.text.repaint()

    @classmethod
    def instance(cls):
        if not cls.default:
            cls.default = Console()
        return cls.default
