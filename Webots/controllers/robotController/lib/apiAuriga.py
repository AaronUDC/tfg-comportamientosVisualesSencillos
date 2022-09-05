
from lib.apiControl import ApiControlRobot
from lib.hiloCamara import HiloCamara
from lib.preprocesado.preprocesadoMascaras import PreprocesadoMascaras
from lib.aurigapy.aurigapy import AurigaPy
import time
from time import gmtime, sleep, strftime

import pygame

import threading

TIME_STEP = 30

#Velocidades para el movimiento
VEL_BASE = 45*3
MOD_VEL = 25

SENSORES_INFERIORES = [6,7]

# Inicializar el hilo de la camara
RESOLUCION_CAM = (80,64)
    
bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/ttyUSB0"

def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

def onReading(value, timeout):
    
    print("%r > %r (%r)" % (funcionInexistente, value, timeout))
    #pass
    
class ApiAuriga(ApiControlRobot):

    def __init__(self):
        
        ApiControlRobot.__init__(self, VEL_BASE,MOD_VEL)
       
        #Inicializar el robot
        self.hiloCam = HiloCamara(RESOLUCION_CAM).start()
        self.preprocesado = PreprocesadoMascaras(RESOLUCION_CAM)
        
        
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

    def update(self):
        self.reloj.tick(TIME_STEP)  

    def parada(self):
        
        self.parado = True
        self.accionActual = 5
        self.seleccionarAccion(5)
        
    def reanudar(self):

        self.parado = False
    
    
    def getTime(self):
        
        return int(time.process_time()*1000)
        
    def getSensorLinea(self):
        return False
    
    def getImgCamara(self):
        #Obtener la ultima imagen capturada por la camara
        return self.hiloCam.read()
    
    def getResolucionCam(self):
        return RESOLUCION_CAM
        
    def getDictEstados(self):
        return self.preprocesado.getDictEstados()
        
    def getEstado(self):
        return self.preprocesado.getEstado(self.getDatosCamara())
        
    def setMotores(self, izqu, der):
        self.auriga.set_speed(int(izqu),int(der), callback = onReading)

    def seleccionarAccion(self, accion):

        velAng = 0
        
        if accion == 0:
            velAng = 15 #Girar fuerte a la izquierda
        
        elif accion == 1:
            velAng = 12 #Girar a la izquierda
        
        elif accion == 2:
            velAng = 0
            #self.setMotores(self.velocBase , self.velocBase) #Avanzar

        elif accion == 3:
            velAng = -12 #Girar a la derecha
        
        elif accion == 4:
            velAng = -15 #Girar fuerte a la derecha
        
        elif accion == 5:
            self.setMotores(0,0) 
            return
            
        #print(velAng)
        l = (VEL_BASE - (14.5/2) * velAng)/ 3 # (VelBase - (distanciaRuedas/2) * velAng) / radioRuedas 
        r = (VEL_BASE + (14.5/2) * velAng)/ 3 # (VelBase + (distanciaRuedas/2) * velAng) / radioRuedas 
        
        self.setMotores(-l,r)

    def _bucleMotores(self):
        #Hilo que se encarga de controlar los motores. Se ejecuta la orden actual cada 50ms
        relojMotores = pygame.time.Clock()
        while not self.terminado:
            #time.sleep(1.0/(TIME_STEP+5))
            relojMotores.tick(TIME_STEP+5)
            
            self.ejecutarAccion(self.accionActual)
            
    def terminarRobot(self):
        #Finalizar los sistemas del robot.
        self.terminado = True
        self.hiloCam.stop()
        time.sleep(2)
        self.setMotores(0,0)
        #self.auriga.reset_robot()
        self.auriga.close()
        
