
import cv2
from lib.apiControl import ApiControlRobot
from lib.singleton import SingletonVariables
import socketserver
import socket
import numpy as np
from datetime import datetime

IP_PC, PORT_PC = "192.168.1.44", 9999
IP_ROBOT, PORT_ROBOT  = "192.168.1.40", 9998
PORT_MANDO = 9997

def timestampMilis():
	#Obtener la fecha y hora actual en milisegundos
	hora = datetime.now()
	milis = round(hora.timestamp() * 1000)
	return milis

def millisToBytes(millis):
	#Convertir un int representando los milisegundos desde Epoch a una cadena de 8 bytes.
	return millis.to_bytes(8,byteorder="big")

def bytesToMillis(millisBytes):
	#Convertir una cadena de bytes a un int
	return int.from_bytes(millisBytes, byteorder = "big")

class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """
    def handle(self):
        data = self.request[0]
        
        imgBytes = np.frombuffer(data[:-8], dtype=np.uint8)
        timestampBytes = data[-8:]

        self.server.lastTimestamp = timestampBytes
        

        self.server.img = np.reshape(imgBytes, (8,6))
        self.server.lastPacketTimestamp = millisToBytes(timestampMilis())

        self.server.isTimeout = False
        

        
class MyServer(socketserver.UDPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.timeout = 0.1
        self.img = np.zeros((8,6))
        self.response = 5
        self.isTimeout = False
        self.lastTimestamp = (0).to_bytes(8,byteorder="big")
        self.lastPacketTimestamp = (0).to_bytes(8,byteorder="big")

    def handle_timeout(self):
        self.isTimeout = True


class ApiServer2(ApiControlRobot):
    def __init__(self):
        #Inicializar el robot
        ApiControlRobot.__init__(self, 0,0)

        self.server = MyServer((IP_PC, PORT_PC), MyUDPHandler)
        self.accionActual = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def requestServer(self):
        self.server.handle_request()

    def update(self):
        pass
        #print("Timeout")
    
    def getTime(self):
        time = datetime.now()

        return time.timestamp()


    def getVelocidadBase(self):
        return self.velocBase

    def getModificadorVelocidad(self):
        return self.modificadorVeloc

    def getSensorLinea(self):
        #Obtener si los sensores de linea han detectado la linea
        return False

    def getDatosCamara(self):
        #Obtener la ultima imagen capturada por la camara
        
        return self.server.img
    
    def getResolucionCam(self):
        return (8,6)


    def setMotores(self, izqu, der):
        #Aplicar una velocidad a cada motor
        print("Esto no deberia pasar")
    
    def ejecutarAccion(self, accion):
        print("Enviado: ", accion)
        accionBytes= bytearray(np.array(([accion]), dtype=np.uint8).tobytes())
        dataBytes = bytearray(self.server.lastTimestamp)
        accionBytes.extend(dataBytes)
        dataBytes = bytearray(self.server.lastPacketTimestamp)
        accionBytes.extend(dataBytes)


        self.socket.sendto(accionBytes, (IP_ROBOT, PORT_ROBOT))


    def terminarRobot(self):
        self.server.server_close()