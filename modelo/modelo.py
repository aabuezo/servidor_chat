from peewee import DateTimeField, Model, CharField, ForeignKeyField, BooleanField, SqliteDatabase
from datetime import datetime

base_turnos = SqliteDatabase('database/base_turnos.db')

lst_pacientes = ['Alejandro', 'Juan', 'Luis']

especialidades_dict = {
    1: 'Obstetricia',
    2: 'Oftalmologia',
    3: 'Pediatría',
    4: 'Clínica Médica',
    5: 'Cirugia Cardiovascular',
    6: 'Rayos X'
}

turnos_dict = {
    1: 'Lunes',
    2: 'Martes',
    3: 'Miércoles',
    4: 'Jueves',
    5: 'Viernes'
}

turnos_disponibles = {}


class TablaBase(Model):
    timestamp = DateTimeField(default=datetime.now)
    class Meta:
        database = base_turnos


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
    with base_turnos.atomic():
        turno.save()


def test_turnos():
    t = TurnoDisponible()
    t.get_turnos_disponibles()


def crear_database():
    base = base_turnos
    print("abriendo la conexion a la base de datos")
    base.connect()
    print("conectado a la base de datos")
    base.create_tables([Paciente, Especialidad, TurnoDisponible, NuevoTurno])
    print("tablas creadas")
    carga_inicial_datos()
    print("datos iniciales cargados")
    base.close()
    print("base de datos cerrada")


if __name__ == '__main__':
    # crear_database()
    test_turnos()