import socket
import threading
import random
import numpy as np
import time

def servir(socketTcp):
    try:
        gestion_conexiones()
        client_conn, client_addr = socketTcp.accept()
        print("Conectado a", client_addr)
        global listaconexiones
        listaconexiones.append(client_conn)
        gestion_conexiones()
        if len(listaconexiones) == 1:
            msg_in_btyes = 'Bienvenido al buscaminas, inserta "F" para facil y "D" para dificil\nPara salir inserta "end"'
            msg_in_btyes = msg_in_btyes.encode('utf-8')  # Transforma de stringa a bytes
        else:
            msg_in_btyes = 'Bienvenido al buscaminas, otro cliente esta elgiendo dificultad'
            msg_in_btyes = msg_in_btyes.encode('utf-8')
        client_conn.sendall(msg_in_btyes) # Bienvenida
        thread = threading.Thread(target=entrar_partida, args=[client_conn])
        thread.start()
    except Exception as e:
        print(e)


def gestion_conexiones():
    global listaconexiones
    for conn in listaconexiones:
        if conn.fileno() == -1:
            listaconexiones.remove(conn)
    print("------------------------------------------------------")
    print("hilos activos:", threading.active_count())
    print("enum", threading.enumerate())
    print("conexiones: ", len(listaconexiones))
    print(listaconexiones)
    print("------------------------------------------------------\n")

def entrar_partida(client_conn: socket.socket):
    
    global matriz
    global num_casillas
    global casillas_abiertas
    global dif

    while len(listaconexiones) > 1 and num_casillas == 0:
        time.sleep(0.001)        

    if num_casillas == 0:
        data = client_conn.recv(buffer_size).decode('utf-8')  #Mensaje con la dificultad
        matriz = crear_matriz(data)
        dif = data
        print(matriz[0])
        while not matriz[1] and not (data == "end" or data == ""):
            client_conn.sendall(matriz[0].encode('utf-8'))
            data = client_conn.recv(buffer_size).decode('utf-8')
            dif = data
            matriz = crear_matriz(data)
        if data == "end" or data == "":
            print("\nDesconectandose del cliente...")
            client_conn.close()
            return
        if data == "F" :
            num_casillas = 71
        else :
            num_casillas = 216
    if num_casillas != 0:
        data = dif + ',Para seleccionar una casilla inserta Fila, Columna\nEjemplo: 6,9 \n'
        client_conn.sendall(data.encode('utf-8'))
        casillas_abiertas = 0
        # ----------- Empieza a jugar -----------
        state_game: str
        while True: 
            data = client_conn.recv(buffer_size).decode('utf-8')
            state_game = jugar(matriz[0], data)   
            casillas_abiertas = casillas_abiertas + 1
            if state_game == "Perdiste":
                client_conn.sendall(b'Perdiste')
                matriz = 0 
                num_casillas = 0
                casillas_abiertas = 0
                break
            elif state_game == "Bien":
                client_conn.sendall(b'Bien')
            else:
                client_conn.sendall(b'Casilla ocupada')
            if casillas_abiertas == num_casillas:
                client_conn.sendall(b'Ganaste')
                matriz = 0 
                num_casillas = 0
                casillas_abiertas = 0
                dif = 0
                print(data)
                break
    print("Se cerro el socket")
    client_conn.close()

def jugar(matriz: np.ndarray, casilla:str):
    posicion = casilla.split(",")
    if matriz[int(posicion[0])-1][int(posicion[1])-1] == 0:
        matriz[int(posicion[0])-1][int(posicion[1])-1] = 2
        print("Bien")
        return "Bien"
    elif matriz[int(posicion[0])-1][int(posicion[1])-1] == 2:
        print("Casilla ocupada")
        return "Casilla ocupada"
    else:
        print("Perdiste")
        return "Perdiste"
    
def crear_matriz(dificultad: str):
    if dificultad == "F" :
        size = 9
        minas = 10
    elif dificultad == "D" :
        size = 16
        minas = 40
    else:
        return 'Opcion no valida, inserta "F" para facil y "D" para dificil\nPara salir pon "end"', False
    matriz = np.zeros((size,size))
    count = 1
    while count <= minas :
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        
        if matriz[x][y] == 0 :
            matriz[x][y] = 1
            count = count + 1
    return matriz, True


# ---------------------------Main------------------
#print("Incerta la ip del servidor")
HOST = "127.0.0.1"
PORT = 54321 
buffer_size = 1024
listaconexiones = []
matriz = ()
num_casillas = 0
casillas_abiertas = 0
dif = 0


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT)) 
    server_socket.listen(2)
    print("Servidor de Buscaminas activo, esperando peticiones\n")
    servir(server_socket)
