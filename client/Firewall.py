from enum import Enum
from socket import socket
from typing import List


class FirewallType(Enum):
    BLACK_LIST = "BLACK_LIST"
    WHITE_LIST = "WHITE_LIST"


class Firewall:
    type: FirewallType
    port_list: List[int]

    def __init__(self, type_val: FirewallType):
        self.type = type_val

    def add_port(self, port: int):
        """
        Adds port to port_list
        :param port:
        :return:
        """
        pass

    def del_port(self, port: int):
        """
        Deletes port from port_list
        :param port:
        :return:
        """
        pass

    def check_should_let_through(self, packet):
        """
        Depending on packet, checks firewall conditions based on its type.
        :param packet:
        :return:
        """
        pass


class ControlledSocket(socket):
    firewall: Firewall
    socket: socket

    def __init__(self, firewall, socket_val):
        super().__init__()
        self.firewall = firewall
        self.socket = socket_val

    def sendto(self, data: bytes, address: any) -> int:
        """
        Use this function to check whether firewall should be used.
        :param data:
        :param address:
        :return:
        """
        pass

    def recv(self, bufsize: int, flags: int = ...) -> bytes:
        """
        Use this function to check whether firewall should be used.
        :param bufsize:
        :param flags:
        :return:
        """
        pass

    def send(self, data: bytes, flags: int = ...) -> int:
        """
        Use this function to check whether firewall should be used.
        :param data:
        :param flags:
        :return:
        """
        pass
