from controlador.controlador import Server
from modelo.modelo import crear_database

if __name__ == '__main__':
    crear_database()
    app = Server()
