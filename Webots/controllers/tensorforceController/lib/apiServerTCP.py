
from lib.apiControl import ApiControlRobot
from lib.preprocesado.preprocesadoServer import PreprocesadoServer

import socket

import numpy as np
from datetime import datetime
import time
import math
import pygame

IP_PC, PORT_PC = "", 9999
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
        
        self.preprocesado = PreprocesadoServer(self.dimImagen)

        self.socketMando = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Desactivar algoritmo de Nagle
        
        self.sock.settimeout(60)

        self.sock.bind((IP_PC,PORT_PC))
        print("Esperando Conexión")
        self.sock.listen(1)
        self.conection, self.dir = self.sock.accept()
        self.lastPacketTimestamp = timestampMilis()
        self.lastTimestamp = millisToBytes(0)
        self.img = None

        self.accionActual = 0

    def update(self):
        self.reloj.tick(30)
        #print("Timeout")

    def parada(self):
        
        self.parado = True
        self.socketMando.sendto(np.array(([1]), dtype=np.uint8).tobytes(), (self.dir[0], PORT_MANDO))

    def reanudar(self):

        self.parado = False
        self.socketMando.sendto(np.array(([0]), dtype=np.uint8).tobytes(), (self.dir[0], PORT_MANDO))
    
    def getTime(self):

        time = datetime.now()
        return time.timestamp()

    def getSensorLinea(self):
        #Obtener si los sensores de linea han detectado la linea
        return False

    def getImgCamara(self):
        #Obtener la ultima imagen capturada por la camara
        return self.img

    def getResolucionCam(self):

        return self.dimImagen

    def getDictEstados(self):

        return self.preprocesado.getDictEstados()

    def getEstado(self):
        
        chunk = self.conection.recv(88)

        if chunk == b'':
            raise RuntimeError("socket connection broken")     

        imgBytes = np.frombuffer(chunk[:-8], dtype=np.uint8)

        timestampBytes = chunk[-8:]
        
        self.lastTimestamp = timestampBytes

        self.img = np.reshape(imgBytes, (self.dimImagen[1],self.dimImagen[0]))
        self.lastPacketTimestamp = timestampMilis()

        imagenProcesada, viendoLinea = self.preprocesado.getEstado(self.img)
        self.preprocesado.estadoActual = imagenProcesada
        self.preprocesado.viendoLinea = viendoLinea

        return imagenProcesada, viendoLinea

    def setAccion(self, accion):
        self.seleccionarAccion(accion)
    
    def seleccionarAccion(self, accion):
        accionBytes= bytearray(np.array(([accion]), dtype=np.uint8).tobytes())
        dataBytes = bytearray(self.lastTimestamp)
        accionBytes.extend(dataBytes)
        dataBytes = bytearray(millisToBytes(timestampMilis()-self.lastPacketTimestamp))
        accionBytes.extend(dataBytes)
        
        sent = self.conection.send(accionBytes)
        #print("Enviado: ", time.process_time())
        
        if sent == 0:
            raise RuntimeError("socket connection broken")

    def terminarRobot(self):
        self.conection.shutdown(socket.SHUT_RDWR)
        self.conection.close()