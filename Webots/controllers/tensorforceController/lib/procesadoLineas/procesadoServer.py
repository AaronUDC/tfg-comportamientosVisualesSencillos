

from datetime import datetime
import threading
from time import gmtime, strftime
import cv2
import numpy as np
from lib.singleton import SingletonVariables
from lib.procesadoLineas.hiloProcesado import HiloProcesadoImg

RESOLUCION_SALIDA_DEFECTO = (8,10)

MIN_LINEA_VISIBLE = 0.1

class ProcesadoServer(HiloProcesadoImg):
    
    def __init__(self, apiControl, dimensiones, resolucionSalida = RESOLUCION_SALIDA_DEFECTO):
        super().__init__(apiControl, dimensiones)
        
        self.resolucionSalida = resolucionSalida

        self.estadoActual = np.zeros(self.resolucionSalida)
        self.viendoLinea = True
        self.lastImg = None
        self.lastRawImg = None
        self.lock = threading.Lock()

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

    def update(self):
        while not self.stopped:
            img = self.apiControl.getDatosCamara()
            
            estado, visible = self.processImage(img)

            self.lock.acquire(blocking=False)

            if estado is not None:
                self.estadoActual =  estado
                self.viendoLinea  = visible

            
            if (self.lock.locked()):
                self.lock.release()

    def getNumEstados(self):
        return self.resolucionSalida[0]*self.resolucionSalida[1]*256
    
    def getDictEstados(self):
        return dict(type= 'int', shape=self.resolucionSalida, num_values= 256)
        #return dict(type= 'float', shape=self.resolucionSalida, min_value = 0.0, max_value = 255.0)
    
    def printUltimaFotog(self):
        carpeta = 'savedPhotos'

        hora = datetime.now()
        horaSt= hora.strftime('%d.%m.%Y_%H.%M.%S.%f')

        #self.lock.acquire() #Nos ponemos a la espera si el thread está bloqueado
		#Guardar la ultima imagen almacenada en un archivo, incluyendo el angulo e indice asignado.
        
        variablesGlobales = SingletonVariables()

        nombre = 'manual_procesadoImagen_{fecha}_.jpg'.format(fecha= horaSt)
        
        guardado1 = cv2.imwrite('{carpeta}{separador}{nombre}'.format(carpeta=carpeta, separador=variablesGlobales.separadorCarpetas ,nombre=nombre), self.lastImg)
         
        if(guardado1):
            print('Guardado ', nombre)
        else:
            print("No se ha podido guardar la imagen")


    def read(self):
        self.lock.acquire()

        estado = np.copy(self.estadoActual)
        viendoLinea = self.viendoLinea
        lastImg =  np.copy(self.lastImg)
        if (self.lock.locked()):
            self.lock.release()

        return estado, viendoLinea, lastImg

    def getEstado(self, image):
        resizedImg, viendoImg = self.processImage(image)
        
        self.lastImg = resizedImg
        self.lastRawImg = image

        return resizedImg, viendoImg