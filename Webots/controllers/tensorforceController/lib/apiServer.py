
import cv2
from lib.apiControl import ApiControlRobot
from lib.singleton import SingletonVariables
import socketserver
import socket
import numpy as np
from datetime import datetime

IP_PC, PORT_PC = "192.168.1.44", 9999
IP_ROBOT, PORT_ROBOT  = "192.168.1.38", 9998
class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """
    def handle(self):
        data = self.request[0]
        
        img = np.frombuffer(data, dtype=np.uint8)
        #print(img)
        #print("{} wrote:".format(self.client_address[0]))
        #print(data)

        self.server.img = np.reshape(img, (8,6))
        

        
class MyServer(socketserver.UDPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.timeout = 1
        self.img = np.zeros((8,6))
        self.response = 5


class ApiServer(ApiControlRobot):
    def __init__(self):
        #Inicializar el robot
        ApiControlRobot.__init__(self, 0,0)

        self.server = MyServer((IP_PC, PORT_PC), MyUDPHandler)
        self.accionActual = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    def update(self):
        self.server.handle_request()
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
        self.socket.sendto(np.array(([accion]), dtype=np.uint8).tobytes(), (IP_ROBOT, PORT_ROBOT))


    def terminarRobot(self):
        self.server.server_close()