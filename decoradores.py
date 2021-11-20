

def log_to_file(funcion):
    def guardar_archivo_logs(*args):
        funcion(*args)
        with open("logfiles/logs.txt", "a") as f:
            f.write(str(args))
            f.write('\n')
    return guardar_archivo_logs


@log_to_file
def printlog(info, to_screen=True):
    if to_screen:
        print(str(info))


