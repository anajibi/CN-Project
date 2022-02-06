import json
import socket
from enum import Enum
from typing import Dict

from Firewall import Firewall, ControlledSocket


def tcp_send_data(data: dict, ip, port):
    data = json.dumps(data)
    with ControlledSocket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(bytes(data, encoding='utf-8'))
        message = s.recv(1024).decode('utf-8')
        response = json.loads(message)
    return response


class Menu:
    parent: any  # any: Menu
    sub_menus: Dict[str, any]  # any: Menu
    name: str
    firewall: Firewall

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.sub_menus = {}
        self.proxy_port = -1
        self.chat_port = 3030
        self.streaming_info_port = 4030
        self.streaming_port = 4031

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

    def get_chat_port(self):
        if self.proxy_port == -1:
            return self.chat_port
        return self.proxy_port

    def get_streaming_info_port(self):
        if self.proxy_port == -1:
            return self.streaming_info_port
        return self.proxy_port

    def get_streaming_port(self):
        if self.proxy_port == -1:
            return self.streaming_port
        return self.proxy_port

    def __str__(self):
        return self.name


class ServerType(Enum):
    STREAMING = "choghondar"
    CHAT = "shalgham"
