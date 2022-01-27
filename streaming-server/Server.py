import socket
from typing import Dict, List, Tuple

SERVER_PORT_INFO = 4030

URL = "localhost"
""""
PROTOCOL:
4030:
Request: 
TCP: {resource: "LIST"}
UDP: {resource: @MEDIA}

Response:
TCP:{payload: @LIST}
UDP: ByteStream

"""


class MediaServer:
    media: Dict[str, str]

    publish: socket.socket
    online_delivery: socket.socket

    def __init__(self):
        self.publish = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.publish.bind((URL, SERVER_PORT_INFO))
        self.publish.listen()

    def start(self):
        pass


MediaServer.start()
