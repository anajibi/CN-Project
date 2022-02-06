from email import message
from unicodedata import name
import numpy as np
import cv2, imutils, socket, time, base64, threading, wave, pyaudio, pickle, struct, sys, os, queue
from concurrent.futures import ThreadPoolExecutor


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
        'mahmooti' : '2.mp4',
        'keyhan kalhor' : '3.mp4'
    }

    audio = {
        'behdad babaei' : '1.wav',
        'mahmooti' : '2.wav'
    }

    publish: socket.socket
    online_delivery: socket.socket

    def __init__(self):
        self.publish = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.publish.bind((URL, SERVER_PORT_INFO))
        self.publish.listen()
        self.online_video_delivery = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.online_video_delivery.bind((URL, SERVER_STREAM_PORT))
        self.online_audio_delivery = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.online_audio_delivery.bind((URL, SERVER_STREAM_PORT))
        self.online_audio_delivery.listen()


    def video_stream_gen(self, vid, q):
        print('video_stream_gen')
        WIDTH = 400
        while vid.isOpened():
            try:
                _, frame = vid.read()
                frame = imutils.resize(frame, width=WIDTH)
                q.put(frame)
            except:
                os._exit(1)
        vid.release()

    def video_stream(self, client_addr, FPS, q):
        print('video_stream')
        fps, st, frames_to_count, cnt = 0, 0, 1, 0
        cv2.namedWindow('TRANSMITTING VIDEO')
        cv2.moveWindow('TRANSMITTING VIDEO', 10, 30)
        TS = 0.5 / FPS
        while True:
            frame = q.get()
            encoded, buffer = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            message = base64.b64encode(buffer)
            self.online_video_delivery.sendto(message, client_addr)
            frame = cv2.putText(frame, 'FPS: ' + str(round(fps, 1)), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            if cnt == frames_to_count:
                try:
                    fps = frames_to_count / (time.time() - st)
                    st = time.time()
                    cnt = 0
                    if fps > FPS:
                        TS += 0.001
                    elif fps < FPS:
                        TS -= 0.001
                    else:
                        pass
                except:
                    pass
            cnt += 1
            cv2.imshow('TRANSMITTING VIDEO', frame)
            key = cv2.waitKey(int(1000 * TS)) & 0xFF
            if key == ord('q'):
                os._exit(1)

    def audio_stream(self, name, client_socket):
        print('audio_stream')
        CHUNK = 1024
        wf = wave.open(self.audio[name], 'rb')
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()), channels=wf.getnchannels(), rate=wf.getframerate(), input=True, frames_per_buffer=CHUNK)
        if client_socket:
            while True:
                data = wf.readframes(CHUNK)
                serialized = pickle.dumps(data)
                message = struct.pack('Q', len(serialized)) + serialized
                client_socket.sendall(message)


    def send_stream(self, name, conn, client_addr):
        print('send_stream')
        q = queue.Queue(maxsize=10)
        vid = cv2.VideoCapture(self.media[name])
        FPS = vid.get(cv2.CAP_PROP_FPS)
        with ThreadPoolExecutor(max_workers=3) as executor:
                    executor.submit(self.video_stream_gen, vid,q)
                    executor.submit(self.video_stream, client_addr, FPS, q)
                    executor.submit(self.audio_stream, name, conn)

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
            msg, addr = self.online_video_delivery.recvfrom(1024)
            print('udp socket')
            conn, _ = self.online_audio_delivery.accept()
            print('tcp socket')
            threading.Thread(target=self.send_stream, args=(msg.decode('ascii'), conn, addr)).start()

    def start(self):
        """
        calls online_delivery UDP service.
        :return:
        """
        threading.Thread(target=self.acc_publish, args=()).start()
        threading.Thread(target=self.acc_online_delivery, args=()).start()


MediaServer().start()
