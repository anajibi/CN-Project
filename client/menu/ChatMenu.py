from menu.ExitMenu import ExitMenu
from menu.LoginMenu import LoginMenu
from menu.Menu import Menu
from menu.SignupMenu import SignupMenu


class ChatMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Chat Menu")
        self.sub_menus = {
            "1": SignupMenu(self),
            "2": LoginMenu(self),
            "3": ExitMenu(self)
        }
