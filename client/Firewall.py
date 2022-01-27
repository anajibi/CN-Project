from enum import Enum
from socket import socket
from typing import List


class FirewallType(Enum):
    BLACK_LIST = "BLACK_LIST"
    WHITE_LIST = "WHITE_LIST"


class Firewall:
    type: FirewallType
    port_list: List[int]

    def check_should_let_through(self, packet):
        pass



class ControlledSocket:
    firewall: Firewall
    socket: socket

    def __init__(self, firewall):
        self.firewall = firewall

    def recv(self):
        pass

    def send(self):
        pass
