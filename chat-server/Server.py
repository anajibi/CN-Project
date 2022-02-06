import json
import socket
import threading
from typing import Dict, List, Tuple, Set, Union

CHAT_TIMEOUT = 2 * 60  # 2 minutes
SERVER_PORT_INFO = 3030
URL = "localhost"

"""
PROTOCOL (Port 3030):

    Request: 
        { command: GET_USER, username: <username> } -> { status: OK | USER_TAKEN }
        { command: LOGIN, username: <username>, password: <password> } -> { status: <status> } This connection will be closed after receiving the response
        { command: REGISTER, username: <username>, password: <password> } -> { status: <status> } This connection will be closed after receiving the response
        { command: INBOX, username: <username> } -> { status: <status> ,Dict[str, number] } --- This connection will be closed after receiving the response
        { command: CHAT, username: <username>, contact: <username>} ---- This Connection should be persistent until the user exits the chat and server might send a message on this connection
        with format { message: <message> }
        { command SEND, to: <username>, message: <message> } -> { status: <status> } ---- This message is sent on the connection initiated with command CHAT
        { command MESSAGES, count: <number> } -> { List[str] } ---- This message is sent on the connection initiated with command CHAT
    
    Response:
        { payload: ""}
    
    all messages:
        { from: "", to:"", message: ""}

"""


def send_data(data: dict, sock: socket):
    json_data = json.dumps(data)
    sock.sendall(bytes(json_data, encoding='utf-8'))


def message_to_str(messages: List[Tuple[Union[str, None], str]]):
    result = []
    for message in messages:
        if message[0] is None:
            result.append(f'you: {message[1]}')
        else:
            result.append(f"{message[0]: {message[1]}}")
    return result


class Chat:
    seen_messages: List[Tuple[Union[str, None], str]]
    unseen_messages: List[Tuple[str, str]]

    def load_x_messages(self, messages_num: int):
        """
        Returns x last messages of this chat.
        :param messages_num:
        :return:
        """
        if len(self.unseen_messages) > messages_num:
            messages_to_send = self.unseen_messages[-messages_num:]
            self.unseen_messages = self.unseen_messages[:-messages_num]
            self.seen_messages += messages_to_send

            return message_to_str(messages_to_send)
        else:
            self.seen_messages += self.unseen_messages
            return message_to_str(self.seen_messages[-messages_num:])


class Inbox:
    chats_list: Dict[str, Chat]
    chats_order: List[str]

    def __init__(self):
        self.chats_list = {}
        self.chats_order = list()

    def summarize_inbox(self) -> Dict[str, int]:
        """
        Returns a dict with the number of unseen messages for each chat
        :return:
        """
        result = {}
        for user in reversed(self.chats_order):
            result[user] = len(self.chats_list[user].unseen_messages)
        return result

    def add_message(self, message: str, username: str):
        """
        Adds a message to the chat.
        :param message:
        :param username:
        :return:
        """
        self.chats_order.remove(username)
        self.chats_order.append(username)
        if username in self.chats_list:
            self.chats_list[username].unseen_messages.append((username, message))
        else:
            self.chats_list[username] = Chat()
            self.chats_list[username].unseen_messages.append((username, message))

    def add_read_message(self, username: str, message: str):
        """
        Adds a message to the chat.
        :param message:
        :param username:
        :return:
        """
        self.chats_list[username].seen_messages.append((username, message))

    def get_chat(self, username: str) -> Chat:
        """
        Returns a chat from our dest client.
        :param username:
        :return:
        """
        return self.chats_list[username]

    def add_chat(self, username: str):
        self.chats_list[username] = Chat()
        self.chats_order.append(username)

    def add_self_message(self, username: str, message: str):
        self.chats_list[username].seen_messages.append((None, message))


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class ChatServer:
    users: Dict[str, str]
    users_inbox: Dict[str, Inbox]
    online_users: Dict[str, Tuple[socket.socket, str]]

    chat_socket: socket.socket

    def get_user_socket(self, username: str):
        return self.online_users[username][0]

    def get_user_contact(self, username: str):
        return self.online_users[username][1]

    def __init__(self):
        self.chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.chat_socket.bind((URL, SERVER_PORT_INFO))
        self.chat_socket.listen()
        self.users = {}
        self.online_users = {}
        self.users_inbox = {}
        self.start()

    def start(self):
        try:
            while (True):
                socket, addr = self.chat_socket.accept()
                self.handle_request(socket, addr)
                # Gets exception somewhere
        except Exception as e:
            pass

    @threaded
    # receives a request from client
    def handle_request(self, sock: socket.socket, addr):
        try:
            while (True):
                data = sock.recv(1024)
                if not data:
                    break
                self.handle_message(data, sock, addr)
        except Exception as e:
            pass

    def handle_message(self, data, sock, addr):
        try:
            message = eval(data.decode())
            if message["command"] == "GET_USER":
                self.send_user_available(message["username"], sock)
            if message["command"] == "LOGIN":
                self.login(message["username"], message["password"], sock)
            elif message["command"] == "REGISTER":
                self.register(message["username"], message["password"], sock)
            elif message["command"] == "INBOX":
                self.inbox(message["username"], sock)
            elif message["command"] == "CHAT":
                self.chat(message["username"], message["contact"], sock)

        except Exception as e:
            data = {
                "status": "UNKNOWN_COMMAND"
            }
            send_data(data, sock)

    def chat(self, username: str, contact: str, sock: socket.socket):
        if username not in self.users:
            data = {
                "status": "NOT_REGISTERED"
            }
            send_data(data, sock)
        else:
            if contact not in self.users_inbox[username].chats_list:
                data = {
                    "status": "NO_CHAT"
                }
                send_data(data, sock)
            else:
                data = {
                    "status": "OK"
                }
                send_data(data, sock)
                sock.settimeout(CHAT_TIMEOUT)
                self.online_users[username] = (sock, contact)
                self.handle_chat(username, contact, sock)

    def handle_chat(self, username, contact, sock: socket.socket):
        try:
            while (True):
                data = sock.recv(1024)
                if not data:
                    break
                self.handle_chat_message(username, contact, data, sock)
        except Exception as e:
            pass

    def handle_chat_message(self, username: str, contact, data, sock: socket.socket):
        try:
            message = eval(data.decode())
            if message["command"] == "SEND":
                self.send(username, message["to"], message["message"], sock)
            elif message["command"] == "MESSAGES":
                self.messages(message["count"], username, contact, sock)
        except Exception as e:
            sock.close()
            del self.online_users[username]

    def messages(self, count: int, username: str, contact: str, sock: socket.socket):
        sock.sendall(str(self.users_inbox[username].get_chat(contact).load_x_messages(count)).encode())

    def send(self, username: str, to: str, message: str, sock: socket.socket):

        if self.get_user_contact(username) != to:
            data = {
                "status": "CANT_SEND_MESSAGE_ON_DIFFERENT_CHATS"
            }
            send_data(data, sock)
        else:
            self.users_inbox[username].add_read_message(to, message)
            if to in self.online_users and self.get_user_contact(to) == username:
                data = {
                    "command": "RECEIVE",
                    "message": message
                }
                send_data(data, self.get_user_socket(to))
                self.users_inbox[to].add_read_message(username, message)
            else:
                self.users_inbox[to].add_message(username, message)
                data = {
                    "status": "OK"
                }
                send_data(data, sock)
            data = {
                "status": "OK"
            }
            send_data(data, sock)

    def login(self, username: str, password: str, sock: socket.socket):
        if username in self.users:
            if self.users[username] == password:
                data = {
                    "status": "OK"
                }
            else:
                data = {
                    "status": "WRONG_PASSWORD"
                }
        else:
            data = {
                "status": "WRONG_USERNAME"
            }
        send_data(data, sock)

    def register(self, username: str, password: str, sock: socket.socket):
        if username in self.users:
            data = {
                "status": "USERNAME_TAKEN"
            }
        else:
            self.users[username] = password
            self.add_user_to_other_inboxes(username)
            self.users_inbox[username] = Inbox()
            data = {
                "status": "OK"
            }
        send_data(data, sock)

    def add_user_to_other_inboxes(self, username: str):
        for inbox in self.users_inbox.values():
            inbox.add_chat(username)

    def inbox(self, username: str, sock: socket.socket):
        if username in self.users_inbox:
            data = self.get_inbox_data(username)
        else:
            data = {
                "status": "UNKNOWN_USER"
            }
        send_data(data, sock)

    def get_inbox_data(self, username: str):
        inbox = self.users_inbox[username]
        return {
            "status": "OK",
            "inbox": str(inbox.summarize_inbox())
        }

    def send_user_available(self, username: str, sock: socket.socket):
        if username in self.users:
            data = {
                "status": "USER_TAKEN"
            }
        else:
            data = {
                "status": "OK"
            }
        send_data(data, sock)


ChatServer().start()
