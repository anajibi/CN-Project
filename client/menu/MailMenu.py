import json
import re
import socket
import threading
from typing import List

from Firewall import ControlledSocket
from menu.Menu import Menu, tcp_send_data


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class MailMenu(Menu):
    inbox: str
    messages: List[str]

    def __init__(self, parent):
        super().__init__(parent, "Mail Menu")

    def show(self):
        # if not isinstance(self.parent, LoginMenu):
        #     exit(1)
        data = {
            "command": "INBOX",
            "username": self.parent.username
        }
        response = tcp_send_data(data, 'localhost', 3030)
        if response['status'] != "OK":
            print("Username Doesn't Exist.")
        else:
            self.inbox = response['inbox']
            print(self.inbox)
        return self

    def execute(self):
        while True:
            contact = input()
            if contact == '0':
                return self  # Todo ? If doesn't work, self.parent.run()
            if contact in self.inbox:
                self.chat_with(contact)
                self.show()

    def pretty(self, d, indent=0):
        for key, value in d.items():
            print('\t' * indent + str(key))
            if isinstance(value, dict):
                self.pretty(value, indent+1)
            else:
                print('\t' * (indent+1) + str(value))

    def chat_with(self, contact: str):
        username = self.parent.username
        data = {
            "command": "CHAT",
            "username": username,
            "contact": contact
        }
        data = json.dumps(data)
        with ControlledSocket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', self.get_chat_port()))
            s.sendall(bytes(data, encoding='utf-8'))
            message = s.recv(1024).decode('utf-8')
            response = json.loads(message)
            if response['status'] != "OK":
                print("Inbox had an error.")
            else:
                self.start_talking(contact, s)

    @staticmethod
    def is_pm_shortcut(pm):
        return pm.startswith('/')

    def start_talking(self, contact: str, s: ControlledSocket):
        username = self.parent.username
        data = eval(self.get_messages(5, s))
        for line in data:
            print(line)
        while True:
            pm = input(f"{username}: ")
            if self.is_pm_shortcut(pm):
                if pm == '/exit':
                    break
                if regexp := re.match(r"/load (\d+)", pm):
                    count = int(regexp.group(1))
                    data = eval(self.get_messages(count, s))
                    for line in data:
                        print(line)
            else:
                data = {
                    "command": "SEND",
                    "to": contact,
                    "message": pm
                }
                data = json.dumps(data)
                s.sendall(bytes(data, encoding='utf-8'))
                response = s.recv(1024).decode('utf-8')

    @staticmethod
    def get_messages(count: int, s: ControlledSocket):
        data = {
            "command": "MESSAGES",
            "count": count
        }
        data = json.dumps(data)
        s.sendall(bytes(data, encoding='utf-8'))
        return s.recv(1024).decode('utf-8')
