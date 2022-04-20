from lib.apiControl import ApiControlRobot
from controller import Robot
from controller import Camera
from controller import Supervisor
from controller import *
from controller import Node

import numpy as np

#Iteraciones por segundo
TIME_STEP = 30

#Velocidades para el movimiento
VEL_BASE = 5
MOD_VEL = 2

NUM_WAYPOINTS = 3 #Cantidad de puntos de restauracion que se usaran en el buffer
STEP_INTERVAL = 40 #Cantidad de iteraciones entre cada waypoint

#SENSORES_INFERIORES = ["left light sensor", "right light sensor"]
SENSORES_INFERIORES = ["ground left infrared sensor", "ground right infrared sensor"]
class ApiWebots(ApiControlRobot):

    def __init__(self):
        #Inicializar el robot
        self.robot = Supervisor()
        #Inicializar Camara
        self.camera = self.robot.getDevice('cameraLinea')
        self.camera.enable(TIME_STEP*4)
        
        #Inicializar Sensores
        self.sensorLineaIzq = self.robot.getDevice(SENSORES_INFERIORES[0])
        self.sensorLineaDer = self.robot.getDevice(SENSORES_INFERIORES[1])

        self.sensorLineaIzq.enable(TIME_STEP * 4)
        self.sensorLineaDer.enable(TIME_STEP * 4)

        #Inicializar ruedas
        self.ruedaIzq = self.robot.getDevice('left wheel motor')
        self.ruedaDer = self.robot.getDevice('right wheel motor')
        
        self.ruedaIzq.setPosition(float('inf'))
        self.ruedaIzq.setVelocity(0)
        self.ruedaDer.setPosition(float('inf'))
        self.ruedaDer.setVelocity(0)

        self.waypoints = [] #Cola de puntos de restauración
        self.stepCount = 0  #Contador para guardar un nuevo punto de restauracion

        #Inicializamos los puntos de restauracion
        for _ in range(NUM_WAYPOINTS):
            self.waypoint()

        print(self.waypoints)


    def update(self):
        
        self.robot.step(TIME_STEP)
        self.stepCount = (self.stepCount +1) % STEP_INTERVAL

        if self.stepCount == 0:
            self.waypoint()

    def getSensorLinea(self):
        der = self.sensorLineaDer.getValue()
        izq = self.sensorLineaIzq.getValue()
        #print(der, izq)
        return der < 600 or izq < 600

    def getDatosCamara(self):
        imagen = self.camera.getImage()
        if imagen is not None:
            return np.frombuffer(self.camera.getImage(), np.uint8).reshape((self.camera.getHeight(), self.camera.getWidth(), 4))
        
        return None
        #return self.camera.getImage()

    def getResolucionCam(self):
        return (self.camera.getWidth(), self.camera.getHeight())

    def setMotores(self, izq, der):
        #Aplicar una velocidad a cada motor
        self.ruedaDer.setVelocity(der)
        self.ruedaIzq.setVelocity(izq)

    def ejecutarAccion(self, accion):

        #print(accion)
        if accion == 0:
            self.setMotores(VEL_BASE , VEL_BASE) #Avanzar

        elif accion == 1:
            
            self.setMotores(VEL_BASE - MOD_VEL, VEL_BASE + MOD_VEL) #Girar a la derecha

        elif accion == 2:
            self.setMotores(VEL_BASE + MOD_VEL, VEL_BASE - MOD_VEL) #Girar a la izquierda
            
        elif accion == 3:
            self.setMotores(VEL_BASE - MOD_VEL * 2, VEL_BASE + MOD_VEL * 2) #Girar fuerte a la derecha

        elif accion == 4:
            self.setMotores(VEL_BASE + MOD_VEL * 2, VEL_BASE - MOD_VEL * 2) #Girar fuerte a la izquierda

    def terminarRobot(self):
        #Desactivar todos los dispositivos al terminar la ejecución
        self.camera.disable()
        self.sensorLineaIzq.disable()
        self.sensorLineaDer.disable()
    
    def reset(self):
        #Esta función sirve para colocar de nuevo el robot en la linea en caso de que se salga

        if not self.robot.getSupervisor(): #Comprobar si el robot es un supervisor
            return
        
        #self.robot.simulationReset()

        #Obtenemos los campos de posición y rotación
        nodoRobot = self.robot.getFromDef('robot')
        transField = nodoRobot.getField('translation')
        rotField = nodoRobot.getField('rotation')

        #Obtenemos el punto de restauración más antiguo de la cola
        (pos, rot) = self.waypoints[0]

        #Aplicamos la posición y rotacion en ese punto de restauración al robot
        transField.setSFVec3f(pos)
        rotField.setSFRotation(rot)
        
        #Reiniciamos todos los otros puntos a este
        for _ in range(NUM_WAYPOINTS):
            self.waypoint()

        #Reiniciamos las físicas, para evitar comportamientos extraños
        self.robot.simulationResetPhysics()
        self.robot.step(TIME_STEP)

        #Reiniciamos la posición de las ruedas
        self.ruedaIzq.setPosition(float('inf'))
        self.ruedaIzq.setVelocity(0)
        self.ruedaDer.setPosition(float('inf'))
        self.ruedaDer.setVelocity(0)

    def waypoint(self):

        if not self.robot.getSupervisor(): #Comprobar si el robot es un supervisor
            return
        
        #Obtener los campos de posición y rotación del robot
        nodoRobot = self.robot.getFromDef('robot')
        transField = nodoRobot.getField('translation')
        rotField = nodoRobot.getField('rotation')

        #Eliminamos el elemento más antiguo si la cola está llena
        if len(self.waypoints) >= NUM_WAYPOINTS:
            self.waypoints.pop(0)
        
        #Añadimos una nueva posición y rotación a la cola
        pos = transField.getSFVec3f()
        rot = rotField.getSFRotation()
        self.waypoints.append((pos, rot))
        

