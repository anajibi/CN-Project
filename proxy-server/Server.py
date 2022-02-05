# Proxy Input Request Port
import socket
import threading
from enum import Enum
from typing import Dict, Tuple

CHAT_PORT = 6060
STREAMING_PORT = 6070

# ChatServer
CHAT_SERVER_PORT = 3030

# MediaServer
MEDIA_SERVER_PORT = 4030


class SockType(Enum):
    TCP = "TCP",
    UDP = "UDP"


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


# A Proxy server for udp and tcp packets
class ProxyServer:
    chat: socket.socket
    media_tcp: socket.socket
    media_udp: socket.socket
    forwarding_table: Dict[Tuple[int, SockType], socket.socket]  # (3423, SockType.TCP): 2348

    def __init__(self):
        """
        Sets 3 sockets. Listens.
        Calls each handle_client & sets it inside forwarding_table.
        """
        self.init_sockets()
        self.forwarding_table = {}
        self.accept_and_forward_tcp(self.chat, CHAT_SERVER_PORT)
        self.accept_and_forward_tcp(self.media_tcp, MEDIA_SERVER_PORT)
        self.accept_and_forward_udp()

    @threaded
    def accept_and_forward_tcp(self, sock: socket.socket, target_port: int, target_sock_type: SockType):
        try:
            while True:
                client, addr = sock.accept()
                self.handle_client(client, target_port, target_sock_type)
        except Exception as e:
            sock.close()

    @threaded
    def handle_client(self, client: socket.socket, target_port: int):
        sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM)
        sock.bind(("", 0))
        sock.connect(('localhost', target_port))
        self.handle_recv(sock, client)
        self.handle_recv(client, sock)

    @threaded
    def handle_recv(self, recv_sock, send_sock):
        try:
            while True:
                data = recv_sock.recv(1024)
                send_sock.send(data)
        except Exception as e:
            recv_sock.close()
            send_sock.close()

    @threaded
    def accept_and_forward_udp(self):
        try:
            while True:
                data, addr = self.media_udp.recvfrom(1024)
                self.handle_client_udp(data, addr)
        except Exception as e:
            pass

    @threaded
    def handle_client_udp(self, data, addr):
        if addr in self.forwarding_table:
            self.forward_udp(data, addr, self.forwarding_table[addr])
        else:
            self.forward_udp(data, addr, None)

    @threaded
    def forward_udp(self, data, addr, target_socket):
        if target_socket is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(("", 0))
            self.forwarding_table[addr] = sock.getsockname()[1]
            self.backward_udp(addr, sock)
            sock.sendto(data, ('localhost', MEDIA_SERVER_PORT))
        else:
            target_socket.sendto(data, ('localhost', MEDIA_SERVER_PORT))

    @threaded
    def backward_udp(self, _addr, sock):
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                if addr[1] == MEDIA_SERVER_PORT:
                    self.media_udp.sendto(data, _addr)
        except Exception as e:
            pass

    def init_sockets(self):
        chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        chat.bind(('localhost', CHAT_PORT))
        chat.listen()
        self.chat = chat
        media_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        media_tcp.bind(('localhost', STREAMING_PORT))
        media_tcp.listen()
        self.media_tcp = media_tcp
        media_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        media_udp.bind(('localhost', STREAMING_PORT))
        self.media_udp = media_udp

    # @threaded
    # def accept_chat(self):
    #     try:
    #         while (True):
    #             socket, addr = self.chat.accept()
    #             self.handle_chat(socket, addr)
    #     except Exception as e:
    #         pass
    #
    # @threaded
    # def accept_media_tcp(self):
    #     try:
    #         while (True):
    #             socket, addr = self.chat.accept()
    #             self.handle_chat(socket, addr)
    #     except Exception as e:
    #         pass
    #
    # @threaded
    # def accept_media_udp(self):
    #     pass
    #
    # @threaded
    # def handle_chat(self, chat_socket: socket):
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     sock.bind(("", 0))
    #     sock.connect(('localhost', CHAT_SERVER_PORT))
    #     self.handle_recv(chat_socket, sock)
    #     self.handle_recv(sock, chat_socket)
    #
    # @threaded
    # def handle_media_tcp(self, media_tcp_socket: socket):
    #     pass
    #
    # @threaded
    # def handle_media_udp(self, media_udp_socket: socket):
    #     pass
