from client.Client import ServerType, StreamingMenu, ChatMenu
from client.menu.Menu import Menu


class ConnectToExternalServerMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Connect to External Servers")
        self.sub_menus = {
            str(ServerType.STREAMING.value): StreamingMenu(self),
            str(ServerType.CHAT.value): ChatMenu(self)}
