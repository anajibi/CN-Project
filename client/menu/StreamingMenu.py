from client.menu.Menu import Menu


class StreamingMenu(Menu):
    def __init__(self, parent):
        print("Welcome to Choghondar.")
        super().__init__(parent, "Streaming Menu")
        # self.get_video_names()
