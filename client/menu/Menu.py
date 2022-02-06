import json
import socket
from enum import Enum
from typing import Dict



class Menu:
    parent: any  # any: Menu
    sub_menus: Dict[str, any]  # any: Menu
    name: str

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.sub_menus = {}

    def run(self):
        return self.show().execute()

    def show(self):
        """
        Shows Menu Options.
        E.g.:
        1. Login
        2. Signup
        3. Exit
        :return:
        """
        # if not isinstance(self, ChatMenu):
        #     print(f"0. Back")
        for k, v in self.sub_menus.items():
            print(f"{k}. {v}")
        return self

    def input_valid(self, chosen_menu: str):
        # if isinstance(self, ChatMenu) and chosen_menu == '0':
        #     return False
        if chosen_menu not in self.sub_menus:
            return False
        return True

    def get_parent(self):
        next_menu = self.parent
        if not next_menu:
            exit(0)
        return next_menu

    def execute(self):
        """
        Handles User Input.
        :return:
        """
        chosen_menu = input()
        if not self.input_valid(chosen_menu):
            return self.retry()
        if chosen_menu == '0':
            next_menu = self.get_parent()
        else:
            next_menu = self.sub_menus.get(chosen_menu)
        assert isinstance(next_menu, Menu)
        next_menu.run()
        return self

    def retry(self):
        print("Bad input. Try again.")
        return self.run()

    def __str__(self):
        return self.name

def tcp_send_data(data: dict, ip, port):
    data = json.dumps(data)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(bytes(data, encoding='utf-8'))
        message = s.recv(1024).decode('utf-8')
        response = json.loads(message)
    return response

class ServerType(Enum):
    STREAMING = "choghondar"
    CHAT = "shalgham"

