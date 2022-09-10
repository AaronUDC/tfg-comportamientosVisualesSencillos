

from cProfile import label
import string
from turtle import shape
import cv2
import numpy as np
import pandas
import argparse
from matplotlib import pyplot as plt

class Analisis:

    def numTerminales(self,datos):
        pass
    def numNegativos(self,datos):
        pass

    def numPasos(self,datos):
        pass

    def refuerzoDescontado(self,datos, gamma):
        pass

    def refuerzoDescontadoEnTiempo(self,datos, gamma):
        pass
    
class AnalisisQLearning(Analisis):

    def numTerminales(self,datos):
        return  sum(datos[6])

    def numNegativos(self,datos):
        return sum(refuerzo < 0 for refuerzo in datos[7]) 

    def numPasos(self,datos):
        return datos[0].shape[0]

    def refuerzoDescontado(self,datos, gamma):
        #Con un gamma de 1, no hay descuento.
        suma= 0.0

        for i, refuerzo in enumerate(datos, start = 0):
            suma += (gamma**i) * refuerzo
        
        return suma

    def refuerzoDescontadoEnTiempo(self,datos, gamma):
        
        refuerzoDescontado = np.zeros(shape = datos[7].shape)

        for i in range(datos[7].size):
            refuerzoDescontado[i] = self.refuerzoDescontado(datos[7][0:i], gamma)

        return refuerzoDescontado 

class AnalisisDeepQLearning(Analisis):

    def numTerminales(self,datos):
        return  sum(datos[4])

    def numNegativos(self,datos):
        return sum(refuerzo < 0 for refuerzo in datos[5]) 

    def numPasos(self,datos):
        return datos[0].shape[0]

    def refuerzoDescontado(self,datos, gamma):
        #Con un gamma de 1, no hay descuento.
        suma= 0.0

        for i, refuerzo in enumerate(datos, start = 0):
            suma += (gamma**i) * refuerzo
        
        return suma

    def refuerzoDescontadoEnTiempo(self,datos, gamma):
        
        refuerzoDescontado = np.zeros(shape = datos[5].shape)

        for i in range(datos[5].size):
            refuerzoDescontado[i] = self.refuerzoDescontado(datos[5][0:i], gamma)

        return refuerzoDescontado 

GAMMA = 1

if __name__ == '__main__':
  
    parser = argparse.ArgumentParser()

    parser.add_argument("path", help="Ruta al arhivo CSV de evaluación", type=str)
    parser.add_argument("-t", help="Tipo de algoritmo, 1 -> Q-Learning 2 -> DeepQlearning", type=int, nargs=1, default=[2])

    args = parser.parse_args()

    path= args.path
    tipo = args.t
    print(tipo)
    datos = pandas.read_csv(path)
    arrayDatos = datos.to_numpy()

    datosTrasp = arrayDatos.transpose()
    
    analizador = None
    if tipo[0] == 1:
        #QLearning
        analizador = AnalisisQLearning()
    elif tipo[0] == 2:
        analizador = AnalisisDeepQLearning()

    numPasos = analizador.numPasos(datosTrasp)
    numTerminales =  analizador.numTerminales(datosTrasp)
    numNegativos = analizador.numNegativos(datosTrasp)
    print("Numero de pasos: ", numPasos)
    print("Numero de estados terminales: ",numTerminales)
    print("Numero de refuerzos negativos: ", numNegativos)

    print("Recompensa acumulada (gamma = ", GAMMA, "): ", analizador.refuerzoDescontado(datosTrasp[5], GAMMA))
    
    refuerzoDescontadoEnTiempoList =  analizador.refuerzoDescontadoEnTiempo(datosTrasp, GAMMA)
    print("Refuerzo descontado a lo largo del tiempo")

    plt.plot(datosTrasp[0],refuerzoDescontadoEnTiempoList,"k-", label ="Refuerzo en el tiempo", lw = 1, ms= 4)
    plt.xlabel("Iteración")
    plt.ylabel("Refuerzo acumulado")
    plt.show()


