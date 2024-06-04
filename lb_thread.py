import socket
import threading
import logging

class BackendList:
    def __init__(self):
        self.servers = []
        self.servers.append(('127.0.0.1', 8000))
        self.servers.append(('127.0.0.1', 8001))
        self.servers.append(('127.0.0.1', 8002))
        self.servers.append(('127.0.0.1', 8003))
        self.servers.append(('127.0.0.1', 8004))
        self.current = 0

    def getserver(self):
        s = self.servers[self.current]
        self.current = self.current + 1
        if self.current >= len(self.servers):
            self.current = 0
        return s


class Backend:
    def __init__(self, targetaddress, client_socket):
        self.targetaddress = targetaddress
        self.client_socket = client_socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect(targetaddress)
        threading.Thread(target=self.handle).start()

    def handle(self):
        try:
            while True:
                data = self.server_socket.recv(1024)
                if not data:
                    break
                self.client_socket.sendall(data)
        finally:
            self.server_socket.close()
            self.client_socket.close()


class ProcessTheClient:
    def __init__(self, client_socket, backend_address):
        self.client_socket = client_socket
        self.backend_address = backend_address
        self.backend = Backend(backend_address, client_socket)
        threading.Thread(target=self.handle).start()

    def handle(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                self.backend.server_socket.sendall(data)
        finally:
            self.client_socket.close()


class Server:
    def __init__(self, portnumber):
        self.portnumber = portnumber
        self.bservers = BackendList()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', portnumber))
        self.server_socket.listen(5)
        logging.warning(f"Load balancer thread running on port {portnumber}")
        self.run()

    def run(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            logging.warning(f"Connection from {addr}")
            backend_address = self.bservers.getserver()
            logging.warning(f"Koneksi dari {addr} diteruskan ke {backend_address}")
            ProcessTheClient(client_socket, backend_address)


def main():
    portnumber = 55555
    try:
        portnumber = int(sys.argv[1])
    except:
        pass
    Server(portnumber)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
