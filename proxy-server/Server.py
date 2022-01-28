# Proxy Input Request Port
import socket
import threading
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


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class ProxyServer:
    chat: socket.socket
    media_tcp: socket.socket
    media_udp: socket.socket
    forwarding_table: Dict[Tuple[Tuple[str, int], SockType], int]  # (('localhost', 3423), SockType.TCP): 2348

    def __init__(self):
        """
        Sets 3 sockets. Listens.
        Calls each handle_client & sets it inside forwarding_table.
        """
        # Similar to MediaServer __init__
        self.accept_chat()
        self.accept_media_tcp()
        self.accept_media_udp()
        pass

    @threaded
    def accept_chat(self):
        pass

    @threaded
    def accept_media_tcp(self):
        pass

    @threaded
    def accept_media_udp(self):
        pass

    @threaded
    def handle_chat(self, chat_socket: socket):
        """
        Accepts its listen func.
        :param chat_socket:
        :return:
        """
        pass

    @threaded
    def handle_media_tcp(self, media_tcp_socket: socket):
        pass

    @threaded
    def handle_media_udp(self, media_udp_socket: socket):
        pass

