from time import sleep
import cv2
#import lib.apiControl
import numpy as np
import time
import math
from threading import Thread
import threading

import glob
from lib.procesadoLineas.hiloProcesado import HiloProcesadoImg

from lib.singleton import SingletonVariables

carpeta = 'plantillas'

widePercent = 0

PORCENTAJE_MAX = 0.15 # Umbral para considerar que la máscara más similar a la imagen no es suficientemente similar como para considerar que se ve la linea

class ProcesadoMascaras(HiloProcesadoImg):
    def __init__(self,apiControl, dimensiones, carpetaKernels = carpeta):
        
        super().__init__(apiControl, dimensiones)
        
        self.numkernels = 0
        self.listaKernels, self.listaPuntuacionMax = self._getKernels(carpetaKernels)
        
        # Variables para poder guardar la ultima imagen capturada en memoria
        self.lastImg = None
        self.lastRawImg = None
        
        self.estadoAct= np.zeros(self.numkernels)
        self.nFoto = 0
        self.index = 0 #Indice del estado

        print(self.listaPuntuacionMax)
        #Lock
        self.lock = threading.Lock()
        
    
    def _getKernels(self, carpeta):
        
        variablesGlobales = SingletonVariables()

        listaImgs = []
        listaPuntuacionMax = []
        for imagenPath in sorted(glob.glob('{carpeta}{separador}*.png'.format(carpeta = carpeta, separador = variablesGlobales.separadorCarpetas))):
            #print(imagenPath)
            img = cv2.imread(imagenPath)
            
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            #img = img[int((self.dimensiones[1])*0.4): int(self.dimensiones[1]-1), int(self.dimensiones[0]*(widePercent/2)):int(self.dimensiones[0]*(1-widePercent/2))]             
            
            img = img/255.0 #Convertir una imagen de enteros de 0 a 255 a punto flotante de 0.0 a 1.0

            listaPuntuacionMax.append(np.sum(img) * PORCENTAJE_MAX)
            listaImgs.append((img, np.sum(img))) #Guardamos la imagen y la suma de sus pixeles para ahorrar cálculos posteriormente
            self.numkernels += 1
        
        return listaImgs, listaPuntuacionMax

    def processImage(self, image):

        #Segmentar la imagen
        img = cv2.GaussianBlur(image,(5,5),0, borderType = cv2.BORDER_REPLICATE)
        
        #Cambiamos el espacio de color a HSV
        imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        t0 = time.process_time()

        mask = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41,10)
        
        #Recorte de la zona central inferior de la imagen
        #mask = mask[int((self.dimensiones[1])*0.4): int(self.dimensiones[1]-1), int(self.dimensiones[0]*(widePercent/2)):int(self.dimensiones[0]*(1-widePercent/2))]             
        
        
        mask = 1.0-mask/255.0 #Invertir la imagen y cambiar el rango a (0.0, 1.0)
        t1 = time.process_time()

        #Comprobar cual de los kernels se solapa mejor con la imagen
        listaImgsSim = []
        listaMedidaSim = []

        for kernel in self.listaKernels:
            #Guardamos las imagenes de similitud y la suma de sus pixeles en la lista
            imgSimilitud= mask * kernel[0]

            medidaSimilitud =  np.sum(imgSimilitud)
            listaImgsSim.append(imgSimilitud)
            listaMedidaSim.append(medidaSimilitud)

        t2 = time.process_time()

        return listaMedidaSim, listaImgsSim, (t0,t1,t2)

    def update(self):
        while not self.stopped:
            img = self.apiControl.getDatosCamara() #Leer imagen del thread de la camara

            listaMedidaSim, listaImgsSim, _ = self.processImage(img)
            
            mejorMedida = np.max(listaMedidaSim)
            mejorIndice = listaMedidaSim.index(mejorMedida)
            
            self.lock.acquire(blocking=False) #Bloqueamos los datos antes de sobreescribirlos
            
            self.lastImg = listaImgsSim[mejorIndice] * 255
            self.lastRawImg = img 

            self.estadoAct = np.array(listaMedidaSim)
            
            
            if (mejorMedida > self.listaPuntuacionMax[mejorIndice]):
                #Comprobar si la mejor imagen tiene una puntuación minima
                self.index = mejorIndice
                self.angulo = round(mejorMedida)
            else:
                #En caso contrario consideramos que no se ve la linea
                self.index = self.getNumEstados()-1
                self.angulo = -round(mejorMedida)
                
            
            #print(self.index)
            if self.lock.locked():
                self.lock.release() #Liberamos los datos
            


    def getNumEstados(self):
        return self.numkernels + 1

    def getDictEstados(self):
        return dict(type='float', shape= (self.numkernels,), min_value=0.0)
        #return dict(type='int', num_values=self.getNumEstados())
    
    def printUltimaFotog(self):
        
        carpeta = 'savedPhotos'

        #self.lock.acquire() #Nos ponemos a la espera si el thread está bloqueado
		#Guardar la ultima imagen almacenada en un archivo, incluyendo el angulo e indice asignado.
        
        variablesGlobales = SingletonVariables()


        if self.angulo is None:
            nombre = 'manual_{n}_{index}.jpg'.format(n=self.nFoto, index=self.index)
            nombreRaw = 'manual_{n}_{index}_raw.jpg'.format(n=self.nFoto, index=self.index)
        else:
            nombre = 'manual_{n}_{index}.jpg'.format(n=self.nFoto, index=self.index)
            nombreRaw = 'manual_{n}_{index}_raw.jpg'.format(n=self.nFoto, index=self.index)

        guardado1 = cv2.imwrite('{carpeta}{separador}{nombre}'.format(carpeta=carpeta, separador=variablesGlobales.separadorCarpetas ,nombre=nombre), self.lastImg)
        guardado2 = cv2.imwrite('{carpeta}{separador}{nombre}'.format(carpeta=carpeta, separador=variablesGlobales.separadorCarpetas ,nombre=nombreRaw), self.lastRawImg)
        if(guardado1 and guardado2):
            print('Guardado ', nombre)
        else:
            print("No se ha podido guardar la imagen")
        self.nFoto += 1
        #print("Tiempo medio (s): ", self.media, " fps: ", 1/self.media)

    def read(self):
        
        self.lock.acquire() #Nos ponemos a la espera si el thread está bloqueado
        
        estado = np.copy(self.estadoAct)
        viendoLinea = self.index == self.getNumEstados()-1
        lastImg = np.copy(self.lastImg)

        if (self.lock.locked()):
            self.lock.release()

        return estado, viendoLinea, lastImg

    def getEstadoAct(self):
        
        self.lock.acquire() #Nos ponemos a la espera si el thread está bloqueado
        
        estado = np.copy(self.estadoAct)

        if (self.lock.locked()):
            self.lock.release()

        return estado