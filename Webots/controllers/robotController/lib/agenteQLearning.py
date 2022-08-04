

from lib.hiloLineas import HiloLineas
from lib.singleton import SingletonVariables
from threading import Thread
import threading

import time
from datetime import datetime
from time import gmtime, strftime
import os

import cv2
import numpy as np
import random
from numpy.random import default_rng

nombreAlgoritmo = "QLearning"

class AgenteQLearning():
    def __init__(self, entorno, rA, gamma):
        self.entorno = entorno
        self.nEstados= entorno.states()
        self.nAcciones = entorno.actions()
        
        self.rA = rA #Ratio de aprendizaje
        
        self.gamma = gamma

        self.tablaQ = default_rng().random((self.nEstados, self.nAcciones)) * 3
        
        
        self.estadoAnterior = None
        self.estadoAct = None
        
        self.recompensa = 0 #Ultima recompensa


    def actualizarQValor(self, estado, accion, recompensa, nuevoEstado):
        maximo = np.max(self.tablaQ[nuevoEstado])
        self.tablaQ[estado,accion] = (1-self.rA) * self.tablaQ[estado,accion] + self.rA * (recompensa + self.gamma * maximo)
        
    def getQValor(self, estado, accion):
        return self.tablaQ[estado,accion]

    def getMejorAccion(self,estado):
        return np.argmax(self.tablaQ[estado,:])

    def act(self, estado):
        self.estadoAnterior = self.estadoAct
        self.estadoaAct = estado
        self.accionAct = self.getMejorAccion(estado)
        return self.accionAct
    
    def observe(self, terminal, recompensa):
        
        self.actualizarQValor(self.estadoAnterior, self.accionAct, recompensa, self.estadoAct) 
    
        
    def update(self):
        
        while not self.done:
            #Crear un bloqueo en las variables globales?
            if not self.variablesGlobales.parado:
                    
                #t0 = time.time()
                #Obtener el estado actual
                estado, imagen, angulo = self.hiloLineasCam.read()
                
                
                #Seleccionar accion
                accion = self.getMejorAccion(self.estadoAnterior)
                
                #Si la captura de imagenes esta activada, guardamos la foto
                if self.variablesGlobales.guardarFotos:
                    #Lo ejecutamos en un Thread a parte
                    Thread(target=self._guardarFoto, args=(estado, imagen, angulo, accion)).start()
                    
                
                #Enviar accion al hilo de control
                self.hiloControl.setAccion(accion)
                
                #t1 = time.time()
                #print('Tiempo decision:',round((t1-t0)*1000))
                self.recValida.acquire() #Esperamos a recibir una nueva recompensa.
                
                #t0 = time.time()
                #print("Recompensa ", self.recompensa, accion )
                #Actualizar tabla Q
                self.actualizarQValor(self.estadoAnterior, accion, self.recompensa, estado) 
                
                #t1 = time.time()
                
                #print('Tiempo modTabla:',round((t1-t0)*1000))
                self.recValida.acquire(blocking=False) #Bloqueamos el poder recibir nuevas recompensas
                
                self.estadoAnterior = estado
                #Actualizar la probabilidad de seleccionar una accion aleatoria
                #self.randomProb = self.randomProb - 1.0/self.numRandomActions
                #self.randomProb = max(min(self.randomProb, 1.0), 0.0)
            
    
    def cargarTablaQ(self, path):
        #Cargar una tablaQ de un archivo
        
        self.tablaQ = np.loadtxt(path, skiprows=1)
        print('TablaQ cargada de: ', path)
        print(self.tablaQ)
        
    def guardarTablaQ(self):
        
        variablesGlobales = SingletonVariables()
        
        #Guardar la tablaQ en un archivo, almacenando la versión y algoritmo en la cabecera.
        fechaSt = strftime("%Y-%m-%d_%H.%M.%S", gmtime())
        
        ruta = "savedTables{separador}tablaQ_{fecha}".format(separador = variablesGlobales.separadorCarpetas , fecha = fechaSt)

        if not os.path.exists(ruta):
            os.makedirs(ruta)
            print("se ha creado una carpeta en:", ruta)
        
        nombreArchivo = '{ruta}{separador}TablaQ_{algoritmo}_{version}.txt'.format(ruta = ruta, separador= variablesGlobales.separadorCarpetas,
           algoritmo = nombreAlgoritmo, version= variablesGlobales.version)
        
        cabecera = 'TablaQ rA= {rA} gamma= {gamma}'.format(rA= self.rA, gamma= self.gamma)
        
        np.savetxt(nombreArchivo, self.tablaQ, header=cabecera)
        
        print("Tabla Q guardada en", nombreArchivo)

    
        
