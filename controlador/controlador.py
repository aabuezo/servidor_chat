"""
    Autor: Alejandro A. Buezo
    Ultima modificación: 20-11-2021
"""
import socket
import sys
import threading
from decoradores import printlog
from modelo.modelo import TurnoDisponible, Especialidad, NuevoTurno, Paciente

# si el servidor se ejecuta en otra maquina, recordar cambiar por la IP del servidor entre comillas 
# recordar habilitar el PORT en el firewall del servidor
HOST = 'localhost'
PORT = 3000


class Server:
    """ clase Server que maneja la conexion con los clientes """

    def __init__(self, host=HOST, port=PORT, cn=5):
        """ servidor de turnos """

        self.nombre = 'Clínica   '  # el que responde a los clientes
        self._lst_clientes = []
        self.turno = ''
        self.especialidad = ''
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind( (host, port))
        self._sock.listen(cn)
        self._atender = threading.Thread(target=self.atender)
        self._atender.daemon = True
        self._atender.start()
        self.consola()

    def consola(self):
        """ consola del servidor """

        while True:
            print('Ingrese "salir" para finalizar.\n')
            command = input('-> ')
            if command.lower() == 'salir':
                printlog('Apagando el servidor...\n', True)
                if len(self._lst_clientes) > 0: # si hay clientes activos
                    for c in self._lst_clientes:
                        printlog(f'cerrando la conexion con el cliente {c}')
                        c.close()
                sys.exit()

    def atender(self):
        """ metodo para atender las conexiones entrantes """

        printlog('Esperando conexiones entrantes...\n')
        print('\n')
        while True:
            cliente, addr = self._sock.accept()
            self._lst_clientes.append(cliente)
            printlog(f'cliente conectado desde: {addr}')
            printlog(cliente, False)
            # un nuevo thread para escuchar al cliente que se acaba de conectar
            cc = threading.Thread(target=self.escuchar, args=(cliente,))
            cc.daemon = True
            cc.start()

    def escuchar(self, client):
        """ metodo para escuchar a cada conexion establecida """

        estado = 0  # estado=0 conexión recien establecida
        while True:
            packet = client.recv(1024)
            if packet:
                data = packet.decode('utf-8')
                estado = self.responder(client, estado, data)
                if estado == 3: # estado=3 ya se otorgo el turno, cerrar la conexion con el cliente
                    client.close()
                    printlog(f'Se cerro la conexion con el cliente {client}')
                    self._lst_clientes.remove(client)
                    printlog('Se quito al cliente de la lista', False)
                    return

    def responder(self, cliente, estado, data):
        """ metodo para responder a cada conexión establecida """

        respuesta = ''
        nombre = str(data[:10]).strip() # la longitud del nombre se establece en 10 caracteres
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
        """ arma el menu de especialidades para el cliente """

        especialidades = Especialidad()
        menu = 'Bienvenido al sistema de turnos!\n'
        menu += 'Por favor, elija el número de opcion que desea:\n'
        menu += especialidades.get_lista_especialidades()
        return menu

    def menu_turnos(self):
        """ arma el menu de turnos disponibles para el cliente """

        turnos = TurnoDisponible()
        menu = 'Elija su turno:\n'
        menu += turnos.get_turnos_disponibles()
        return menu

    def elegir_especialidad(self, estado, opcion):
        """ valida y guarda la eleccion de la especialidad elegida por el paciente """

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
        """ valida el turno elegido por el cliente y lo reserva """

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
        """ reserva el turno elegido por el cliente """

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
        """ envia la respuesta al cliente """

        data = self.nombre + respuesta
        packet = data.encode('utf-8')
        try:
            cliente.send(packet)
        except socket.error:
            # aunque se  pedio la conexion con el cliente,
            # el turno ya se reservo, por eso no hacemos rollback
            pass


if __name__ == '__main__':
    srv = Server()
