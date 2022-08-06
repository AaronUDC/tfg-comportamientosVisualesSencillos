from datetime import datetime
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
        self.listaKernels, self.listaPuntuacionMin = self._getKernels(carpetaKernels)
        self.listaKernels = np.array(self.listaKernels)
        # Variables para poder guardar la ultima imagen capturada en memoria
        self.lastImg = None
        self.lastRawImg = None
        
        self.estadoAct= np.zeros(self.numkernels)
        self.mejorMedida = 0.0
        self.mejorIndice = 0
        self.viendoLinea = True

        print(self.listaPuntuacionMin)
        #Lock
        self.lock = threading.Lock()
        
    
    def _getKernels(self, carpeta):
        
        variablesGlobales = SingletonVariables()

        listaImgs = []
        listaPuntuacionMax = []
        for imagenPath in sorted(glob.glob('{carpeta}{separador}*.png'.format(carpeta = carpeta, separador = '/'))):
            #print(imagenPath)
            img = cv2.imread(imagenPath)
            
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            #img = img[int((self.dimensiones[1])*0.4): int(self.dimensiones[1]-1), int(self.dimensiones[0]*(widePercent/2)):int(self.dimensiones[0]*(1-widePercent/2))]             
            img = cv2.dilate(img, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))

            img = img/255.0 #Convertir una imagen de enteros de 0 a 255 a punto flotante de 0.0 a 1.0

            #img = cv2.resize(img, (40,32))

            listaPuntuacionMax.append(np.sum(img) * PORCENTAJE_MAX)
            listaImgs.append(img) #Guardamos la imagen y la suma de sus pixeles para ahorrar cálculos posteriormente
            self.numkernels += 1
            #if self.numkernels == 5:
             #   break
        
        return listaImgs, listaPuntuacionMax

    def processImage(self, mask):
        
        #t0 = time.process_time()

        #Cambiamos el espacio de color a HSV
        mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
        #imgGray = cv2.resize(imgGray, (40,32))

        mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))

        
        mask = cv2.erode(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
        _, mask = cv2.threshold(mask, 41, 255,cv2.THRESH_BINARY)
        
        #Recorte de la zona central inferior de la imagen
        #mask = mask[int((self.dimensiones[1])*0.4): int(self.dimensiones[1]-1), int(self.dimensiones[0]*(widePercent/2)):int(self.dimensiones[0]*(1-widePercent/2))]             
        
        mask = 1.0-(mask/255) #Invertir la imagen y cambiar el rango a (0.0, 1.0)
        mask = cv2.GaussianBlur(mask,(11,1),0, cv2.BORDER_REPLICATE)
        
        #cv2.imshow("mascara",mask)
        
        #t1 = time.process_time()

        #Comprobar cual de los kernels se solapa mejor con la imagen
        listaImgsSim = []
        listaMedidaSim = []
        #t1 = time.process_time()

        
        for kernel in self.listaKernels:
            #Guardamos las imagenes de similitud y la suma de sus pixeles en la lista
            imgSimilitud= mask * kernel
            
          
            medidaSimilitud =  np.sum(imgSimilitud)
        
            listaImgsSim.append(imgSimilitud)
            listaMedidaSim.append(medidaSimilitud)

        #t2 = time.process_time()

        return listaMedidaSim, listaImgsSim#, (t0,t1,t2)
    
    def getEstado(self, imagen):
        
        listaMedidas, listaImgs = self.processImage(imagen)
        
        mejorMedida = np.max(listaMedidas)
        mejorIndice = listaMedidas.index(mejorMedida)
        
        self.lastImg = listaImgs[mejorIndice] * 255
        self.lastRawImg = imagen

        
        if (mejorMedida > self.listaPuntuacionMin[mejorIndice]):
            #Comprobar si la mejor imagen tiene una puntuación minima
            
            return mejorIndice, True 
        else:
            #En caso contrario consideramos que no se ve la linea
            return self.getNumEstados()-1, False
        
        
    
    
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
            self.mejorMedida = mejorMedida
            self.mejorIndice = mejorIndice
            
            if (mejorMedida > self.listaPuntuacionMin[mejorIndice]):
                #Comprobar si la mejor imagen tiene una puntuación minima
                self.viendoLinea = True
            else:
                #En caso contrario consideramos que no se ve la linea
                self.viendoLinea = False
                
            
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

        hora = datetime.now()
        horaSt= hora.strftime('%d.%m.%Y_%H.%M.%S.%f')
        
        if self.viendoLinea is True:
            nombre = 'manual_mascaras_{fecha}_Linea_{puntos}_i{indice}'.format(fecha = horaSt,puntos = self.mejorMedida, indice=self.mejorIndice)
        else:
            nombre = 'manual_mascaras_{fecha}_NOLinea_{puntos}_i{indice}'.format(fecha = horaSt,puntos = self.mejorMedida, indice=self.mejorIndice)


        guardado1 = cv2.imwrite('{carpeta}{separador}{nombre}.jpg'.format(carpeta=carpeta, separador=variablesGlobales.separadorCarpetas ,nombre=nombre), self.lastImg)
        guardado2 = cv2.imwrite('{carpeta}{separador}{nombre}_raw.jpg'.format(carpeta=carpeta, separador=variablesGlobales.separadorCarpetas ,nombre=nombre), self.lastRawImg)
        if(guardado1 and guardado2):
            print('Guardado ', nombre)
        else:
            print("No se ha podido guardar la imagen")

    def read(self):
        
        self.lock.acquire() #Nos ponemos a la espera si el thread está bloqueado
        
        estado = np.copy(self.estadoAct)
        viendoLinea = self.viendoLinea
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
