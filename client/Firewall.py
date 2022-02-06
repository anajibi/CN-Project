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
        self.port_list = []

    def add_port(self, port: int):
        """
        Adds port to port_list
        :param port:
        :return:
        """
        self.port_list.append(port)

    def del_port(self, port: int):
        """
        Deletes port from port_list
        :param port:
        :return:
        """
        if port in self.port_list:
            self.port_list.remove(port)
        else:
            print("Port not found in port_list")

    def can_go_through(self, port: int):
        """
        Depending on packet, checks firewall conditions based on its type.
        :param packet:
        :return:
        """

        if self.type == FirewallType.BLACK_LIST:
            return self.check_black_list(port)
        else:
            return self.check_white_list(port)

    def check_black_list(self, port):
        return not (port in self.port_list)

    def check_white_list(self, port):
        return port in self.port_list


class ControlledSocket(socket):
    firewall: Firewall

    def __init__(self, firewall, socket_val):
        super().__init__()
        self.firewall = firewall

    def sendto(self, data: bytes, address: any) -> int:
        """
        Use this function to check whether firewall should be used.
        :param data:
        :param address:
        :return:
        """
        if self.firewall.can_go_through(address[1]):
            return super().sendto(data, address)
        else:
            print("packet dropped due to firewall rules")
            return -1

    def recv(self, bufsize: int, flags: int = ...) -> bytes:
        """
        Use this function to check whether firewall should be used.
        :param bufsize:
        :param flags:
        :return:
        """
        if self.firewall.can_go_through(self.getsockname()[1]):
            return super(ControlledSocket, self).recv(bufsize, flags)
        else:
            print("packet dropped due to firewall rules")
            return None

    def send(self, data: bytes, flags: int = ...) -> int:
        """
        Use this function to check whether firewall should be used.
        :param data:
        :param flags:
        :return:
        """
        if self.firewall.can_go_through(self.getsockname()[1]):
            return super(ControlledSocket, self).send(data, flags)
        else:
            print("packet dropped due to firewall rules")
            return -1
