from enum import Enum
import json
import socket
from typing import Dict, List

from client.Firewall import Firewall


class ServerType(Enum):
    STREAMING = "choghondar"
    CHAT = "shalgham"


def tcp_send_data(data: dict, ip, port):
    data = json.dumps(data)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        s.sendall(bytes(data, encoding='utf-8'))
        message = s.recv(1024).decode('utf-8')
        response = json.loads(message)
    return response


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
        if not isinstance(self, ChatMenu):
            print(f"0. Back")
        for k, v in self.sub_menus.items():
            print(f"{k}. {v}")
        return self

    def input_valid(self, chosen_menu: str):
        if isinstance(self, ChatMenu) and chosen_menu == '0':
            return False
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

    def udp_send_data(self, data: dict):
        data = json.dumps(data)

    def __str__(self):
        return self.name


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
            str(ServerType.CHAT.value): ChatMenu(self)}


class StreamingMenu(Menu):
    def __init__(self, parent):
        print("Welcome to Choghondar.")
        super().__init__(parent, "Streaming Menu")
        # self.get_video_names()


class ChatMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Chat Menu")
        self.sub_menus = {
            "1": SignUpMenu(self),
            "2": LoginMenu(self),
            "3": ExitMenu(self)
        }


class AdminMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Admin Menu")
        self.sub_menus = {

        }


class SignUpMenu(Menu):
    username: str
    password: str

    def __init__(self, parent):
        super().__init__(parent, "Signup")

    def show(self):
        self.username = ""
        self.password = ""
        return self

    def execute(self):
        self.sign_up_procedure()
        self.parent.run()
        return self

    def sign_up_procedure(self):
        self.prompt_username()
        self.prompt_password()
        self.send_user_pass_to_server()

    def is_username_new(self):
        data = {
            'command': 'GET_USER',
            'username': self.username
        }
        response = tcp_send_data(data=data, ip='localhost', port=3030)
        return response['status'] == "OK"  # Todo: Enum

    def is_username_bad(self):
        return (not self.is_username_new()) or self.username == '0'

    def send_user_pass_to_server(self):
        data = {
            'command': 'REGISTER',
            'username': self.username,
            'password': self.password
        }
        response = tcp_send_data(data=data, ip='localhost', port='3030')
        return response == "OK"

    def prompt_username(self):
        print("Please enter your username.")
        while True:
            self.username = input()
            if self.is_username_bad():
                print(
                    "This username is already existed or invalid. Please enter another one.")
            else:
                break

    def prompt_password(self):
        print("Please enter your password.")
        self.password = input()


class LoginMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Login")
        self.sub_menus = {}


class ExitMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Exit")


class MailMenu(Menu):
    def __init__(self, parent):
        super().__init__(parent, "Mail Menu")
        self.sub_menus = {}


class Client:
    admin_pass: str
    firewall: Firewall

    def __init__(self):
        # MainMenu(None).run()
        ChatMenu(None).run()


client: Client = Client()
