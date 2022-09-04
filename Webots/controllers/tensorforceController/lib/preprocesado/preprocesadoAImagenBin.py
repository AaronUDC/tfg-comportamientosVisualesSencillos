


from datetime import datetime
import threading
from time import gmtime, strftime
import cv2
import numpy as np
from lib.singleton import SingletonVariables
from lib.procesadoLineas.preprocesado import Preprocesado

RESOLUCION_SALIDA_DEFECTO = (8,10)

MIN_LINEA_VISIBLE = 0.15

class PreprocesadoAImagenBin(Preprocesado):
    
    def __init__(self, dimensiones, resolucionSalida = RESOLUCION_SALIDA_DEFECTO):
        super().__init__(dimensiones)
        
        self.resolucionSalida = resolucionSalida

        self.estadoActual = np.zeros(self.resolucionSalida)
        self.viendoLinea = True
        self.lastImg = None
        self.lastRawImg = None
        self.lock = threading.Lock()

        self.sumaMinima = (resolucionSalida[0]*resolucionSalida[1] * 256) * (1.0-MIN_LINEA_VISIBLE)
        print(self.sumaMinima)
    
    def processImage(self, image):
        img = cv2.GaussianBlur(image,(5,5),0, borderType = cv2.BORDER_REPLICATE)
        
        #Cambiamos el espacio de color a escala de grises
        imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        #Reescalar la imagen a la resolución de salida
        resizedMask = cv2.resize(imgGray, (self.resolucionSalida[1],self.resolucionSalida[0]), interpolation=cv2.INTER_LINEAR)

        self.lastImg = resizedMask
        self.lastRawImg = image

        sumImg = self.lastImg.sum()
        #print(sumImg)
        if sumImg < self.sumaMinima:
            return resizedMask, True 

        return resizedMask, False

    def getNumEstados(self):
        return self.resolucionSalida[0]*self.resolucionSalida[1]*256
    
    def getDictEstados(self):
        #return dict(type= 'int', shape=self.resolucionSalida, num_values= 256)
        return dict(type= 'float', shape=(8,10,1), min_value = 0.0, max_value = 1.0)

    def getEstado(self, image):
        resizedImg, viendoImg = self.processImage(image)
        
        self.lastImg = resizedImg
        self.lastRawImg = image

        return resizedImg, viendoImg