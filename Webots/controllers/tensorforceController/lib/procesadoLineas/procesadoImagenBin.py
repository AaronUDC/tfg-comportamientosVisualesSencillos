


from datetime import datetime
import threading
from time import gmtime, strftime
import cv2
import numpy as np
from lib.singleton import SingletonVariables
from lib.procesadoLineas.hiloProcesado import HiloProcesadoImg

RESOLUCION_SALIDA_DEFECTO = (8,6)

MIN_LINEA_VISIBLE = 0.15

class ProcesadoImagenBin(HiloProcesadoImg):
    
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
        return dict(type= 'int', shape=self.resolucionSalida, num_values = 256)
    
    def printUltimaFotog(self):
        carpeta = 'savedPhotos'

        hora = datetime.now()
        horaSt= hora.strftime('%d.%m.%Y_%H.%M.%S.%f')

        #self.lock.acquire() #Nos ponemos a la espera si el thread está bloqueado
		#Guardar la ultima imagen almacenada en un archivo, incluyendo el angulo e indice asignado.
        
        variablesGlobales = SingletonVariables()

        nombre = 'manual_procesadoImagen_{fecha}_.jpg'.format(fecha= horaSt)
        nombreRaw = 'manual_procesadoImagen_{fecha}_raw.jpg'.format(fecha= horaSt)

        guardado1 = cv2.imwrite('{carpeta}{separador}{nombre}'.format(carpeta=carpeta, separador=variablesGlobales.separadorCarpetas ,nombre=nombre), self.lastImg)
        guardado2 = cv2.imwrite('{carpeta}{separador}{nombre}'.format(carpeta=carpeta, separador=variablesGlobales.separadorCarpetas ,nombre=nombreRaw), self.lastRawImg)
        
        if(guardado1 and guardado2):
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