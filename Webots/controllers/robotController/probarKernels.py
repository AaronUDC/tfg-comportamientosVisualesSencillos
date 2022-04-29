import cv2
import numpy as np

from lib.hiloLineas2 import HiloLineas2
from lib.singleton import SingletonVariables

import time
TAMANO_IMG = (80,46)

carpeta= "plantillas"
singleton = SingletonVariables()

singleton.separadorCarpetas = '\\'

imgBasePath = "savedPhotos\manual_1_190.00_24_raw.jpg"


if __name__ == '__main__':
    hiloLineas = HiloLineas2(None, (80,64), carpeta)
    '''
    for image in hiloLineas.listaKernels:
        cv2.imshow("Kernel",image)
        cv2.waitKey(0)
    '''
    print(hiloLineas.listaKernels[0][0].shape)
    imgPrueba = cv2.imread(imgBasePath)
    
    print(imgPrueba.shape)
    cv2.imshow("In",imgPrueba)
    cv2.waitKey(0)

    listaMedidaSim, listaImgsSim, (t0,t1,t2) = hiloLineas.processImage(imgPrueba)

    print('Tiempo 0:',round((t1-t0)*1000))
    print('Tiempo 1:',round((t2-t1)*1000))

    
    mejorMedida = np.max(listaMedidaSim)
    mejorIndice = listaMedidaSim.index(mejorMedida)

    print('Tiempo 2:',round((time.time()-t2)*1000))
    
    print("Mejor medida e indice: ", mejorMedida, mejorIndice)

    for i in range(len(listaMedidaSim)):
        
        cv2.imshow("Kernel",listaImgsSim[i])
        print(listaMedidaSim[i])
        cv2.waitKey(0)
        
    cv2.imwrite("mejor.png", listaImgsSim[mejorIndice]*255)