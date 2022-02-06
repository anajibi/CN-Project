from client.menu.AdminMenu import AdminMenu
from client.menu.ConnectToExternalServerMenu import ConnectToExternalServerMenu
from client.menu.Menu import Menu


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
