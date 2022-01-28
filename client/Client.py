from enum import Enum
from typing import Dict

from client.Firewall import Firewall


class ServerType(Enum):
    STREAMING = "choghondar"
    CHAT = "shalgham"


class Menu:
    parent: any  # any: Menu
    sub_menus: Dict[str, any]  # any: Menu
    name: str

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def show(self):
        """
        Shows Menu Options.
        E.g.:
        1. Login
        2. Signup
        3. Exit
        :return:
        """
        return self

    def execute(self):
        """
        Handles User Input.
        :return:
        """
        return self


class MainMenu(Menu):
    def __init__(self, parent):
        """
        Inherits Menu Class. Only sub_menus & its actions differ.
        Leaf nodes have different implementations.
        :param parent:
        """
        super().__init__(parent, "")
        self.sub_menus = {
            '1': ConnectToExternalServerMenu(self),
            '2': AdminMenu(self)
        }


class ConnectToExternalServerMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Connect to External Servers")
        self.sub_menus = {
            str(ServerType.STREAMING.value): StreamingMenu(self),
            str(ServerType.CHAT.value): UserMenu(self)}


class StreamingMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "")
        self.sub_menus = {}
        # self.get_video_names()


class UserMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "User Menu")
        self.sub_menus = {}


class AdminMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Admin Menu")
        self.sub_menus = {}


class SignUpMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Signup Menu")
        self.sub_menus = {}


class LoginMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Login Menu")
        self.sub_menus = {}


class MailMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Mail Menu")
        self.sub_menus = {}


class ChatMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Chat Menu")
        self.sub_menus = {}


class Client:
    admin_pass: str
    firewall: Firewall

    def __init__(self):
        MainMenu(None).show().execute()


client: Client = Client()
