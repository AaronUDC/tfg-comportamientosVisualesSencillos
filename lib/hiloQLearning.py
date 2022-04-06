import random
import numpy as np

from lib.hiloLineasCamara import HiloLineasCam
from lib.singleton import SingletonVariables
from threading import Thread

class HiloQLearning():
    def __init__(self, estados, acciones, hiloLineasCam, rA, gamma, numRandomActions):
        self.nEstados= estados
        self.nAcciones = acciones
        
        self.rA = rA #Ratio de aprendizaje
        self.gamma = gamma

        self.tablaQ = np.zeros((estados, acciones))
        
        self.hiloControl = None
        
        self.hiloLineasCam = hiloLineasCam
        self.estadoAnterior = self.hiloLineasCam.read()
        
        self.recompensa = (0,False) #Ultima recompensa, el segundo dato indica si se ha aplicado o no
        
        
        self.randomProb = 1.0
        self.numRandomActions = numRandomActions
        
        self.variablesGlobales = SingletonVariables()
        
        self.done = False
        

    def actualizarQValor(self, estado, accion, recompensa, nuevoEstado):
        maximo = np.max(self.tablaQ[nuevoEstado])
        self.tablaQ[estado,accion] = (1-self.rA) * self.tablaQ[estado,accion] + self.rA * (recompensa + self.gamma * maximo)
        
    def getQValor(self, estado, accion):
        return self.tablaQ[estado,accion]

    def getMejorAccion(self,estado):
        return np.argmax(self.tablaQ[estado,:])
    
    def start(self):
        Thread(target=self.update, args=()).start()
        return self
    
    def update(self):
        
        while not self.done:
            
            if self.variablesGlobales.parado:
                continue
            
            estado = self.hiloLineasCam.read()
            #Seleccionar accion
            accion = self.getMejorAccion(estado) #Obtenemos la mejor accion segun el estado actual
            
            if random.random() < self.randomProb: 
                accion = random.randint(0,self.nAcciones-1)
            else:
                accion = self.getMejorAccion(self.estadoAnterior)
                
            #Enviar accion al hilo de control
            self.hiloControl.setAccion(accion)
            
            (recompensa, recValida) = self.recompensa
            while not recValida:
                (recompensa, recValida) = self.recompensa
            
            self.recompensa = (recompensa, False)
            print("Recompensa ", recompensa, accion )
            #Actualizar tabla Q
            self.actualizarQValor(self.estadoAnterior, accion, recompensa, estado) 

            self.estadoAnterior = estado
            #Actualizar la probabilidad de seleccionar una accion aleatoria
            self.randomProb = self.randomProb - 1.0/self.numRandomActions
            self.randomProb = max(min(self.randomProb, 1.0), 0.0)
            
    def setHiloControl(self, hiloControl):
        self.hiloControl = hiloControl
                
    def setRecompensa(self, recompensa):
        (_,recValida) = self.recompensa
        if not recValida: 
            self.recompensa = (recompensa,True)
            return True
        return False
        
    def stop(self):
        self.done = True
    
        
