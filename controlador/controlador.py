import socket
import sys
import threading


class Server:
    def __init__(self, host='localhost', port=3000, cn=10):
        self._lst_clientes = []
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind( (host, port))
        self._sock.listen(cn)
        self._serve = threading.Thread(target=self.serve)
        self._serve.daemon = True
        self._serve.start()
        self.console()

    def console(self):
        while True:
            command = input('-> ')
            if command == 'salir':
                if len(self._lst_clientes) > 0: # si hay clientes activos
                    for c in self._lst_clientes:
                        print(c)
                        print(f'cerrando la conexion con el cliente {c}')
                        c.close()
                sys.exit()

    def serve(self):
        print('Esperando conexiones!')
        while True:
            cliente, addr = self._sock.accept()
            self._lst_clientes.append(cliente)
            print(f'cliente conectado desde: {addr}')
            print(cliente)
            cc = threading.Thread(target=self.listen, args=(cliente, ))
            cc.daemon = True
            cc.start()

    def listen(self, client):
        while True:
            packet = client.recv(1024)
            if packet:
                print(packet.decode('utf-8'))
                self.send(client, 'ok')

    def send(self, client, msg):
        packet = msg.encode('utf-8')
        client.send(packet)


if __name__ == '__main__':
    srv = Server()
