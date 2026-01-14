import socket
import pickle


class Network:

    def __init__(self):

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5556
        self.addr = (self.server, self.port)

    def connect(self, data):

        try:
            self.client.connect(self.addr)
            self.client.sendall(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048))

        except:
            return {"verdict": "Connection refused."}

    def send(self, data):

        try:
            self.client.sendall(pickle.dumps(data))
            return pickle.loads(self.client.recv(4096*2))

        except (socket.error, EOFError):
            return None
