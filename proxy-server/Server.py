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
    forwarding_table: Dict[Tuple[Tuple[str, int], SockType], int]
