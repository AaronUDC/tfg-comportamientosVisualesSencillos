import random
import numpy as np

from lib.hiloLineasCamara import HiloLineasCam
from lib.singleton import SingletonVariables
from threading import Thread
import threading

class HiloQLearning():
    def __init__(self, estados, acciones, hiloLineasCam, rA, gamma):
        self.nEstados= estados
        self.nAcciones = acciones
        
        self.rA = rA #Ratio de aprendizaje
        
        self.gamma = gamma

        self.tablaQ = np.random.rand(estados, acciones) * 3
        
        self.hiloControl = None
        
        self.hiloLineasCam = hiloLineasCam
        self.estadoAnterior = self.hiloLineasCam.read()
        
        self.recompensa = 0 #Ultima recompensa
        # Lock para bloquear el thread una vez se aplica la recompensa 
        # hasta que se reciba otra.
        self.recValida = threading.Lock() 
        
        #Singleton
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
            #Crear un bloqueo en las variables globales?
            if self.variablesGlobales.parado:
                continue
                
            #Obtener el estado actual
            estado = self.hiloLineasCam.read()
            #Seleccionar accion
            accion = self.getMejorAccion(self.estadoAnterior)
                
            #Enviar accion al hilo de control
            self.hiloControl.setAccion(accion)
            
            self.recValida.acquire() #Esperamos a recibir una nueva recompensa.
            
            #print("Recompensa ", self.recompensa, accion )
            #Actualizar tabla Q
            self.actualizarQValor(self.estadoAnterior, accion, self.recompensa, estado) 
            
            self.recValida.acquire(blocking=False) #Bloqueamos el poder recibir nuevas recompensas
            
            self.estadoAnterior = estado
            #Actualizar la probabilidad de seleccionar una accion aleatoria
            #self.randomProb = self.randomProb - 1.0/self.numRandomActions
            #self.randomProb = max(min(self.randomProb, 1.0), 0.0)
            
    def setHiloControl(self, hiloControl):
        self.hiloControl = hiloControl
                
    def setRecompensa(self, recompensa):
        self.recompensa = recompensa 
        if self.recValida.locked():
            self.recValida.release() #Permitimos recibir una nueva recompensa
        
    def stop(self):
        self.done = True
    
        
