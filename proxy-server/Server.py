# Proxy Input Request Port
import socket
from enum import Enum
from typing import Dict, Tuple

CHAT_PORT = 6060
STREAMING_PORT = 6070

# ChatServer
SERVER_PORT_PUBLISH = 3030

# MediaServer
SERVER_PORT_INFO = 4030


class SockType(Enum):
    TCP = "TCP",
    UDP = "UDP"


class ProxyServer:
    chat: socket.socket
    media_tcp: socket.socket
    media_udp: socket.socket
    forwarding_table: Dict[Tuple[Tuple[str, int], SockType], int]  # (('localhost', 3423), SockType.TCP): 2348

    def __init__(self):
        """
        Calls each handle_client & sets it inside forwarding_table.
        """
        # Similar to MediaServer __init__
        pass

    def set_chat_socket(self, chat_socket: socket):
        pass

    def set_media_tcp_socket(self, media_tcp_socket: socket):
        pass

    def set_media_udp_socket(self, media_udp_socket: socket):
        pass

    def handle_client(self, socket_val: socket):
        pass
