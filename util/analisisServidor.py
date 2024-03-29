
from cProfile import label
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
    listaTimestamps = list()
    listaTiemposProcesadoServer = list()

    for paquete in listaRecibidos:
        tiempo = paquete[2] - paquete[1]
        listaTiempos.append(tiempo)
        listaTiemposProcesadoServer.append(paquete[3])
        listaTimestamps.append(paquete[1])

    listaTiemposNp = np.array(listaTiempos)
    listaTimestampsNp = np.array(listaTimestamps)
    listaTiemposProcesadoServerNp = np.array(listaTiemposProcesadoServer)

    print(listaRecibidos[listaTiempos.index(np.max(listaTiemposNp))])

    print("Tiempo medio recepcion (ms): ", np.mean(listaTiemposNp[2:]))
    print("Mediana tiempo recepcion (ms): ", np.median(listaTiemposNp[2:]))
    print("Tiempo maximo: ", np.max(listaTiemposNp[2:]), " Minimo:", np.min(listaTiemposNp[2:]))
    print("Varianza: ", np.var(listaTiemposNp[2:]))
    print("Desviación Típica: ", np.std(listaTiemposNp[2:]))

    #plt.hist(listaTiemposNp,100)

    plt.plot(listaTimestampsNp[2:],listaTiemposNp[2:],"k.-", label ="Tiempo de respuesta del servidor", lw = 1, ms= 4)
    plt.plot(listaTimestampsNp[2:],listaTiemposProcesadoServerNp[2:],"b.-", label ="Tiempo de procesado del servidor", lw = 1, ms= 4)
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
    

    