from enum import Enum
import json
import socket

from client.Firewall import Firewall
from client.menu.ChatMenu import ChatMenu


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


def udp_send_data(data: dict):
    data = json.dumps(data)


class Client:
    admin_pass: str
    firewall: Firewall

    def __init__(self):
        # MainMenu(None).run()
        ChatMenu(None).run()


client: Client = Client()
