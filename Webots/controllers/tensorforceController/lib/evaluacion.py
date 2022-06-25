
import os
import numpy as np
import pandas as pd
from datetime import datetime

from lib.singleton import SingletonVariables
class Evaluador:

    def __init__(self, nombreAgente):

        self.nombreAgente = nombreAgente

        self.episodio_tiempo = list()
        self.episodio_estados = list()
        self.episodio_acciones = list()
        self.episodio_terminales = list()
        self.episodio_refuerzos = list()



    def almacenarPaso(self,tiempo ,estado, acciones, terminal, refuerzo):

        self.episodio_tiempo.append(tiempo)
        self.episodio_estados.append(estado)
        self.episodio_acciones.append(acciones)
        self.episodio_terminales.append(terminal)
        self.episodio_refuerzos.append(refuerzo)

    def getRecompensaAcumuladaDescontada(self, gamma = 1):
        #Con un gamma de 1, no hay descuento.
        suma= 0.0

        for i, refuerzo in enumerate(self.episodio_refuerzos, start = 1):
            suma += (gamma**i) * refuerzo
        
        return suma

    def getNumEstadosTerminales(self):
        #Contarmos las veces que tenemos un true en la lista.
        return  sum(self.episodio_terminales)
    
    def getNumRefuerzosNegativos(self):
        #Contar las veces que se da un refuerzo inferior a 0
        #print(self.episodio_refuerzos)
        return sum(refuerzo > 0 for refuerzo in self.episodio_refuerzos) 


    def guardarEpisodio(self, ruta):
        
        if not os.path.exists(ruta):
            os.makedirs(ruta)
            print("se ha creado una carpeta en:", ruta)
        
        #Creamos el array de datos en formato CSV
        df = pd.DataFrame({
            'tiempo': self.episodio_terminales,
            'estados': self.episodio_estados,
            'acciones': self.episodio_acciones,
            'terminales': self.episodio_terminales,
            'refuerzos': self.episodio_refuerzos,
        })

        variablesGlobales = SingletonVariables()

        hora = datetime.now()
        horaSt= hora.strftime('%d.%m.%Y_%H.%M.%S')
        nombreArchivo = 'evaluacion_agente_{agente}_{fecha}.csv'.format(agente= self.nombreAgente,fecha= horaSt)

        formatoCSV = df.to_csv('{carpeta}{separador}{nombre}'.format(carpeta=ruta, separador=variablesGlobales.separadorCarpetas ,nombre=nombreArchivo))
        if (formatoCSV is not None):
            print("se han guardado los datos de validación en:", nombreArchivo)