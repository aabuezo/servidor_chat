

def log(funcion):
    def guardar_archivo_logs(*args, **kwargs):
        mi_print(*args, **kwargs)
        file = open("logs.txt", "a")
        file.write(*args, **kwargs)
        file.close()
    return guardar_archivo_logs


@log
def mi_print(info):
    print(info)


mi_print("hola mundo!")
