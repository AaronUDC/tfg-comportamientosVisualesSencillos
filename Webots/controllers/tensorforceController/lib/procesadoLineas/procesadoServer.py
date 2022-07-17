

from datetime import datetime
import threading
from time import gmtime, strftime
import cv2
import numpy as np
from lib.singleton import SingletonVariables
from lib.procesadoLineas.hiloProcesado import HiloProcesadoImg

RESOLUCION_SALIDA_DEFECTO = (8,6)

MIN_LINEA_VISIBLE = 0.25

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

        sumImg = self.lastImg.sum()
        #print(sumImg)
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

    def getEstadoAct(self):
        return super().getEstadoAct()