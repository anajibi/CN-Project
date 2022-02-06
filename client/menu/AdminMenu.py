import re

from client.Firewall import Firewall, FirewallType
from client.menu.Menu import Menu


class AdminMenu(Menu):
    username: str
    password: str

    def __init__(self, parent):
        super().__init__(parent, "Admin Menu")

    def show(self):
        print("Enter Admin User Pass.")
        return self

    def execute(self):
        if not self.login_procedure():
            self.parent.run()
        else:
            self.firewall_procedure()

    def firewall_procedure(self):
        hint = """
                activate [whitelist|blacklist] firewall
                [open|close] port
                0 (Exit)
                """
        print(hint)
        while True:
            command = input()
            if command == 'activate whitelist firewall':
                self.firewall = Firewall(FirewallType.WHITE_LIST)
            elif command == 'activate blacklist firewall':
                self.firewall = Firewall(FirewallType.BLACK_LIST)
            elif regexp := re.match(r"open port (\d+)", command):
                port = int(regexp.group(1))
                self.firewall.add_port(port)
            elif regexp := re.match(r"close port (\d+)", command):
                port = int(regexp.group(1))
                self.firewall.del_port(port)
            elif command == '0':
                break
            else:
                print("Invalid Command.")

    def login_procedure(self):
        self.prompt_username()
        self.prompt_password()
        if not (self.username == 'admin' and self.password == 'admin'):
            print("Wrong User Pass.")
            return False
        return True

    def prompt_username(self):
        self.username = input()

    def prompt_password(self):
        self.password = input()
