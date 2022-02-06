import re

from client.menu.ChatMenu import ChatMenu
from client.menu.Menu import Menu, ServerType
from client.menu.StreamingMenu import StreamingMenu


class ConnectToExternalServerMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Connect to External Servers")

    def show(self):
        print(f"{str(ServerType.STREAMING.value)}: {StreamingMenu(self)}")
        print(f"{str(ServerType.CHAT.value)}: {ChatMenu(self)}")

    def execute(self):
        command = input()
        while True:
            if command == str(ServerType.STREAMING.value):
                StreamingMenu(self).run()
            elif regexp := re.match(r"shalgham(?: via (\d+))?", command):
                self.proxy_port = int(regexp.group(1))
