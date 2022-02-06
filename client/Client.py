from enum import Enum
import json
import socket

from Firewall import Firewall, FirewallType, ControlledSocket
from menu.ChatMenu import ChatMenu
from menu.MainMenu import MainMenu

ControlledSocket.firewall = Firewall(FirewallType.BLACK_LIST)

def udp_send_data(data: dict):
    data = json.dumps(data)


class Client:

    admin_pass: str
    firewall: Firewall

    def __init__(self):
        MainMenu(None).run()
        # ChatMenu(None).run()


client: Client = Client()
