"""
    Servidor Chat-Bot
    Archivo: main.py
    Ultima modificación: 23-11-2021
"""
import os
from controlador.controlador import Server
from modelo.datos_base import DATABASE_FILE
from modelo.modelo import crear_database

if __name__ == '__main__':
    if not os.path.exists(DATABASE_FILE):
        crear_database()    # si no existe la BD, la crea
    app = Server()
