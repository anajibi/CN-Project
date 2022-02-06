from audioop import add
import socket
from statistics import median
from typing import Dict
import threading

import cv2, pickle, struct

SERVER_PORT_INFO = 4030
SERVER_STREAM_PORT = 4031

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

class MediaServer:
    # media: Dict[str, str]
    media = {
        'behdad babaei' : '1.mp4',
        'hossein alizade' : '2.mp4',
        'keyhan kalhor' : '3.mp4'
    }

    publish: socket.socket
    online_delivery: socket.socket

    def __init__(self):
        self.publish = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.publish.bind((URL, SERVER_PORT_INFO))
        self.publish.listen()
        self.online_delivery = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.online_delivery.bind((URL, SERVER_STREAM_PORT))
        self.online_delivery.listen()

    def send_stream(self, conn):
        name = conn.recv(1024).decode('ascii')
        print(f'name of media : {name}')
        with conn:
            try:
                vid = cv2.VideoCapture(self.media[name])
                while vid.isOpened():
                    ret, frame = vid.read()
                    serialized_frame = pickle.dumps(frame)
                    header = struct.pack('Q', len(serialized_frame))
                    data = header + serialized_frame
                    conn.sendall(data)
                    cv2.imshow('sending', frame)
                    key = cv2.waitKey(25)
            except ConnectionResetError:
                vid.release()
                cv2.destroyAllWindows()


    def media_list(self):
        list = ''
        for item in self.media.keys():
            list += item
            list += '\n'
        return list

    def acc_publish(self):
        while True:
            conn, addr = self.publish.accept()
            print('publish connection : {addr}')
            with conn:
                conn.sendall(self.media_list().encode('ascii'))

    def acc_online_delivery(self):
        while True:
            conn, addr = self.online_delivery.accept()
            print('online delivery connection : {addr}')
            threading.Thread(target=self.send_stream, args=(conn, )).start()

    def start(self):
        """
        calls online_delivery UDP service.
        :return:
        """
        threading.Thread(target=self.acc_publish, args=()).start()
        threading.Thread(target=self.acc_online_delivery, args=()).start()

MediaServer().start()
