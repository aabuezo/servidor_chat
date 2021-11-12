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
            # un thread para escuchar al cliente
            cc = threading.Thread(target=self.listen, args=(cliente, ))
            cc.daemon = True
            cc.start()

    def listen(self, client):
        estado = 0
        while True:
            packet = client.recv(1024)
            if packet:
                data = packet.decode('utf-8')
                respuesta = self.responder(client, estado, data)
                estado += 1

    def send(self, client, msg):
        nombre = 'Catalina  '
        data = nombre + msg
        packet = data.encode('utf-8')
        client.send(packet)

    def responder(self, cliente, estado, data):
        respuesta = ''
        opcion = 0
        turno = 0
        nombre = data[:10]
        mensaje = data[10:]
        print(str(nombre).rstrip() + ': ' + str(mensaje))
        if estado == 0:
            respuesta = 'Bienvenido al sistema de turnos!\nMi nombre es Catalina, por favor, elija la opcion que desea:\n' + '1. Oftalmologia\n' + '2. Pediatría\n' + '3. Obstetricia\n' + '4. Ginecología'
        elif estado == 1:   # respondio la opcion
            opcion = mensaje[0]
            respuesta = 'Elija su turno:\n1. Lunes\n2. Martes\n3. Miércoles\n4. Jueves\n5. Viernes\n'
        elif estado == 2:   # responde el turno
            turno = mensaje[0]
            respuesta = f'Le confirmo su turno de {opcion} para el dia {turno}\n'
        self.send(cliente, respuesta)


if __name__ == '__main__':
    srv = Server()
