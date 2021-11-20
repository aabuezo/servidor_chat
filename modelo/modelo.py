"""
    Autor: Alejandro A. Buezo
    Ultima modificación: 20-11-2021
"""
from modelo.datos_base import DATABASE, LISTA_PACIENTES, LISTA_ESPECIALIDADES, LISTA_DIAS_TURNOS
from peewee import DateTimeField, Model, CharField, ForeignKeyField, BooleanField
from datetime import datetime
from decoradores import printlog


class TablaBase(Model):
    """ contiene el timestamp y la class Meta para
        todas las subclases """
    timestamp = DateTimeField(default=datetime.now)
    class Meta:
        database = DATABASE


class Paciente(TablaBase):
    """ pacientes en la BD """
    paciente = CharField(null=False)

    def get_id(self, nombre):
        return Paciente.get(Paciente.paciente == nombre).id


class Especialidad(TablaBase):
    """ especialidades en la BD """
    especialidad = CharField(null=False)

    def get_lista_especialidades(self):
        """ obtiene la lista de especialidades disponibles """

        query = Especialidad().select()
        especialidades = ''
        for registro in query:
            especialidades += f'{registro.id}. {registro.especialidad}\n'
        return especialidades

    def get_lista_ids(self):
        """ devuelve una lista con los id de las especialidades """

        query = Especialidad().select()
        lst_esp = []
        for registro in query:
            lst_esp.append(registro.id)
        return lst_esp

    def get_especialidad(self, id):
        """ obtiene una especialidad a partir de un id"""
        return Especialidad.get_by_id(id).especialidad

    def get_id(self, esp):
        """ obtiene un id a partir de una especialidad """
        return Especialidad.get(Especialidad.especialidad == esp).id


class TurnoDisponible(TablaBase):
    """ clase que contiene la lista de turnos disponibles de la BD """
    turno = CharField(null=False)
    disponible = BooleanField(default=True)

    def get_turnos_disponibles(self):
        """ devuelve un string con los turnos disponibles en la BD
            (que aún no se otorgaron) """
        query = TurnoDisponible().select().where(TurnoDisponible.disponible==True)
        turnos = ''
        for registro in query:
            turnos += f'{registro.id}. {registro.turno}\n'
        return turnos

    def get_lista_ids(self):
        """ obtiene la lisa de id de los turnos disponibles en la BD """
        query = TurnoDisponible().select().where(TurnoDisponible.disponible == True)
        lst_turnos = []
        for registro in query:
            lst_turnos.append(registro.id)
        return lst_turnos

    def get_turno(self, id):
        """ devuelve el dia correspondiente al id """
        return TurnoDisponible.get_by_id(id).turno

    def get_id(self, dia):
        """ devuelve el id según el día """
        return TurnoDisponible.get(TurnoDisponible.turno == dia).id


class NuevoTurno(TablaBase):
    """ clase que representa un turno otorgado y guardado en la BD """

    paciente = ForeignKeyField(Paciente, backref='paciente_id')
    especialidad = ForeignKeyField(Especialidad, backref='especialidad_id')
    turno = ForeignKeyField(TurnoDisponible, backref='turno_id')

    def guardar_turno(self, nombre_id, especialidad_id, turno_id):
        """ reserva el turno en la BD y marca como ya no disponible para otros el turno otorgado """

        nt = NuevoTurno.create(paciente=nombre_id, especialidad=especialidad_id, turno=turno_id)
        # td = TurnoDisponible()
        query = TurnoDisponible.update(disponible=False).where(TurnoDisponible.id == turno_id)
        printlog(query)
        query.execute()


def carga_inicial_datos():
    """ funcion para la carga inicial de datos en la BD """

    with DATABASE.atomic():
        for value in LISTA_PACIENTES:
            Paciente.create(paciente=value).save()
        for value in LISTA_ESPECIALIDADES:
            Especialidad.create(especialidad=value).save()
        for value in LISTA_DIAS_TURNOS:
            TurnoDisponible.create(turno=value).save()


def crear_database():
    """ funcion para crear la BD y las tablas """

    with DATABASE:
        printlog("conectado a la base de datos", False)
        DATABASE.create_tables([Paciente, Especialidad, TurnoDisponible, NuevoTurno])
        printlog("tablas creadas", False)
        carga_inicial_datos()
        printlog("datos iniciales cargados", False)


if __name__ == '__main__':
    """ ejecutar desde main.py """
    pass


