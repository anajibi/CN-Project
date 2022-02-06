import socket, cv2, pickle, struct

IP, port = '127.0.0.1', 4030

publish = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

publish.connect((IP, port))
msg = publish.recv(1024)
print(msg.decode('ascii'))

payload_size = struct.calcsize('Q')

stream.connect((IP, port+1))
stream.sendall(b'behdad babaei')
data = b''
while True:
    while len(data) < payload_size:
        packet = stream.recv(4096)
        if not packet:
            break
        data += packet
    frame_size = struct.unpack('Q', data[:payload_size])[0]
    data = data[payload_size:]
    while len(data) < frame_size:
        packet= stream.recv(4096)
        data += packet
    serialized_frame = data[:frame_size]
    data = data[frame_size:]
    frame = pickle.loads(serialized_frame)
    cv2.imshow('behdad babaei', frame)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

publish.close()
stream.close()
cv2.destroyAllWindows()
