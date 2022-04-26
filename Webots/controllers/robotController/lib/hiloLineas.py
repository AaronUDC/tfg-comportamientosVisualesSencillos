from time import sleep
import cv2
import lib.apiControl
import numpy as np
import time
import math
from threading import Thread
import threading

from lib.singleton import SingletonVariables

angulosDefecto = np.array([-30, -10,-5, 0, 5, 10, 30])

widePercent = 0.1

class HiloLineas:
    def __init__(self,control, dimensiones,  angulos = angulosDefecto):
        
        self.apiControl = control

        # Inicializar los datos para el procesado de la imagen a un estado
        self.angulos = angulos
        self.indicesAngulos = np.arange(angulos.size)
        self.indicesLado = np.arange(1,4)

        self.dimensiones = dimensiones
        
        # Variables para poder guardar la ultima imagen capturada en memoria
        self.lastImg = None
        self.lastRawImg = None
        
        self.nFoto = 0
        self.angulo = 0 #Angulo calculado
        self.index = 0 #Indice del estado
        
        #Lock
        self.lock = threading.Lock()
        
        self.stopped = False
        

    def start(self):
            # start the thread to read frames from the video stream
            Thread(target=self.update, args=()).start()
            return self

    def _mayorContorno(self, listaContornos):
        # Recorrer una lista de contornos y devolver el más grande

        areas = []
        for contorno in listaContornos:
            areas.append(cv2.contourArea(contorno))

        mayorArea = np.max(areas)

        return listaContornos[areas.index(mayorArea)]
        
        

    def update(self):
        while not self.stopped:
            img = self.apiControl.getDatosCamara() #Leer imagen del thread de la camara

            if img is None:
                continue
            
            imgs=np.array(img ) #Convertirla en un array de numpy para que sea compatible
			# con las operaciones de openCV
			
			#Analisis del tiempo requerido para el procesado
            #t0 = time.time()
			
			# Agregamos un desenfoque gausiano para minimizar los artefactos pequenos
            imgs = cv2.GaussianBlur(imgs,(5,5),0, borderType = cv2.BORDER_REPLICATE)
            
            #Cambiamos el espacio de color a HSV
            imgGray = cv2.cvtColor(imgs, cv2.COLOR_RGB2GRAY)

            mask = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41,10)
            
            
            #Recorte de la zona central inferior de la imagen
            mask = mask[int((self.dimensiones[1])*0.4): int(self.dimensiones[1]-1), int(self.dimensiones[0]*(widePercent/2)):int(self.dimensiones[0]*(1-widePercent/2))]             
            
            #Girar la imagen 90º para simplificar el calculo del angulo
            mask = cv2.rotate(mask, cv2.ROTATE_90_CLOCKWISE)
            #Invertir la mascara
            mask = 255-mask
            
            mask2 = np.zeros_like(mask)
            #Obtener contornos
            cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            cnts = cnts[0] if len(cnts) == 2 else cnts[1]
            
            
            if cnts == None or len(cnts) == 0:
                #Si no se ha detectado nada, se asigna un 
                #estado que se corresponde con el ultimo de la lista
                self.lock.acquire(blocking=False) #Bloqueamos los datos antes de sobreescribirlos
                
                self.index = self.angulos.size * 3
                self.angulo = None
            else:
                
                mayorContorno = self._mayorContorno(cnts) #Obtener el contorno más grande

                cv2.drawContours(mask2, [mayorContorno], 0, (255), cv2.FILLED)
                
                if cv2.contourArea(mayorContorno) < mask.size * 0.1:
                    #Si lo que se ha detectado es demasiado pequeño, se asigna un 
                    #estado que se corresponde con el ultimo de la lista
                    
                    self.lock.acquire(blocking=False) #Bloqueamos los datos antes de sobreescribirlos
                    
                    self.index = self.angulos.size * 3
                    self.angulo = None
                
                else:
                    (rows, cols) = mask.shape

                    [vx, vy, x, y] = cv2.fitLine(mayorContorno, cv2.DIST_L1, 0, 0.01, 0.01)
                    
                    #Obtener el punto mas a la izquierda y mas a la derecha
                    lefty = int((-x * vy/vx) +y)
                    righty = int(((cols-x)* vy/vx) +y)
                    
                    #Calculo del angulo de la linea
                    self.angulo = math.atan2(vy,vx) *180/np.pi
                
                    indice = round(np.interp(self.angulo,self.angulos,self.indicesAngulos))

                    #Comprobar en que tercio de la vertical se encuentra
                    #el punto mas pegado al borde izquierdo
                    lado = 1
                    if lefty < mask.shape[1]*0.33: 
                        lado = 0
                    elif lefty > mask.shape[1] * 0.66:
                        lado = 2
                    
                    self.lock.acquire(blocking=False) #Bloqueamos los datos antes de sobreescribirlos
                    
                    #Asiganmos el estado segun el indice del angulo y el lado en el que se encuentra
                    self.index = indice + (self.angulos.size * lado)
                    
                
                    cv2.line(mask2,(cols-1, righty),(0,lefty), (127), 1)
                    
            #t1 = time.time()
            
            #actualizamos la ultima imagen almacenada
            self.lastImg = mask2
            self.lastRawImg = img
            
            if self.lock.locked():
                self.lock.release() #Liberamos los datos
                
            #print(1/(t1-t0), self.index)
            
    def getNumEstados(self):
        return self.angulos.size * 3 + 1
        
    def printUltimaFotog(self):
        
        carpeta = 'savedPhotos'

        self.lock.acquire() #Nos ponemos a la espera si el thread está bloqueado
		#Guardar la ultima imagen almacenada en un archivo, incluyendo el angulo e indice asignado.
        
        variablesGlobales = SingletonVariables()


        if self.angulo is None:
            nombre = 'manual_{n}_None_{index}.jpg'.format(n=self.nFoto, index=self.index)
            nombreRaw = 'manual_{n}_None_{index}_raw.jpg'.format(n=self.nFoto, index=self.index)
        else:
            nombre = 'manual_{n}_{angulo:.2f}_{index}.jpg'.format(n=self.nFoto, angulo=self.angulo, index=self.index)
            nombreRaw = 'manual_{n}_{angulo:.2f}_{index}_raw.jpg'.format(n=self.nFoto, angulo=self.angulo, index=self.index)

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
        
        return self.index, self.lastImg, self.angulo

       
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

        
