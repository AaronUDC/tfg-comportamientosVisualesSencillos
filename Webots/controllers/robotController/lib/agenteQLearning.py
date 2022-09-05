
from lib.singleton import SingletonVariables


from time import gmtime, strftime
import os

import numpy as np
from numpy.random import default_rng

nombreAlgoritmo = "QLearning"

class AgenteQLearning():
    def __init__(self, entorno, rA, gamma):
        self.entorno = entorno
        self.dictEstados= entorno.states()
        self.dictAcciones = entorno.actions()
        
        self.rA = rA #Ratio de aprendizaje
        
        self.gamma = gamma

        #Inicializar una la tabla-Q con valores aleatorios.
        print(self.dictEstados)
        print(self.dictAcciones)
        self.tablaQ = default_rng().random((self.dictEstados['num_values'], self.dictAcciones['num_values'])) * 3
        
        self.estadoAnterior = None
        self.estadoAct = None
        
        self.recompensa = 0 #Ultima recompensa


    def actualizarQValor(self, estadoAnterior, accion, recompensa, nuevoEstado):
        maximo = np.max(self.tablaQ[nuevoEstado])
        self.tablaQ[estadoAnterior,accion] = self.tablaQ[estadoAnterior,accion] + self.rA * (recompensa + self.gamma * maximo - self.tablaQ[estadoAnterior,accion])
        
    def getQValor(self, estado, accion):
        return self.tablaQ[estado,accion]

    def getMejorAccion(self,estado):
        return np.argmax(self.tablaQ[estado,:])

    def act(self, estado):
        self.estadoAnterior = self.estadoAct
        self.estadoAct = estado
        self.accionAct = self.getMejorAccion(estado)
        return self.accionAct
    
    def observe(self, terminal, recompensa, estado):
        
        self.actualizarQValor(self.estadoAct, self.accionAct, recompensa, estado) 
    
    def cargarTablaQ(self, ruta):
        #Cargar una tablaQ de un archivo
        
        self.tablaQ = np.loadtxt(ruta, skiprows=1)
        print('TablaQ cargada de: ', ruta)
        print(self.tablaQ)
        
    def guardarTablaQ(self, directorio):
        
        variablesGlobales = SingletonVariables()

        if not os.path.exists(directorio):
            os.makedirs(directorio)
        
        nombreArchivo = 'TablaQ_{algoritmo}_{version}.txt'.format(separador= variablesGlobales.separadorCarpetas,
           algoritmo = nombreAlgoritmo, version= variablesGlobales.version)
        
        cabecera = 'TablaQ rA= {rA} gamma= {gamma}'.format(rA= self.rA, gamma= self.gamma)
        
        ruta = "{directorio}{separador}{nombreArchivo}".format(
            directorio = directorio, separador= variablesGlobales.separadorCarpetas,
            nombreArchivo = nombreArchivo)

        np.savetxt(ruta, self.tablaQ, header=cabecera)
        
        print("Tabla Q guardada en", ruta)

    
        
