


import threading
import cv2
import numpy as np
from lib.procesadoLineas.hiloProcesado import HiloProcesadoImg

RESOLUCION_SALIDA_DEFECTO = (10,10)

class ProcesadoImagen(HiloProcesadoImg):
    
    def __init__(self, apiControl, dimensiones, resolucionSalida = RESOLUCION_SALIDA_DEFECTO):
        super().__init__(apiControl, dimensiones)
        
        self.resolucionSalida = resolucionSalida

        self.estadoActual = np.zeros(self.resolucionSalida)
        self.viendoLinea = False
        self.lastImg = None
        self.lock = threading.Lock()
    
    def processImage(self, image):
        img = cv2.GaussianBlur(image,(5,5),0, borderType = cv2.BORDER_REPLICATE)
        
        #Cambiamos el espacio de color a escala de grises
        imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        #Umbralizar la imagen, o ponerla en blanco y negro
        mask = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41,10)
        
        mask = np.round(mask /255)

        #Reescalar la imagen a la resolución de salida
        resizedMask = cv2.resize(mask, self.resolucionSalida, interpolation=cv2.INTER_LINEAR)

        self.lastImg = resizedMask*255

        return resizedMask

    def update(self):
        while not self.stopped:
            img = self.apiControl.getDatosCamara()
            
            estado = self.processImage(img)

            self.lock.acquire(blocking=False)

            self.estadoActual =  estado

            if (self.lock.locked()):
                self.lock.release()

    def getNumEstados(self):
        return self.resolucionSalida[0]*self.resolucionSalida[1]
    
    def getDictEstados(self):
        return dict(type= 'int', shape=self.resolucionSalida, num_values = 2, min_value = 0, max_value = 1)
    
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