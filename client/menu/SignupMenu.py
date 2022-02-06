from client.Client import tcp_send_data
from client.menu.Menu import Menu


class SignUpMenu(Menu):
    username: str
    password: str

    def __init__(self, parent):
        super().__init__(parent, "Signup")

    def show(self):
        self.username = ""
        self.password = ""
        return self

    def execute(self):
        self.sign_up_procedure()
        self.parent.run()
        return self

    def sign_up_procedure(self):
        self.prompt_username()
        self.prompt_password()
        self.send_user_pass_to_server()

    def is_username_new(self):
        data = {
            'command': 'GET_USER',
            'username': self.username
        }
        response = tcp_send_data(data=data, ip='localhost', port=3030)
        return response['status'] == "OK"  # Todo: Enum

    def is_username_bad(self):
        return (not self.is_username_new()) or self.username == '0'

    def send_user_pass_to_server(self):
        data = {
            'command': 'REGISTER',
            'username': self.username,
            'password': self.password
        }
        response = tcp_send_data(data=data, ip='localhost', port='3030')
        return response['status'] == "OK"

    def prompt_username(self):
        print("Please enter your username.")
        while True:
            self.username = input()
            if self.is_username_bad():
                print(
                    "This username is already existed or invalid. Please enter another one.")
            else:
                break

    def prompt_password(self):
        print("Please enter your password.")
        self.password = input()
