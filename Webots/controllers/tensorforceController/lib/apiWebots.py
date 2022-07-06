from lib.apiControl import ApiControlRobot

from lib.singleton import SingletonVariables
import numpy as np
from numpy import linalg

from controller import Robot
from controller import Camera
from controller import Supervisor
from controller import *
from controller import Node

import numpy as np

#Iteraciones por segundo
TIME_STEP = 30

#Velocidades para el movimiento
VEL_BASE = 3
MOD_VEL = 1

NUM_WAYPOINTS = 5 #Cantidad de puntos de restauracion que se usaran en el buffer
STEP_INTERVAL = 40 #Cantidad de iteraciones entre cada waypoint

DISTANCIA_MIN_INICIO = 0.1 #Distancia mínima (m) al punto de inicio del robot para comprobar cuando se da una vuelta.

#SENSORES_INFERIORES = ["left light sensor", "right light sensor"]
SENSORES_INFERIORES = ["ground left infrared sensor", "ground right infrared sensor"]
class ApiWebots(ApiControlRobot):

    def __init__(self):
        ApiControlRobot.__init__(self, VEL_BASE,MOD_VEL)
        #Inicializar el robot
        self.robot = Supervisor()
        #Inicializar Camara
        self.camera = self.robot.getDevice('cameraLinea')
        self.camera.enable(TIME_STEP*4)
        
        #Inicializar Sensores
        self.sensorLineaIzq = self.robot.getDevice(SENSORES_INFERIORES[0])
        self.sensorLineaDer = self.robot.getDevice(SENSORES_INFERIORES[1])

        self.sensorLineaIzq.enable(TIME_STEP)
        self.sensorLineaDer.enable(TIME_STEP)

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
            self.pushWaypoint()

        #print(self.waypoints)

        #Punto inicial
        self.puntoInicial = self.getWaypoint()
        self.visitandoMeta = True
        
        self.vuelta = 0 #TODO: Esto mejor en el padre, ya que se debería poder usar en todas las implementaciones.

    

    def update(self):
        
        self.robot.step(TIME_STEP)
        self.stepCount = (self.stepCount +1) % STEP_INTERVAL

        if self.stepCount == 0:
            self.pushWaypoint()

        #TODO: Contador de vueltas.
        #Obtener posición actual
        (posActual, dirActual) = self.getWaypoint()
        posActualArr = np.array(posActual)
        (posMeta, dirMeta) = self.puntoInicial
        posMetaArr = np.array(posMeta)

        distanciaAMeta = linalg.norm(posMetaArr- posActualArr)
        #print(distanciaAMeta)

        if distanciaAMeta < DISTANCIA_MIN_INICIO:
            if not self.visitandoMeta:
                self.visitandoMeta = True
                self.vuelta += 1
                print("Vuelta:", self.vuelta)
        else:
            if distanciaAMeta > DISTANCIA_MIN_INICIO and self.visitandoMeta:
                self.visitandoMeta = False
                #print("Nueva vuelta")
        #Combrobar si se encuentra cerca de la meta
            #Si se encuentra cerca sumar una vuelta si no se está visitando y marcar que se está visitando
            #Si se aleja de la meta (igual un poco más del mínimo) y se está visitando, marcar que no se está visitando

        
            
    #TODO: Get Vuelta

    #TODO: Set Vuelta

    def getTime(self):
        #Devolver el tiempo de la simulacion en segundos
        return self.robot.getTime()
        

    def getSensorLinea(self):
        der = self.sensorLineaDer.getValue()
        izq = self.sensorLineaIzq.getValue()
        #print(der, izq)
        return der < 600 or izq < 600

    def getDatosCamara(self):
        imagen = self.camera.getImage()
        if imagen is not None:
            return np.frombuffer(imagen, np.uint8).reshape((self.camera.getHeight(), self.camera.getWidth(), 4))
        
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
            self.setMotores(self.velocBase , self.velocBase) #Avanzar

        elif accion == 1:
            
            self.setMotores(self.velocBase - self.modificadorVeloc, self.velocBase + self.modificadorVeloc) #Girar a la derecha

        elif accion == 2:
            self.setMotores(self.velocBase + self.modificadorVeloc, self.velocBase - self.modificadorVeloc) #Girar a la izquierda
            
        elif accion == 3:
            self.setMotores(self.velocBase - self.modificadorVeloc * 2, self.velocBase + self.modificadorVeloc * 2) #Girar fuerte a la derecha

        elif accion == 4:
            self.setMotores(self.velocBase + self.modificadorVeloc * 2, self.velocBase - self.modificadorVeloc * 2) #Girar fuerte a la izquierda

    def terminarRobot(self):
        #Desactivar todos los dispositivos al terminar la ejecución
        self.camera.disable()
        self.sensorLineaIzq.disable()
        self.sensorLineaDer.disable()
        self.setMotores(0,0) #Paramos los motores
        
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
            self.pushWaypoint()

        #Reiniciamos las físicas, para evitar comportamientos extraños
        self.robot.simulationResetPhysics()
        self.robot.step(TIME_STEP)

        #Reiniciamos la posición de las ruedas
        self.ruedaIzq.setPosition(float('inf'))
        self.ruedaIzq.setVelocity(0)
        self.ruedaDer.setPosition(float('inf'))
        self.ruedaDer.setVelocity(0)

        SingletonVariables().parado = False

        #TODO: Si se resetea, pensar en si solo resetear el contador de vueltas, 
        # o además colocar un nuevo punto de inicio en el lugar en el que se recupera el robot.
        self.setVuelta(0)

    def getWaypoint(self):
        if not self.robot.getSupervisor(): #Comprobar si el robot es un supervisor
            return
        
        #Obtener los campos de posición y rotación del robot
        nodoRobot = self.robot.getFromDef('robot')
        transField = nodoRobot.getField('translation')
        rotField = nodoRobot.getField('rotation')
        #Añadimos una nueva posición y rotación a la cola
        pos = transField.getSFVec3f()
        rot = rotField.getSFRotation()

        return (pos, rot)

    def pushWaypoint(self):

        if not self.robot.getSupervisor(): #Comprobar si el robot es un supervisor
            return
        
        waypoint = self.getWaypoint()

        #Eliminamos el elemento más antiguo si la cola está llena
        if len(self.waypoints) >= NUM_WAYPOINTS:
            self.waypoints.pop(0)
        
        self.waypoints.append(waypoint)
        

