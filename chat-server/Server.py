import socket
import threading
from typing import Dict, List, Tuple, Set

CHAT_TIMEOUT = 2 * 60  # 2 minutes
SERVER_PORT_INFO = 3030
URL = "localhost"

"""
PROTOCOL (Port 3030):

    Request: 
        { command: GET_USERS} -> { users: [user1, user2, ...] }
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


class Chat:
    seen_messages: List[str]
    unseen_messages: List[str]

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
            return messages_to_send
        else:
            self.seen_messages += self.unseen_messages
            return self.seen_messages[-messages_num:]


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
            self.chats_list[username].unseen_messages.append(message)
        else:
            self.chats_list[username] = Chat()
            self.chats_list[username].unseen_messages.append(message)

    def add_read_message(self, username: str, message: str):
        """
        Adds a message to the chat.
        :param message:
        :param username:
        :return:
        """
        self.chats_list[username].seen_messages.append(message)

    def get_chat(self, username: str) -> Chat:
        """
        Returns a chat from our dest client.
        :param username:
        :return:
        """
        return self.chats_list[username]

    def add_chat(self, username:str):
        self.chats_list[username] = Chat()
        self.chats_order.append(username)


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class ChatServer:
    users: Dict[str, str]
    users_inbox: Dict[str, Inbox]
    online_users: Dict[str, Tuple[socket.socket, str]]

    chat_socket: socket.socket

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
            if message["command"] == "GET_USERS":
                self.send_users(sock)
            if message["command"] == "LOGIN":
                self.login(message["username"], message["password"], sock)
            elif message["command"] == "REGISTER":
                self.register(message["username"], message["password"], sock)
            elif message["command"] == "INBOX":
                self.inbox(message["username"], sock)
            elif message["command"] == "CHAT":
                self.chat(message["username"], message["contact"], sock)

        except Exception as e:
            sock.sendall(b"{status: UNKNOWN_COMMAND}")

    def chat(self, username: str, contact: str, sock: socket.socket):
        if username not in self.users:
            sock.sendall(b"{status: NOT_REGISTERED}")
        else:
            if contact not in self.users_inbox[username].chats_list:
                sock.sendall(b"{status: NO_CHAT}")
            else:
                sock.sendall(b"{status: OK}")
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
        sock.sendall(self.users_inbox[username].get_chat(contact).load_x_messages(count).encode())

    def send(self, username: str, to: str, message: str, sock: socket.socket):
        if self.online_users[username][1] != to:
            sock.sendall(b"{status: CANT_SEND_MESSAGE_ON_DIFFERENT_CHATS}")
        else:
            if to in self.online_users and self.online_users[to][1] == username:
                self.online_users[to][0].sendall(b"{command: RECEIVE, message: " + message.encode() + b"}")
                self.users_inbox[to].add_read_message(username, message)
            else:
                self.users_inbox[to].add_message(username, message)
                sock.sendall(b"{status: OK}")
            sock.sendall(b"{status: OK}")

    def login(self, username: str, password: str, sock: socket.socket):
        if username in self.users:
            if self.users[username] == password:
                sock.sendall(b"{status: OK}")
            else:
                sock.sendall(b"{status: WRONG_PASSWORD}")
        else:
            sock.sendall(b"{status: WRONG_USERNAME}")

    def register(self, username: str, password: str, sock: socket.socket):
        if username in self.users:
            sock.sendall(b"{status: USERNAME_TAKEN}")
        else:
            self.users[username] = password
            self.add_user_to_other_inboxes(username)
            self.users_inbox[username] = Inbox()
            sock.sendall(b"{status: OK}")

    def add_user_to_other_inboxes(self, username: str):
        for inbox in self.users_inbox.values():
            inbox.add_chat(username)

    def inbox(self, username: str, sock: socket.socket):
        if username in self.users_inbox:
            self.send_inbox(username, sock)
        else:
            sock.sendall(b"{status: UNKNOWN_USER}")

    def send_inbox(self, username: str, sock: socket.socket):
        inbox = self.users_inbox[username]
        sock.sendall(b"{status: OK, inbox: " + str(inbox.summarize_inbox()).encode() + b"}")

    def send_users(self, sock: socket.socket):
        sock.sendall(b"{users: " + str(self.users).encode() + b"}")


ChatServer().start()
