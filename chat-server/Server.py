import socket
from typing import Dict, List, Tuple

SERVER_PORT_INFO = 3030
URL = "localhost"

"""
PROTOCOL (Port 3030):

    Request: 
        { username: "" }, -> { payload: List[ str (username), num (unread_chat_num)] }
        { username: "", messages_num: int }
    
    Response:
        { payload: ""}
    
    all messages:
        { from: "", to:"", message: ""}

"""


class Chat:
    seen_messages: List[str]
    unseen_messages: List[str]

    def load_x_messages(self, messages_num: int):
        """
        Returns x last messages of this chat.
        :param messages_num:
        :return:
        """
        pass


class Inbox:
    chats_list: Dict[str, Chat]

    def get_chat(self, username: str) -> Chat:
        """
        Returns a chat from our dest client.
        :param username:
        :return:
        """
        pass


class ChatServer:
    user: Dict[str, Inbox]
    online_users: Dict[str, Tuple[str, int]]

    chat_socket: socket.socket

    def __init__(self):
        self.chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chat_socket.bind((URL, SERVER_PORT_INFO))
        self.chat_socket.listen()

    def start(self):
        try:
            while (True):
                socket, addr = self.chat_socket.accept()
                # Gets exception somewhere
        except Exception as e:
            pass

    def handle_request(self):
        pass


ChatServer().start()
