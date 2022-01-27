from enum import Enum
from typing import Dict

from client.Firewall import Firewall


class ServerType(Enum):
    STREAMING = "choghondar"
    CHAT = "shalgham"


class Menu:
    parent: Menu
    sub_menus: Dict[int, Menu]
    name: str

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def show(self):
        return self

    def execute(self):
        return self


class MainMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "")
        self.sub_menus = {1: ConnectToExternalServerMenu(self),
                          2: AdminMenu(self),
                          }


class ConnectToExternalServerMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Connect to external servers")
        self.sub_menus = {
            str(ServerType.STREAMING.value): StreamingMenu(self),
            str(ServerType.CHAT.value): UserMenu(self)}


class StreamingMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "")
        self.sub_menus = {}
        self.get_video_names()


class UserMenu(Menu):
    pass


class AdminMenu(Menu):
    pass


class SignUpMenu(Menu):
    pass


class LoginMenu(Menu):
    pass


class MailMenu(Menu):
    pass


class ChatMenu(Menu):
    pass


class Client:
    admin_pass: str
    firewall: Firewall

    def __init__(self):
        MainMenu().show().execute()

    # def read_client_metadata(self):
    #     pass
    #
    # def save_client_metadata(self):
    #     pass


client: Client = Client()
