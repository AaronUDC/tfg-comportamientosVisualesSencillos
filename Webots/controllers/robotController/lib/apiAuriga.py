
from lib.apiControl import ApiControlRobot
from lib.hiloCamara import HiloCamara
from lib.aurigapy.aurigapy import AurigaPy
import time
from time import gmtime, sleep, strftime

import pygame

TIME_STEP = 30

#Velocidades para el movimiento
VEL_BASE = 30
MOD_VEL = 15

SENSORES_INFERIORES = [6,7]

# Inicializar el hilo de la camara
RESOLUCION_CAM = (80, 64)
    
bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/ttyUSB0"

sensorDer = 0
sensorIz = 0

#Lectura constante de cada sensor
def callbackSensorR(value, timeout):
    global sensorDer
    if not timeout and value is not None:
        sensorDer = int(value)
        
    
def callbackSensorL(value, timeout):
    global sensorIz
    if not timeout and value is not None:
        sensorIz = int(value)	


def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

def onReading(value, timeout):
    
    print("%r > %r (%r)" % (timestamp(), value, timeout))
    #pass
    
class ApiAuriga(ApiControlRobot):

    def __init__(self):
        #Inicializar el robot
        self.hiloCam = HiloCamara(RESOLUCION_CAM).start()
        
        self.reloj = pygame.time.Clock()

        self.auriga = AurigaPy(debug=False)
        print(" Conectando..." )
        self.auriga.connect(usb)
        print(" Conectado!" )
        time.sleep(0.2)

        self.setMotores(0,0) 
        
        self.izq= False         

    def update(self):
        #global sensorDer, sensorIz
        #Actualizar los sistemas del robot
        #self.reloj.tick(TIME_STEP)
        
        self.izq = not self.izq
        #rint(self.reloj.get_fps())
        #sensorDer = self.auriga.get_line_sensor(SENSORES_INFERIORES[0])
        #sensorIz = self.auriga.get_line_sensor(SENSORES_INFERIORES[1])

    def getSensorLinea(self):
        global sensorDer, sensorIz
        #if self.izq:
        sensorIz = self.auriga.get_line_sensor(SENSORES_INFERIORES[1])
        #else:
        sensorDer = self.auriga.get_line_sensor(SENSORES_INFERIORES[0])
        
        if sensorDer is None or sensorIz is None:
            return False
        
         
        return sensorDer != 3 or sensorIz != 3
        
        
    def getDatosCamara(self):
        #Obtener la ultima imagen capturada por la camara
        return self.hiloCam.read()
    
    def getResolucionCam(self):
        return RESOLUCION_CAM

    def setMotores(self, izqu, der):
        self.auriga.set_speed(izqu,der)
    
    def ejecutarAccion(self, accion):

        #print(accion)
        if accion == 0:
            self.setMotores(-(VEL_BASE) , VEL_BASE) #Avanzar

        elif accion == 1:
            
            self.setMotores(-(VEL_BASE + MOD_VEL), VEL_BASE - MOD_VEL) #Girar a la derecha

        elif accion == 2:
            self.setMotores(-(VEL_BASE - MOD_VEL), VEL_BASE + MOD_VEL) #Girar a la izquierda
            
        elif accion == 3:
            self.setMotores(-(VEL_BASE + MOD_VEL * 2), VEL_BASE - MOD_VEL * 2) #Girar fuerte a la derecha

        elif accion == 4:
            self.setMotores(-(VEL_BASE - MOD_VEL * 2), VEL_BASE + MOD_VEL * 2) #Girar fuerte a la izquierda

    def terminarRobot(self):
        #Finalizar los sistemas del robot.
        self.hiloCam.stop()
        self.setMotores(0,0)
        time.sleep(2)
        self.auriga.reset_robot()
        self.auriga.close()
        

    #Metodos que solo tienen uso en webots para reiniciar la simulacion
    def reset(self):
        pass

    def waypoint (self):    
        pass
