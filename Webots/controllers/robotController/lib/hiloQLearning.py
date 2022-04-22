import random
import numpy as np

from lib.hiloLineas import HiloLineas
from lib.singleton import SingletonVariables
from threading import Thread
import threading

import time
from datetime import datetime
from time import gmtime, strftime

import cv2
import numpy as np

nombreAlgoritmo = "QLearning"

class HiloQLearning():
    def __init__(self, estados, acciones, hiloLineasCam, rA, gamma):
        self.nEstados= estados
        self.nAcciones = acciones
        
        self.rA = rA #Ratio de aprendizaje
        
        self.gamma = gamma

        self.tablaQ = np.random.rand(estados, acciones) * 3
        
        self.hiloControl = None
        
        self.hiloLineasCam = hiloLineasCam
        self.estadoAnterior,_,_ = self.hiloLineasCam.read()
        
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
    
    def _guardarFoto(self, estado, imagen, angulo, accion):
        
        #Crear un string con los datos de lo capturado por la camara.
        
        carpeta = 'savedPhotos'
        
        hora = datetime.now()
        horaSt= hora.strftime('%d.%m.%Y_%H.%M.%S.%f')
                        
        if angulo is None:
            nombreArchivo = '{fecha}_None_{estado}_{accion}.jpg'.format(fecha=horaSt,estado=estado,accion=accion)
        else:
            nombreArchivo = '{fecha}_{angulo:.2f}_{estado}_{accion}.jpg'.format(fecha=horaSt,angulo=angulo,estado=estado,accion=accion)
        
        guardado = cv2.imwrite("{carpeta}{separador}{nombre}".format(carpeta=carpeta,separador=self.variablesGlobales.separadorCarpetas,nombre=nombreArchivo),imagen)

        #if guardado:
        #   print('Guardado ', nombreArchivo)
            
        
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
            
    def setHiloControl(self, hiloControl):
        self.hiloControl = hiloControl
                
    def setRecompensa(self, recompensa):
        self.recompensa = recompensa 
        if self.recValida.locked():
            self.recValida.release() #Permitimos recibir una nueva recompensa
    
    def cargarTablaQ(self, path):
        #Cargar una tablaQ de un archivo
        
        self.tablaQ = np.loadtxt(path, skiprows=1)
        print('TablaQ cargada de: ', path)
        print(self.tablaQ)
        
    def guardarTablaQ(self):
        #Guardar la tablaQ en un archivo, almacenando la versión y algoritmo en la cabecera.
        fecha = strftime("%Y-%m-%d_%H.%M.%S", gmtime())
        nombreArchivo = 'savedTables{separador}TablaQ_{fecha}_{algoritmo}_{version}.txt'.format(separador= self.variablesGlobales.separadorCarpetas, fecha=fecha, \
           algoritmo = nombreAlgoritmo, version= self.variablesGlobales.version)
        
        cabecera = 'TablaQ rA= {rA} gamma= {gamma}'.format(rA= self.rA, gamma= self.gamma)
        
        np.savetxt(nombreArchivo, self.tablaQ, header=cabecera)
        
        print("Tabla Q guardada en", nombreArchivo)
    
    def stop(self):
        self.done = True
    
        
