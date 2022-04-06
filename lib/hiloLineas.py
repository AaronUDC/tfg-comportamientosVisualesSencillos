from picamera import PiCamera
from time import sleep
import cv2
from lib.hiloCamara import HiloCamara
import numpy as np
import time
import math
from threading import Thread

class HiloLineas:
    def __init__(self,camara, dimensiones,  angulos = np.array([-30, -10,-3.75, 0, 3.75, 10, 30])):
        # initialize the camera and stream
        self.angulos = angulos
        self.indicesAngulos = np.arange(angulos.size)
        self.indicesLado = np.arange(1,4)
        self.dimensiones = dimensiones
        
        self.camara = camara

        self.stopped = False
        
        self.lastImg = None
        self.nFoto = 0
        self.angulo = 0
        self.index = 0

    def start(self):
            # start the thread to read frames from the video stream
            Thread(target=self.update, args=()).start()
            return self

    def update(self):
        while not self.stopped:
            img = self.camara.read() #Leer imagen del thread de la camara
            imgs=np.array(img) #Convertirla en un array de numpy para que sea compatible
                   # con las operaciones de openCV
            imgHSV = cv2.cvtColor(imgs, cv2.COLOR_RGB2HSV)
            (h,s,v) = cv2.split(imgHSV)

            mask = cv2.inRange(v, 50, 255)
            widePercent = 0.2
            
            mask = mask[int(self.dimensiones[1]*0.2): int(self.dimensiones[1]*0.7), int(self.dimensiones[0]*(widePercent/2)):int(self.dimensiones[0]*(1-widePercent/2))] #Recortede la zona central
            
            
            canny= cv2.Canny(mask,100,150, None,3)
            lines = cv2.HoughLines(canny, 1 , np.pi / 180, 20,None, 0, 0)

            x1 = 0
            x2 = 0

            y1 = 0
            y2 = mask.shape[1]

            #Calcular la línea media
            if lines is not None:
                for i in range(0, len(lines)):
                    rho = lines[i][0][0]
                    theta = lines[i][0][1]

                    a = math.cos(theta)
                    b = math.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    
                    pt1 = (int(x0 + 2000*(-b)), int(y0 + 2000*(a)))
                    
                    pt1 = (x0 + 1*(-b), y0 + 1*(a))

                    pend = (pt1[1]-y0)/(pt1[0]-x0)
                    
                    x1 = (((y1-y0)/pend) + x0) + x1
                    x2 = (((y2-y0)/pend) + x0) + x2

                x1 = int(x1/len(lines))
                x2 = int(x2/len(lines))

                self.angulo = math.atan2((x1-x2),-(y1-y2)) *180/np.pi

                indice = round(np.interp(self.angulo,self.angulos,self.indicesAngulos))
            
                lado = 1
                if x2< mask.shape[0]*0.33: 
                    lado = 0
                elif x2 > mask.shape[0] * 0.66:
                    lado = 2
                self.index = indice + (self.angulos.size * lado)
                
            else:
                self.index = self.angulos.size * 3
                
            self.lastImg = canny
    
    def getNumEstados(self):
        return self.angulos.size * 3 + 1
        
    def read(self):
        # return the frame most recently read
        return self.angulo, self.index
        
    def printUltimaFotog(self):
        
        cv2.imwrite('{n}_{angulo}_{index}.jpg'.format(n=self.nFoto, angulo=self.angulo, index=self.index),self.lastImg)
        self.nFoto += 1
        
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

        
