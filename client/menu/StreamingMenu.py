import pickle
import socket
import struct

import cv2

from client.Firewall import ControlledSocket
from client.menu.Menu import Menu

IP, port = '127.0.0.1', 4030


class StreamingMenu(Menu):
    publish_socket: ControlledSocket
    stream_socket: ControlledSocket

    def __init__(self, parent):
        print("Welcome to Choghondar.")
        super().__init__(parent, "Streaming Menu")
        self.publish_socket = ControlledSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_socket = ControlledSocket(socket.AF_INET, socket.SOCK_STREAM)

    def show(self):
        self.publish_socket.connect((IP, port))
        msg = self.publish_socket.recv(1024)
        print(msg.decode('ascii'))

        payload_size = struct.calcsize('Q')

        self.stream_socket.connect((IP, port + 1))
        self.stream_socket.sendall(b'behdad babaei')
        data = b''
        while True:
            while len(data) < payload_size:
                packet = self.stream_socket.recv(4096)
                if not packet:
                    break
                data += packet
            frame_size = struct.unpack('Q', data[:payload_size])[0]
            data = data[payload_size:]
            while len(data) < frame_size:
                packet = self.stream_socket.recv(4096)
                data += packet
            serialized_frame = data[:frame_size]
            data = data[frame_size:]
            frame = pickle.loads(serialized_frame)
            cv2.imshow('behdad babaei', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        self.publish_socket.close()
        self.stream_socket.close()
        cv2.destroyAllWindows()

        return self

    def execute(self):
        self.parent.run()
