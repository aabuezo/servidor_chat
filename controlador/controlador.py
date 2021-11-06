import socket
import sys
import threading


class Server:
    def __init__(self, host='localhost', port=3000, cn=2):
        self._lst_clientes = []
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind( (host, port))
        self._sock.listen(cn)
        # self._sock.setblocking(False)
        self._serve = threading.Thread(target=self.serve)
        self._serve.daemon = True
        self._serve.start()
        self.console()

    def console(self):
        while True:
            command = input('-> ')
            if command == 'salir':
                for c in self._lst_clientes:
                    print(c)
                    c.close()
                sys.exit()

    def serve(self):
        while True:
            conn, addr = self._sock.accept()
            # conn.setblocking(False)sa
            self._lst_clientes.append(conn)
            print(f'cliente conectado desde: {addr}')
            self.listen(conn) # listen_to_all y hacerlo thread!!!

    def listen(self, client):
        packet = client.recv(1024)
        if packet:
            print(packet.decode('utf-8'))
            self.send(client, 'ok')
        # self._sock.close()

    def send(self, client, msg):
        packet = msg.encode('utf-8')
        client.send(packet)


if __name__ == '__main__':
    srv = Server()
