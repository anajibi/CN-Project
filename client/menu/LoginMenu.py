from client.Client import tcp_send_data
from client.menu.MailMenu import MailMenu
from client.menu.Menu import Menu


class LoginMenu(Menu):
    username: str
    password: str

    def __init__(self, parent):
        super().__init__(parent, "Login")

    def show(self):
        self.username = ""
        self.password = ""
        return self

    def execute(self):
        self.login_procedure()
        self.parent.run()
        return self

    def login_procedure(self):
        self.prompt_username()
        self.prompt_password()
        if not self.send_user_pass_to_server():
            print("Incorrect username or password.")
            self.parent.run()
        else:
            MailMenu(self).run()

    def send_user_pass_to_server(self):
        data = {
            'command': 'LOGIN',
            'username': self.username,
            'password': self.password
        }
        response = tcp_send_data(data=data, ip='localhost', port='3030')
        return response['status'] == "OK"

    def prompt_username(self):
        print("Please enter your username.")
        self.username = input()

    def prompt_password(self):
        print("Please enter your password.")
        self.password = input()
