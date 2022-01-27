import socket
from typing import Dict, List, Tuple

SERVER_PORT_PUBLISH = 3030
URL = "localhost"
""""
PROTOCOL:
3030:
Request: 
{ username: ""}

Response:
{ payload: ""}

3040:
all messages:
{ from: "", to:"", message: ""}

"""


class Chat:
    seen_messages: List[str]
    unseen_messages: List[str]


class Inbox:
    chats_list: Dict[str, Chat]


class ChatServer:
    user: Dict[str, Inbox]
    online_users: [str, Tuple[str, int]]

    publish: socket.socket
    online_delivery: socket.socket

    def __init__(self):
        self.publish = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.publish.bind((URL, SERVER_PORT_PUBLISH))
        self.publish.listen()

        self.online_delivery = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.online_delivery.bind((URL, SERVER_PORT_ONLINE_CHAT))
        self.online_delivery.listen()

    def start(self):
        pass


ChatServer.start()
