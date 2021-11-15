from peewee import SqliteDatabase, DateTimeField, Model, CharField, ForeignKeyField, BooleanField
from datetime import date, datetime

db = SqliteDatabase('../database/data.db')

lst_pacientes = ['Alejandro', 'Juan', 'Luis']

especialidades_dict = {
    1: 'Obstetricia',
    2: 'Oftalmologia',
    3: 'Pediatría',
    4: 'Clínica Médica'
}

turnos_dict = {
    1: 'Lunes',
    2: 'Martes',
    3: 'Miércoles',
    4: 'Jueves',
    5: 'Viernes'
}


class TablaBase(Model):
    timestamp = DateTimeField(default=datetime.now)
    class Meta:
        database = db

class Paciente(TablaBase):
    paciente = CharField(null=False)


class Especialidad(TablaBase):
    especialidad = CharField(null=False)

    def get_especialidades(self):
        pass


class TurnoDisponible(TablaBase):
    turno = CharField(null=False)
    disponible = BooleanField(default=True)

    def get_turnos_disponibles(self):
        pass


class NuevoTurno(TablaBase):
    paciente = ForeignKeyField(Paciente, backref='paciente_id')
    especialidad = ForeignKeyField(Especialidad, backref='especialidad_id')
    turno = ForeignKeyField(TurnoDisponible, backref='turno_id')


def carga_inicial_datos():
    for value in lst_pacientes:
        paciente = Paciente.create(paciente=value)
        paciente.save()
    for value in especialidades_dict.values():
        especialidad = Especialidad.create(especialidad=value)
        especialidad.save()
    for value in turnos_dict.values():
        turno_disponible = TurnoDisponible.create(turno=value)
        turno_disponible.save()


def crear_turno(turno):
    with db.atomic():
        turno.save()


if __name__ == '__main__':
    db.connect()
    db.create_tables([Paciente, Especialidad, TurnoDisponible, NuevoTurno])
    carga_inicial_datos()
    db.close()
    # nuevo_turno = NuevoTurno(paciente='Alejandro', especialidad=especialidades_dict['2'], turno=turnos_dict['1'])
    # crear_turno(nuevo_turno)