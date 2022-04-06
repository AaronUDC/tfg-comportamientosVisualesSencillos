import random
import numpy as np

class TablaQ():
    def __init__(self, estados, acciones, rA, gamma):
        self.estados= estados
        self.acciones = acciones
        
        self.rA = rA #Ratio de aprendizaje
        self.gamma = gamma

        self.tablaQ = np.zeros((estados, acciones))
        
    def actualizarQValor(self, estado, accion, recompensa, nuevoEstado):
        maximo = np.max(self.tablaQ[nuevoEstado])
        self.tablaQ[estado,accion] = (1-self.rA) * self.tablaQ[estado,accion] + self.rA * (recompensa + self.gamma * maximo)

    def getQValor(self, estado, accion):
        return self.tablaQ[estado,accion]

    def getMejorAccion(self,estado):
        return np.argmax(self.tablaQ[estado,:])


