import base64
import os
import pickle
import socket
import struct
from datetime import time
from typing import List

import numpy as np
import pyaudio
import cv2

from Firewall import ControlledSocket
from menu.Menu import Menu



class StreamingMenu(Menu):
    publish_socket: ControlledSocket
    stream_socket: ControlledSocket
    movie_list: List[str]

    def __init__(self, parent):
        super().__init__(parent, "Streaming Menu")
        self.publish_socket = ControlledSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.stream_socket = ControlledSocket(socket.AF_INET, socket.SOCK_STREAM)
        self.movie_list = []

    def show(self):
        print("Welcome to Choghondar.")
        self.publish_socket.connect(('localhost', self.get_streaming_info_port()))
        response = self.publish_socket.recv(1024).decode('ascii')
        response = response.split('\n')
        index = 1
        for line in response:
            if line:
                self.movie_list.append(line)
                print(f"{index}. {line}")
                index = index + 1
        print(f"{index}. Exit")

        return self

    def execute(self):
        while True:
            command = ""
            while not self.accepted(command):
                command = input()

            selected = int(command)
            if selected == len(self.movie_list) + 1:
                break

            self.run_movie(selected)
            
        self.parent.run()
        

    def accepted(self, command: str):
        if not command.isdigit():
            return False
        if int(command) > len(self.movie_list) + 1:
            return False
        return True

    def run_movie(self, selected: int):
        movie_name = self.movie_list[selected - 1]
        BUFF_SIZE = 65536

        client_socket = ControlledSocket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
        client_socket.settimeout(1)
        host_ip = 'localhost'
        client_socket.sendto(bytes(movie_name, 'ascii'), (host_ip, self.streaming_port))

        def video_stream():
            cv2.namedWindow('RECEIVING VIDEO')
            cv2.moveWindow('RECEIVING VIDEO', 10,360)
            fps,st,frames_to_count,cnt = (0,0,20,0)
            while True:
                try:
                    packet,_ = client_socket.recvfrom(BUFF_SIZE)
                    data = base64.b64decode(packet,' /')
                    npdata = np.fromstring(data,dtype=np.uint8)

                    frame = cv2.imdecode(npdata,1)
                    frame = cv2.putText(frame,'FPS: '+str(fps),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
                    cv2.imshow("RECEIVING VIDEO",frame)
                    key = cv2.waitKey(1) & 0xFF

                    if key == ord('q'):
                        client_socket.close()
                        return

                    if cnt == frames_to_count:
                        try:
                            fps = round(frames_to_count/(time.time()-st))
                            st=time.time()
                            cnt=0
                        except:
                            pass
                    cnt+=1
                except:
                    cv2.destroyAllWindows()
                    return

        def audio_stream():
            p = pyaudio.PyAudio()
            CHUNK = 1024
            stream = p.open(format=p.get_format_from_width(2),
                            channels=2,
                            rate=44100,
                            output=True,
                            frames_per_buffer=CHUNK)

            # create socket
            client_socket = ControlledSocket(socket.AF_INET,socket.SOCK_STREAM)
            socket_address = (host_ip,self.get_streaming_port())
            print('server listening at',socket_address)
            client_socket.connect(socket_address)
            print("CLIENT CONNECTED TO",socket_address)
            data = b""
            payload_size = struct.calcsize("Q")
            while True:
                try:
                    while len(data) < payload_size:
                        packet = client_socket.recv(4*1024) # 4K
                        if not packet: break
                        data+=packet
                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack("Q",packed_msg_size)[0]
                    while len(data) < msg_size:
                        data += client_socket.recv(4*1024)
                    frame_data = data[:msg_size]
                    data  = data[msg_size:]
                    frame = pickle.loads(frame_data)
                    stream.write(frame)

                except:
                    break

            client_socket.close()

        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(audio_stream)
            executor.submit(video_stream)

    

