
import os
import cv2
import numpy as np
import pandas as pd
from datetime import datetime

from requests import head

from lib.singleton import SingletonVariables
from tensorforce.agents import Agent
class Evaluador:

    def __init__(self, nombreAgente):

        self.nombreAgente = nombreAgente
        self.agente = None

        self.episodio_tiempo = list()
        self.episodio_estados = list()
        self.episodio_acciones = list()
        self.episodio_terminales = list()
        self.episodio_refuerzos = list()


    def setAgente(self, agente):
        self.agente = agente

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

    def _guardarEstados(self,ruta, hora):

        horaSt= hora.strftime('%d.%m.%Y_%H.%M.%S')

        variablesGlobales = SingletonVariables()
        rutaEstados = '{carpeta}{separador}states'.format(carpeta=ruta, separador=variablesGlobales.separadorCarpetas )
        if not os.path.exists(rutaEstados):
            os.makedirs(rutaEstados)

        listaRutas=list()

        for (i,(estado,tiempo)) in  enumerate(zip(self.episodio_estados,self.episodio_tiempo)):
            nombreArchivo = "state_{agente}_{hora}.{fotograma:06}.png".format(
                agente = self.nombreAgente, hora = horaSt, tiempo = tiempo, fotograma= i)
            rutaArchivo = "{ruta}{separador}{archivo}".format(
                ruta = rutaEstados, separador = variablesGlobales.separadorCarpetas,
                archivo = nombreArchivo)

            #print(rutaArchivo)
            cv2.imwrite(rutaArchivo, estado)
            listaRutas.append(nombreArchivo)

        return listaRutas

    def _guardarAgente(self, ruta):

        variablesGlobales = SingletonVariables()
        rutaAgente= '{carpeta}{separador}agent'.format(carpeta=ruta, separador=variablesGlobales.separadorCarpetas )
        if not os.path.exists(rutaAgente):
            os.makedirs(rutaAgente)

        print(self.agente.save(directory=rutaAgente, filename=self.nombreAgente))

        rutaAgenteModel= '{carpeta}{separador}agentModel'.format(carpeta=ruta, separador=variablesGlobales.separadorCarpetas )
        if not os.path.exists(rutaAgenteModel):
            os.makedirs(rutaAgenteModel)

        print(self.agente.save(directory=rutaAgenteModel, filename=self.nombreAgente, format = "saved-model"))
        

    def guardarEpisodio(self, ruta):
        
        variablesGlobales = SingletonVariables()

        hora = datetime.now()
        horaSt= hora.strftime('%d.%m.%Y_%H.%M.%S')

        rutaEvaluacion = '{carpeta}{separador}{agente}_{fecha}'.format(carpeta=ruta, separador=variablesGlobales.separadorCarpetas, agente = self.nombreAgente,fecha= horaSt)

        if not os.path.exists(rutaEvaluacion):
            os.makedirs(rutaEvaluacion)
            print("se ha creado una carpeta en:", rutaEvaluacion)
        
        listaRutas = self._guardarEstados(rutaEvaluacion, hora)

        if self.agente is not None:
            self._guardarAgente(rutaEvaluacion)

        #Creamos el array de datos en formato CSV
        df = pd.DataFrame({
            'tiempo': self.episodio_tiempo,
            'estados': listaRutas,
            'acciones': self.episodio_acciones,
            'terminales': self.episodio_terminales,
            'refuerzos': self.episodio_refuerzos,
        })

        nombreArchivo = 'evaluacion_agente_{agente}_{fecha}.csv'.format(agente= self.nombreAgente,fecha= horaSt)

        formatoCSV = df.to_csv('{carpeta}{separador}{nombre}'.format(carpeta=rutaEvaluacion, separador=variablesGlobales.separadorCarpetas ,nombre=nombreArchivo))
        if (formatoCSV is not None):
            print("se han guardado los datos de evaluación en:", nombreArchivo)
