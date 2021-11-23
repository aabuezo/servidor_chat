"""
    Servidor Chat-Bot
    Archivo: controlador.py
    Ultima modificación: 23-11-2021
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
    """ clase Server que maneja la conexion con los pacientes (clientes chat) """

    def __init__(self, host=HOST, port=PORT, cn=5):
        """ servidor de turnos """

        self.INICIO = 0
        self.ELIGE_ESPECIALIDAD = 1
        self.ELIGE_TURNO = 2
        self.FIN = 3
        self.especialidad = ''
        self.nombre = 'Clíni-Bot '  # nombre con que responde a los clientes
        self._lst_clientes = []
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.bind((host, port))
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
                if len(self._lst_clientes) > 0:     # si hay clientes activos
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

        estado = self.INICIO
        while True:
            packet = client.recv(1024)
            if packet:
                data = packet.decode('utf-8')
                estado = self.responder(client, estado, data)
                if estado == self.FIN:
                    client.close()
                    printlog(f'Se cerro la conexion con el cliente {client}')
                    self._lst_clientes.remove(client)
                    printlog('Se quito al cliente de la lista', False)
                    return

    def responder(self, cliente, estado, data):
        """ metodo para responder a cada conexión establecida """

        respuesta = ''
        nombre = str(data[:10]).strip()     # la longitud del nombre se establece en 10 caracteres
        mensaje = data[10:]
        printlog(str(nombre).rstrip() + ': ' + str(mensaje))

        if estado == self.INICIO:
            respuesta = self.menu_especialidades()
            estado = self.ELIGE_ESPECIALIDAD
        elif estado == self.ELIGE_ESPECIALIDAD:
            try:
                opcion = int(mensaje)
            except ValueError:
                opcion = 0
            estado, respuesta = self.elegir_especialidad(estado, opcion)
        elif estado == self.ELIGE_TURNO:
            try:
                opcion = int(mensaje)
            except ValueError:
                opcion = 0
            estado, respuesta = self.elegir_turno(estado, opcion, nombre)

        self.enviar_respuesta(cliente, respuesta)
        return estado

    def menu_especialidades(self):
        """ arma el menu de especialidades para el paciente """

        especialidades = Especialidad()
        menu = 'Bienvenido al sistema de turnos!\n'
        menu += 'Por favor, elija el número de opcion que desea:\n'
        menu += especialidades.get_lista_especialidades()
        return menu

    def menu_turnos(self):
        """ arma el menu de turnos disponibles para el paciente """

        turnos = TurnoDisponible()
        menu = 'Elija su turno:\n'
        menu += turnos.get_turnos_disponibles()
        return menu

    def elegir_especialidad(self, estado, opcion):
        """ valida y guarda la eleccion de la especialidad elegida por el paciente """

        esp = Especialidad()
        esp_ids = esp.get_lista_ids()
        printlog(esp_ids)
        if estado == self.ELIGE_ESPECIALIDAD and opcion in esp_ids:
            self.especialidad = esp.get_especialidad(opcion)
            respuesta = self.menu_turnos()
            estado = self.ELIGE_TURNO
        else:
            respuesta = 'Opción inválida.\nIngrese su opcion nuevamente'
        return estado, respuesta

    def elegir_turno(self, estado, opcion, nombre):
        """ valida el turno elegido por el paciente y lo reserva """

        td = TurnoDisponible()
        turnos_ids = td.get_lista_ids()
        printlog(turnos_ids)
        if len(turnos_ids) == 0:    # no hay mas turnos disponibles
            respuesta = 'Lamento comunicarle que no hay mas turnos disponibles.\n' \
            'Por favor vuelva a comunicarse en otro momento.\n'
            estado = self.FIN
        elif estado == self.ELIGE_TURNO and opcion in turnos_ids:
            turno = td.get_turno(opcion)
            if self.reservar_turno(nombre, turno):
                respuesta = f'Le confirmamos su turno:\n' \
                            + f'Paciente: {nombre}\n' \
                            + f'Especialidad: {self.especialidad}\n' \
                            + f'Dia: {turno}\n\nLo esperamos!'
                estado = self.FIN
            else:
                respuesta = f'No es posible reservar el turno.\n' \
                            + 'Comuníquese nuevamente'
        else:
            respuesta = 'Opción inválida.\nIngrese su opcion nuevamente'
        return estado, respuesta

    def reservar_turno(self, nombre, turno):
        """ reserva el turno elegido por el paciente """
        if self.especialidad == '':
            return False
        esp = Especialidad()
        pac = Paciente()
        tur = TurnoDisponible()
        nombre_id = pac.get_id(nombre)
        esp_id = esp.get_id(self.especialidad)
        turno_id = tur.get_id(turno)
        nt = NuevoTurno()
        nt.guardar_turno(nombre_id, esp_id, turno_id)
        return True

    def enviar_respuesta(self, cliente, respuesta):
        """ envia la respuesta al paciente """

        data = self.nombre + respuesta
        packet = data.encode('utf-8')
        try:
            cliente.send(packet)
        except socket.error:
            # aunque se  pedio la conexion con el paciente,
            # el turno ya se reservo, por eso no hacemos rollback
            pass


if __name__ == '__main__':
    srv = Server()
