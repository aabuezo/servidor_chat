from modelo.datos_base import DATABASE, LISTA_PACIENTES, LISTA_ESPECIALIDADES, LISTA_DIAS_TURNOS
from peewee import DateTimeField, Model, CharField, ForeignKeyField, BooleanField
from datetime import datetime
from decoradores import printlog

especialidades_dict = {}
turnos_dict = {}
especialidades_dict_orig = {
    1: 'Obstetricia',
    2: 'Oftalmologia',
    3: 'Pediatría',
    4: 'Clínica Médica',
    5: 'Cirugia Cardiovascular',
    6: 'Rayos X'
}

turnos_dict_orig = {
    1: 'Lunes',
    2: 'Martes',
    3: 'Miércoles',
    4: 'Jueves',
    5: 'Viernes'
}


class TablaBase(Model):
    timestamp = DateTimeField(default=datetime.now)
    class Meta:
        database = DATABASE


class Paciente(TablaBase):
    paciente = CharField(null=False)

    def get_id(self, nombre):
        return Paciente.get(Paciente.paciente == nombre).id


class Especialidad(TablaBase):
    especialidad = CharField(null=False)

    def get_lista_especialidades(self):
        query = Especialidad().select()
        especialidades = ''
        for registro in query:
            especialidades += f'{registro.id}. {registro.especialidad}\n'
        return especialidades

    def get_lista_ids(self):
        query = Especialidad().select()
        lst_esp = []
        for registro in query:
            lst_esp.append(registro.id)
        return lst_esp

    def get_especialidad(self, id):
        # query = Especialidad().select().where(id==id)
        # print(query)
        return Especialidad.get_by_id(id).especialidad

    def get_id(self, esp):
        return Especialidad.get(Especialidad.especialidad == esp).id


class TurnoDisponible(TablaBase):
    turno = CharField(null=False)
    disponible = BooleanField(default=True)

    def get_turnos_disponibles(self):
        query = TurnoDisponible().select().where(TurnoDisponible.disponible==True)
        turnos = ''
        for registro in query:
            turnos += f'{registro.id}. {registro.turno}\n'
        return turnos

    def get_lista_ids(self):
        query = TurnoDisponible().select().where(TurnoDisponible.disponible == True)
        lst_turnos = []
        for registro in query:
            lst_turnos.append(registro.id)
        return lst_turnos

    def get_turno(self, id):
        # query = TurnoDisponible().select().where(id==id)
        # return query.turno
        return TurnoDisponible.get_by_id(id).turno

    def get_id(self, dia):
        return TurnoDisponible.get(TurnoDisponible.turno == dia).id


class NuevoTurno(TablaBase):
    paciente = ForeignKeyField(Paciente, backref='paciente_id')
    especialidad = ForeignKeyField(Especialidad, backref='especialidad_id')
    turno = ForeignKeyField(TurnoDisponible, backref='turno_id')

    def guardar_turno(self, nombre_id, especialidad_id, turno_id):
        nt = NuevoTurno.create(paciente=nombre_id, especialidad=especialidad_id, turno=turno_id)
        # td = TurnoDisponible()
        query = TurnoDisponible.update(disponible=False).where(TurnoDisponible.id == turno_id)
        printlog(query)
        query.execute()


def carga_inicial_datos():
    with DATABASE.atomic():
        for value in LISTA_PACIENTES:
            Paciente.create(paciente=value).save()
        for value in LISTA_ESPECIALIDADES:
            Especialidad.create(especialidad=value).save()
        for value in LISTA_DIAS_TURNOS:
            TurnoDisponible.create(turno=value).save()


def crear_database():
    with DATABASE:
        printlog("conectado a la base de datos", False)
        DATABASE.create_tables([Paciente, Especialidad, TurnoDisponible, NuevoTurno])
        printlog("tablas creadas", False)
        carga_inicial_datos()
        printlog("datos iniciales cargados", False)


if __name__ == '__main__':
    pass


