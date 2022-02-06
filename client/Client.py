from enum import Enum
import json
import socket

from client.Firewall import Firewall
from client.menu.ChatMenu import ChatMenu


def udp_send_data(data: dict):
    data = json.dumps(data)


class Client:
    admin_pass: str
    firewall: Firewall

    def __init__(self):
        # MainMenu(None).run()
        ChatMenu(None).run()


client: Client = Client()
