import json
import re
import socket

from client.menu.Menu import Menu, tcp_send_data


class MailMenu(Menu):
    inbox: str

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

    def chat_with(self, contact: str):
        username = self.parent.username
        data = {
            "command": "CHAT",
            "username": username,
            "contact": contact
        }
        data = json.dumps(data)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 3030))
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

    def start_talking(self, contact: str, s: socket.socket):
        username = self.parent.username
        print(self.get_messages(5, s))
        while True:
            pm = input(f"{username}: ")
            if self.is_pm_shortcut(pm):
                if pm == '/exit':
                    break
                if regexp := re.match(r"/load (\d+)", pm):
                    count = int(regexp.group(1))
                    print(self.get_messages(count, s))
            data = {
                "command": "SEND",
                "to": contact,
                "message": pm
            }
            data = json.dumps(data)
            s.sendall(bytes(data, encoding='utf-8'))

    @staticmethod
    def get_messages(count: int, s: socket.socket):
        data = {
            "command": "MESSAGES",
            "count": count
        }
        data = json.dumps(data)
        s.sendall(bytes(data, encoding='utf-8'))
        return s.recv(1024).decode('utf-8')
