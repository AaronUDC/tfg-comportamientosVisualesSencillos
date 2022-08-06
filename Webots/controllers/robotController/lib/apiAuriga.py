
from lib.apiControl import ApiControlRobot
from lib.hiloCamara import HiloCamara
from lib.procesadoLineas.procesadoMascaras import ProcesadoMascaras
from lib.aurigapy.aurigapy import AurigaPy
import time
from time import gmtime, sleep, strftime

import pygame

import threading

TIME_STEP = 15

#Velocidades para el movimiento
VEL_BASE = 40
MOD_VEL = 20

SENSORES_INFERIORES = [6,7]

# Inicializar el hilo de la camara
RESOLUCION_CAM = (80,64)
    
bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/ttyUSB0"

sensorDer = 0
sensorIz = 0

def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

def onReading(value, timeout):
    
    print("%r > %r (%r)" % (funcionInexistente, value, timeout))
    #pass
    
class ApiAuriga(ApiControlRobot):

    def __init__(self):
        #Inicializar el robot
        self.hiloCam = HiloCamara(RESOLUCION_CAM).start()
        self.procesadoLineas = ProcesadoMascaras(self,RESOLUCION_CAM)
        
        
        self.reloj = pygame.time.Clock()
        
        self.parado = True
        
        self.terminado = False
        self.accionActual = 5 #Empieza parado
        
        self.auriga = AurigaPy(debug=False)
        print(" Conectando..." )
        self.auriga.connect(usb)
        print(" Conectado!" )
        time.sleep(0.2)
        
        #Iniciar el hilo que controla los motores
        self.threadMotores = threading.Thread(target= self._bucleMotores)
        self.threadMotores.start()
        
    def _bucleMotores(self):
        #Hilo que se encarga de controlar los motores. Se ejecuta la orden actual cada 50ms
        while not self.terminado:
            time.sleep(1.0/(TIME_STEP+5))
            self.ejecutarAccion(self.accionActual)
    
    def setAccion(self, accion):
        if not self.parado: #Si esta parado, no admitimos nuevas ordenes
            self.accionActual = accion

    def parada(self):
        
        self.parado = True
        self.accionActual = 5
    def reanudar(self):
        self.parado = False
        
    def update(self):
        print(self.reloj.tick(TIME_STEP))
    
    def getEstado(self):
    
        return self.procesadoLineas.getEstado(self.getDatosCamara())
        

    def getSensorLinea(self):
        pass
        
    
    def getTime(self):
        
        return int(time.process_time()*1000)
        
        
    def getDatosCamara(self):
        #Obtener la ultima imagen capturada por la camara
        return self.hiloCam.read()
    
    def getResolucionCam(self):
        return RESOLUCION_CAM

    def setMotores(self, izqu, der):
        self.auriga.set_speed(izqu,der, callback = onReading)
    
    def ejecutarAccion(self, accion):

        #print(accion)
        if accion == 0:
            self.setMotores(-(VEL_BASE - MOD_VEL * 2), VEL_BASE + MOD_VEL * 2) #Girar fuerte a la izquierda
        
        elif accion == 1:
            self.setMotores(-(VEL_BASE - MOD_VEL), VEL_BASE + MOD_VEL) #Girar a la izquierda
            
        elif accion == 2:
            self.setMotores(-(VEL_BASE) , VEL_BASE) #Avanzar

        elif accion == 3:
            self.setMotores(-(VEL_BASE + MOD_VEL), VEL_BASE - MOD_VEL) #Girar a la derecha

        elif accion == 4:
            self.setMotores(-(VEL_BASE + MOD_VEL * 2), VEL_BASE - MOD_VEL * 2) #Girar fuerte a la derecha

        elif accion == 5:
            self.setMotores(0,0) #Parar
        
        
    def terminarRobot(self):
        #Finalizar los sistemas del robot.
        self.terminado = True
        self.hiloCam.stop()
        time.sleep(2)
        self.setMotores(0,0)
        #self.auriga.reset_robot()
        self.auriga.close()
        
