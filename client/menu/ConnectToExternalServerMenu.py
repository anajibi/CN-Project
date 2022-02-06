import re

from menu.ChatMenu import ChatMenu
from menu.Menu import Menu, ServerType
from menu.StreamingMenu import StreamingMenu


class ConnectToExternalServerMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Connect to External Servers")

    def show(self):
        print(f"{str(ServerType.STREAMING.value)}: {StreamingMenu(self)}")
        print(f"{str(ServerType.CHAT.value)}: {ChatMenu(self)}")
        return self

    def execute(self):
        command = input()
        while True:
            if command == str(ServerType.STREAMING.value):
                StreamingMenu(self).run()
            elif regexp := re.match(r"shalgham(?: via (\d+))?", command):
                self.proxy_port = int(regexp.group(1))
                ChatMenu(self).run()
            elif command == 0:
                self.parent.run()
