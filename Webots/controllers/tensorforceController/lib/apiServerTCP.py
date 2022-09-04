
import imp
import cv2
from lib.apiControl import ApiControlRobot
from lib.singleton import SingletonVariables
from lib.procesadoLineas.procesadoServer import ProcesadoServer
import socketserver
import socket
import numpy as np
from datetime import datetime
import time
import math
import pygame

IP_PC, PORT_PC = "192.168.1.44", 9999
IP_ROBOT, PORT_ROBOT  = "192.168.1.43", 9998
PORT_MANDO = 9997

def timestampMilis():
	#Obtener la fecha y hora actual en milisegundos
	return  math.floor(time.process_time() * 1000)

def millisToBytes(millis):
	#Convertir un int representando los milisegundos desde Epoch a una cadena de 8 bytes.
	return millis.to_bytes(8,byteorder="big")

def bytesToMillis(millisBytes):
	#Convertir una cadena de bytes a un int
	return int.from_bytes(millisBytes, byteorder = "big")

class ApiServerTCP(ApiControlRobot):
    def __init__(self):
        #Inicializar el robot
        ApiControlRobot.__init__(self, 0,0)
        self.dimImagen = (10,8)

        self.reloj = pygame.time.Clock()
        
        self.hiloProcesado = ProcesadoServer(self,self.dimImagen)

        #self.server = MyServer((IP_PC, PORT_PC), MyTCPHandler)
        #self.server.daemon_threads = True
        self.socketMando = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        #self.sock.setsockopt(socket.IPPROTO_TCP, socket.SO, 6)
        self.sock.settimeout(60)

        self.sock.bind((IP_PC,PORT_PC))
        print("Esperando Conexión")
        self.sock.listen(1)
        self.conection, self.dir = self.sock.accept()
        self.lastPacketTimestamp = timestampMilis()
        self.lastTimestamp = millisToBytes(0)
        self.img = None


        self.accionActual = 0

    
    def parada(self):
        
        self.parado = True
        self.socketMando.sendto(np.array(([1]), dtype=np.uint8).tobytes(), (self.dir[0], PORT_MANDO))

    def setAccion(self, accion):
        self.ejecutarAccion(accion)

    def reanudar(self):
        self.parado = False
        self.socketMando.sendto(np.array(([0]), dtype=np.uint8).tobytes(), (self.dir[0], PORT_MANDO))


    def conectServer(self):
        pass

    def update(self):
        self.reloj.tick(30)
        #print("Timeout")
    
    def getTime(self):
        time = datetime.now()

        return time.timestamp()

    def getSensorLinea(self):
        #Obtener si los sensores de linea han detectado la linea
        return False

    def getDatosCamara(self):
        #Obtener la ultima imagen capturada por la camara
        
        return self.img

    def getEstado(self):
        #print("recibiendo", time.process_time())
        chunk = self.conection.recv(88)
        #print("Recibido: ", time.process_time())
        if chunk == b'':
            raise RuntimeError("socket connection broken")     

        imgBytes = np.frombuffer(chunk[:-8], dtype=np.uint8)

        timestampBytes = chunk[-8:]
        
        self.lastTimestamp = timestampBytes
        

        self.img = np.reshape(imgBytes, (self.dimImagen[1],self.dimImagen[0]))
        self.lastPacketTimestamp = timestampMilis()


        imagenProcesada, viendoLinea = self.hiloProcesado.getEstado(self.img)
        self.hiloProcesado.estadoActual = imagenProcesada
        self.hiloProcesado.viendoLinea = viendoLinea

        return imagenProcesada, viendoLinea

    def getDictEstados(self):
        return self.hiloProcesado.getDictEstados()
    
    def getResolucionCam(self):
        return self.dimImagen


    def setMotores(self, izqu, der):
        #Aplicar una velocidad a cada motor
        print("Esto no deberia pasar")
    
    def ejecutarAccion(self, accion):
        accionBytes= bytearray(np.array(([accion]), dtype=np.uint8).tobytes())
        dataBytes = bytearray(self.lastTimestamp)
        accionBytes.extend(dataBytes)
        dataBytes = bytearray(millisToBytes(timestampMilis()-self.lastPacketTimestamp))
        accionBytes.extend(dataBytes)
        #print("Enviando", time.process_time())
        sent = self.conection.send(accionBytes)
        #print("Enviado: ", time.process_time())
        
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def terminarRobot(self):
        self.conection.shutdown(socket.SHUT_RDWR)
        self.conection.close()