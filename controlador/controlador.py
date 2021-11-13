import socket
import sys
import threading
from modelo.modelo import especialidades, turnos


class Server:
    def __init__(self, host='localhost', port=4000, cn=10):
        self.nombre = 'Catalina  '
        self._lst_clientes = []
        self.turno = ''
        self.especialidad = ''
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind( (host, port))
        self._sock.listen(cn)
        self._serve = threading.Thread(target=self.atender)
        self._serve.daemon = True
        self._serve.start()
        self.consola()

    def consola(self):
        while True:
            command = input('-> ')
            if command == 'salir':
                if len(self._lst_clientes) > 0: # si hay clientes activos
                    for c in self._lst_clientes:
                        print(c)
                        print(f'cerrando la conexion con el cliente {c}')
                        c.close()
                sys.exit()

    def atender(self):
        print('Esperando conexiones!')
        print('Ingrese "salir" para finalizar')
        while True:
            cliente, addr = self._sock.accept()
            self._lst_clientes.append(cliente)
            print(f'cliente conectado desde: {addr}')
            print(cliente)
            # un thread para escuchar al cliente
            cc = threading.Thread(target=self.escuchar, args=(cliente,))
            cc.daemon = True
            cc.start()

    def escuchar(self, client):
        estado = 0
        while True:
            packet = client.recv(1024)
            if packet:
                data = packet.decode('utf-8')
                estado = self.responder(client, estado, data)
                print(f'estado: {estado}')
                if estado == 3:
                    client.close()
                    print('Se cerro la conexion')
                    self._lst_clientes.remove(client)
                    print('Se quito al cliente de la lista')
                    return

    def responder(self, cliente, estado, data):
        respuesta = ''
        opcion = ''
        nombre = data[:10]
        mensaje = data[10]
        print(str(nombre).rstrip() + ': ' + str(mensaje))
        if estado == 0:
            respuesta = self.menu_especialidades()
            estado += 1
        elif estado == 1:   # ya respondio la opcion
            opcion = mensaje
            if opcion in especialidades.keys():
                self.especialidad = especialidades[opcion]
                respuesta = self.menu_turnos()
                estado += 1
            else:
                respuesta = 'Ingrese su opcion nuevamente'
        elif estado == 2:   # ya respondio el turno
            turno = mensaje
            if turno in turnos.keys():
                self.turno = turnos[turno]
                respuesta = f'Le confirmamos su turno de {self.especialidad} para el dia {self.turno}!\nAdiós!'
                estado += 1
            else:
                respuesta = 'Ingrese su opcion nuevamente'
        data = self.nombre + respuesta
        packet = data.encode('utf-8')
        cliente.send(packet)
        return estado

    def menu_especialidades(self):
        menu = 'Bienvenido al sistema de turnos!\n'
        menu += 'Mi nombre es Catalina, por favor, elija la opcion que desea:\n' \
                + f'1. {especialidades["1"]}\n' \
                + f'2. {especialidades["2"]}\n' \
                + f'3. {especialidades["3"]}\n' \
                + f'4. {especialidades["4"]}'
        return menu

    def menu_turnos(self):
        menu = 'Elija su turno:\n'
        menu += '1. Lunes\n2. Martes\n3. Miércoles\n4. Jueves\n5. Viernes'
        return menu


if __name__ == '__main__':
    srv = Server()
