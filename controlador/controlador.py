import socket
import sys
import threading
from modelo.modelo import especialidades_dict, turnos_dict
from decoradores import printlog


class Server:
    def __init__(self, host='localhost', port=3000, cn=10):
        self.nombre = 'Clínica   '
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
            print('Ingrese "salir" para finalizar.\n')
            command = input('-> ')
            if command == 'salir':
                if len(self._lst_clientes) > 0: # si hay clientes activos
                    for c in self._lst_clientes:
                        printlog(c, False)  # no imprime a la pantalla, pero si al log.txt
                        printlog(f'cerrando la conexion con el cliente {c}')
                        c.close()
                sys.exit()

    def atender(self):
        printlog('Esperando conexiones entrantes...\n')
        while True:
            cliente, addr = self._sock.accept()
            self._lst_clientes.append(cliente)
            printlog(f'cliente conectado desde: {addr}')
            printlog(cliente)
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
                printlog(f'estado: {estado}', False)
                if estado == 3:
                    client.close()
                    printlog(f'Se cerro la conexion con el cliente {client}')
                    self._lst_clientes.remove(client)
                    printlog('Se quito al cliente de la lista', False)
                    return

    def responder(self, cliente, estado, data):
        respuesta = ''
        opcion = ''
        nombre = str(data[:10]).strip()
        mensaje = data[10:]
        printlog(str(nombre).rstrip() + ': ' + str(mensaje))
        if estado == 0:     # estado=0 muestro el menu principal
            respuesta = self.menu_especialidades()
            estado += 1
        elif estado == 1:   # estado=1 elige la especialidad
            opcion = int(mensaje)
            printlog(especialidades_dict.keys())
            if opcion in especialidades_dict.keys():
                self.especialidad = especialidades_dict[opcion]
                respuesta = self.menu_turnos()
                estado += 1
            else:
                respuesta = 'Opción inválida. Ingrese su opcion nuevamente'
        elif estado == 2:   # estado=2 elige el turno
            turno = int(mensaje)
            if turno in turnos_dict.keys():
                self.turno = turnos_dict[turno]
                respuesta = f'Le confirmamos su turno:\n' \
                            + f'Paciente: {nombre}\n' \
                            + f'Especialidad: {self.especialidad}\n' \
                            + f'Dia: {self.turno}\n\nLo esperamos!'
                estado += 1
            else:
                respuesta = 'Opción inválida. Ingrese su opcion nuevamente'
        data = self.nombre + respuesta
        packet = data.encode('utf-8')
        cliente.send(packet)
        return estado

    # ver de usar un decorador aqui
    def menu_especialidades(self):
        menu = 'Bienvenido al sistema de turnos_dict\n'
        menu += 'Por favor, elija el número de opcion que desea:\n' \
                + f'1. {especialidades_dict[1]}\n' \
                + f'2. {especialidades_dict[2]}\n' \
                + f'3. {especialidades_dict[3]}\n' \
                + f'4. {especialidades_dict[4]}'
        return menu

    # ver de usar un decorador aqui
    def menu_turnos(self):
        menu = 'Elija su turno:\n'
        menu += '1. Lunes\n2. Martes\n3. Miércoles\n4. Jueves\n5. Viernes'
        return menu


if __name__ == '__main__':
    srv = Server()
