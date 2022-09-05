
from lib.preprocesado.preprocesado import Preprocesado
from lib.singleton import SingletonVariables

import cv2
import numpy as np

import glob
carpeta = 'mascaras03'

widePercent = 0

PORCENTAJE_MAX = 0.15 # Umbral para considerar que la máscara más similar a la imagen no es suficientemente similar como para considerar que se ve la linea

class PreprocesadoMascaras(Preprocesado):
    def __init__(self, dimensiones, carpetaKernels = carpeta):
        
        super().__init__(dimensiones)
        
        self.numkernels = 0
        self.listaMascaras, self.listaPuntuacionMin = self._cargarMascaras(carpetaKernels)
        self.listaMascaras = np.array(self.listaMascaras)
        # Variables para poder guardar la ultima imagen capturada en memoria
        self.lastImg = None
        self.lastRawImg = None
        
        self.estadoAct= np.zeros(self.numkernels)
        self.mejorMedida = 0.0
        self.mejorIndice = 0
        self.viendoLinea = True

        print(self.listaPuntuacionMin)
        
    
    def _cargarMascaras(self, carpeta):
        
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

            listaPuntuacionMax.append(np.sum(img) * PORCENTAJE_MAX)
            listaImgs.append(img) #Guardamos la imagen y la suma de sus pixeles para ahorrar cálculos posteriormente
            self.numkernels += 1
            #if self.numkernels == 5:
             #   break
        
        return listaImgs, listaPuntuacionMax

    def processImage(self, mask):
        
        #Cambiamos el espacio de color a HSV
        mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)
        #imgGray = cv2.resize(imgGray, (40,32))

        mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
        
        mask = cv2.erode(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)))
        
        _, mask = cv2.threshold(mask, 41, 255,cv2.THRESH_BINARY)
        
        #Recorte de la zona central inferior de la imagen
        #mask = mask[int((self.dimensiones[1])*0.4): int(self.dimensiones[1]-1), int(self.dimensiones[0]*(widePercent/2)):int(self.dimensiones[0]*(1-widePercent/2))]             
        
        mask = 1.0-(mask/255) #Invertir la imagen y cambiar el rango a (0.0, 1.0)
        
        mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))

        mask = cv2.GaussianBlur(mask,(11,1),0, cv2.BORDER_REPLICATE)
        
        #cv2.imshow("mascara",mask)

        #Comprobar cual de los kernels se solapa mejor con la imagen
        listaImgsSim = []
        listaMedidaSim = []
        
        for kernel in self.listaMascaras:
            #Guardamos las imagenes de similitud 
            # y la suma de sus pixeles en la lista
            imgSimilitud= mask * kernel
          
            medidaSimilitud =  np.sum(imgSimilitud)
        
            listaImgsSim.append(imgSimilitud)
            listaMedidaSim.append(medidaSimilitud)

        return listaMedidaSim, listaImgsSim
        
    def getNumEstados(self):
        return self.numkernels + 1

    def getDictEstados(self):
        return dict(type='int', num_values=self.getNumEstados())

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

