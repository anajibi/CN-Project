import socket
from typing import Dict

SERVER_PORT_INFO = 4030

URL = "localhost"

"""
PROTOCOL (Port 4030):
    Request: 
        TCP: {resource: "LIST"}
        UDP: {resource: @MEDIA}
    
    Response:
        TCP:{payload: @LIST}
        UDP: ByteStream
"""


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class MediaServer:
    media: Dict[str, str]

    publish: socket.socket
    online_delivery: socket.socket

    def __init__(self):
        self.publish = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.publish.bind((URL, SERVER_PORT_INFO))
        self.publish.listen()
        self.online_delivery = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.online_delivery.bind((URL, SERVER_PORT_INFO))
        self.online_delivery.listen()

    @threaded
    def acc_publish(self):
        pass

    @threaded
    def acc_online_delivery(self):
        pass

    def send_video_names(self, socket_val: socket, addr: str):
        """
        For publish socket.
        :param socket_val:
        :param addr:
        :return:
        """
        pass

    def start(self):
        """
        calls online_delivery UDP service.
        :return:
        """
        self.acc_publish()
        self.acc_online_delivery()

    def send_stream(self, client):
        pass

    def end_stream(self, client):
        pass


MediaServer().start()
