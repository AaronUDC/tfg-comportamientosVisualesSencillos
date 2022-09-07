

from datetime import datetime
import threading
from time import gmtime, strftime
import cv2
import numpy as np
from lib.singleton import SingletonVariables
from lib.preprocesado.preprocesado import Preprocesado

RESOLUCION_SALIDA_DEFECTO = (8,10)

MIN_LINEA_VISIBLE = 0.1

class PreprocesadoServer(Preprocesado):
    
    def __init__(self, dimensiones, resolucionSalida = RESOLUCION_SALIDA_DEFECTO):
        super().__init__(dimensiones)
        
        self.resolucionSalida = resolucionSalida

        self.estadoActual = np.zeros(self.resolucionSalida)
        self.viendoLinea = True
        self.lastImg = None
        self.lastRawImg = None

        self.sumaMinima = (resolucionSalida[0]*resolucionSalida[1] * 256) * (1.0-MIN_LINEA_VISIBLE)
        print(self.sumaMinima)
    
    def processImage(self, image):

        self.lastImg = image
        
        #_,mask = cv2.erode(image,np.ones((3,3)),iterations=1)
        dilatedImg = cv2.dilate(image, np.ones((3,3), np.uint8))
        diffImg = 255 - cv2.absdiff(image, dilatedImg)
        #print(np.min(diffImg))
        
        if np.max(diffImg) - np.min(diffImg) > (255 * 0.3):
            norm_img = cv2.normalize(diffImg,None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        else:
            norm_img = diffImg
        
        sumImg = norm_img.sum()
        #print(sumImg, self.sumaMinima)
        if sumImg < self.sumaMinima:

            return image, True 

        return image, False

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