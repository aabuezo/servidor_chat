import socket
import sys
import threading
from modelo.modelo import especialidades_dict, turnos_dict, TurnoDisponible, Especialidad, NuevoTurno, Paciente
from decoradores import printlog


class Server:
    def __init__(self, host='localhost', port=6003, cn=10):
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
            if command.lower() == 'salir':
                if len(self._lst_clientes) > 0: # si hay clientes activos
                    for c in self._lst_clientes:
                        printlog(c, False)  # no imprime a la pantalla, pero si al log.txt
                        printlog(f'cerrando la conexion con el cliente {c}')
                        c.close()
                sys.exit()

    def atender(self):
        printlog('Esperando conexiones entrantes...')
        print('\n')
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
        nombre = str(data[:10]).strip()
        mensaje = data[10:]
        printlog(str(nombre).rstrip() + ': ' + str(mensaje))
        if estado == 0:     # estado=0 muestra el menu principal
            respuesta = self.menu_especialidades()
            estado += 1
        elif estado == 1:   # estado=1 elige la especialidad
            opcion = int(mensaje)
            estado, respuesta = self.elegir_especialidad(estado, opcion)
        elif estado == 2:   # estado=2 elige el turno
            opcion = int(mensaje)
            estado, respuesta = self.elegir_turno(estado, opcion, nombre)

        self.enviar_respuesta(cliente, respuesta)
        return estado

    def menu_especialidades(self):
        especialidades = Especialidad()
        menu = 'Bienvenido al sistema de turnos_dict\n'
        menu += 'Por favor, elija el número de opcion que desea:\n'
        menu += especialidades.get_lista_especialidades()
        return menu

    def menu_turnos(self):
        turnos = TurnoDisponible()
        menu = 'Elija su turno:\n'
        menu += turnos.get_turnos_disponibles()
        return menu

    def elegir_especialidad(self, estado, opcion):
        esp = Especialidad()
        esp_ids = esp.get_lista_ids()
        printlog(esp_ids)
        if opcion in esp_ids:
            self.especialidad = esp.get_especialidad(opcion)
            respuesta = self.menu_turnos()
            estado += 1
        else:
            respuesta = 'Opción inválida.\nIngrese su opcion nuevamente'
        return (estado, respuesta)

    def elegir_turno(self, estado, opcion, nombre):
        td = TurnoDisponible()
        turnos_ids = td.get_lista_ids()
        printlog(turnos_ids)
        if opcion in turnos_ids:
            self.turno = td.get_turno(opcion)
            if self.reservar_turno(nombre) == True:
                respuesta = f'Le confirmamos su turno:\n' \
                            + f'Paciente: {nombre}\n' \
                            + f'Especialidad: {self.especialidad}\n' \
                            + f'Dia: {self.turno}\n\nLo esperamos!'
                estado += 1
            else:
                respuesta = f'El turno ya no esta disponible'
        else:
            respuesta = 'Opción inválida.\nIngrese su opcion nuevamente'
        return (estado, respuesta)

    def reservar_turno(self, nombre):
        esp = Especialidad()
        pac = Paciente()
        tur = TurnoDisponible()
        nombre_id = pac.get_id(nombre)
        esp_id = esp.get_id(self.especialidad)
        turno_id = tur.get_id(self.turno)
        nt = NuevoTurno()
        nt.guardar_turno(nombre_id, esp_id, turno_id)
        return True

    def enviar_respuesta(self, cliente, respuesta):
        data = self.nombre + respuesta
        packet = data.encode('utf-8')
        cliente.send(packet)


if __name__ == '__main__':
    srv = Server()
