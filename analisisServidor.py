
import string
import cv2
import numpy as np
import pandas
import argparse
from matplotlib import pyplot as plt

def contarPaquetesRespondidos(datos):
    datosTrasp =  np.transpose(datos)
    #print(datosTrasp[6])
    columnaRecibido = datosTrasp[6]
    numRecibidos = np.count_nonzero(columnaRecibido)
    return numRecibidos

def tiempoDeRecepcionMedio(datos):
    listaRecibidos = [paquete for paquete in datos if paquete[6] == True]
    #print(listaRecibidos)
    listaTiempos = list()
    sum = 0
    for paquete in listaRecibidos:
        tiempo = paquete[2] - paquete[1]
        listaTiempos.append(tiempo)
        sum += tiempo

    listaTiemposNp = np.array(listaTiempos)
    
    print(listaRecibidos[listaTiempos.index(np.max(listaTiemposNp))])

    print("Tiempo medio recepcion (ms): ", np.mean(listaTiemposNp))
    print("Tiempo mediana recepcion (ms): ", np.median(listaTiemposNp))
    print("Tiempo maximo: ", np.max(listaTiemposNp), " Mininmo:", np.min(listaTiemposNp))
    print("Varianza: ", np.var(listaTiemposNp))
    print("Desviación Típica: ", np.std(listaTiemposNp))

    plt.hist(listaTiemposNp,100)
    plt.show()

if __name__ == '__main__':
  
    parser = argparse.ArgumentParser()

    parser.add_argument("path", help="Ruta al arhivo CSV de evaluación", type=str)

    args = parser.parse_args()

    path= args.path

    datos = pandas.read_csv(path)
    arrayDatos = datos.to_numpy()
    
    
    #Contar el numero de paquetes enviados, respondidos, y sin respuesta
    respondidos = contarPaquetesRespondidos(arrayDatos)
    enviados = arrayDatos.shape[0]
    print("Enviados: ", enviados, "\nRespondidos: ", respondidos, "\nSin respuesta (Parada): ", enviados-respondidos)
    
    #Medir tiempos de recepción medios
    tiempoDeRecepcionMedio(arrayDatos)
    

    