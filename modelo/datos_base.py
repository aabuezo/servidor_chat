"""
    Autor: Alejandro A. Buezo
    Ultima modificación: 20-11-2021
"""
# datos de la base de datos

from peewee import SqliteDatabase


DATABASE_FILE = 'database/base_turnos.db'
DATABASE = SqliteDatabase(DATABASE_FILE)


# datos para la carga inicial
LISTA_PACIENTES = [
    'Alejandro',
    'Leonardo',
    'Luis',
    'Daniel',
    'Christian',
    'Juan'
]
LISTA_ESPECIALIDADES = [
    'Obstetricia',
    'Oftalmologia',
    'Pediatría',
    'Clínica Médica',
    'Cirugia Cardiovascular',
    'Rayos X',
    'Ginecología',
    'Odontología',
    'Psicología'
]
LISTA_DIAS_TURNOS = [
    'Lunes',
    'Martes',
    'Miércoles',
    'Jueves',
    'Viernes',
    'Sábado'
]