# datos de la base de datos
import os
from peewee import SqliteDatabase

DATABASE_FILE = 'database/base_turnos.db'
DATABASE = SqliteDatabase(DATABASE_FILE)


# datos para la carga inicial
LISTA_PACIENTES = ['Alejandro', 'Juan', 'Luis']
LISTA_ESPECIALIDADES = [
    'Obstetricia',
    'Oftalmologia',
    'Pediatría',
    'Clínica Médica',
    'Cirugia Cardiovascular',
    'Rayos X'
]
LISTA_DIAS_TURNOS = [
    'Lunes',
    'Martes',
    'Miércoles',
    'Jueves',
    'Viernes'
]