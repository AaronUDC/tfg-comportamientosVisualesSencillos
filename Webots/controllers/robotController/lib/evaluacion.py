
import os
import numpy as np
import pandas as pd
from datetime import datetime

import cv2

from lib.singleton import SingletonVariables
class Evaluador:

    def __init__(self, nombreAgente, agente, rutaEvaluacion):
        self.variablesGlobales = SingletonVariables()
        
        self.nombreAgente = nombreAgente
        self.agente = agente

        self.episodio_tiempo = list()
        self.episodio_estados = list()
        self.episodio_fotosMasc = list()
        self.episodio_fotosRaw = list()
        self.episodio_acciones = list()
        self.episodio_terminales = list()
        self.episodio_refuerzos = list()
        
        self.cicloActual = 0
        
        self.rutaLog = self._crearCarpetaLogs(rutaEvaluacion)
        
    def setAgente(self, agente):
        self.agente = agente
    
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
        return sum(refuerzo < 0 for refuerzo in self.episodio_refuerzos) 


    def _crearCarpetaLogs(self, rutaEvaluacion):
        hora = datetime.now()
        fechaSt= hora.strftime('%Y.%m.%d_%H.%M.%S')
        
        ruta = "{rutaEval}{separador}{nombreAgente}_{fecha}".format(rutaEval = rutaEvaluacion, separador = self.variablesGlobales.separadorCarpetas , nombreAgente = self.nombreAgente,fecha = fechaSt)

        rutaFotosMask = "{rutaLogs}{separador}mask".format(rutaLogs = ruta, separador = self.variablesGlobales.separadorCarpetas)
        rutaFotosRaw = "{rutaLogs}{separador}raw".format(rutaLogs = ruta, separador = self.variablesGlobales.separadorCarpetas)
        
        if not os.path.exists(ruta):
            os.makedirs(rutaFotosRaw)
            os.makedirs(rutaFotosMask)
            
            print("se ha creado una carpeta en:", ruta)

        return ruta
        
    def _guardarFoto(self, foto, tipo):
        #Guardar una foto en su carpeta segun el tipo
        
        nombre = "{tipo}{separador}{idFoto:010}.png".format(separador = self.variablesGlobales.separadorCarpetas,tipo = tipo, idFoto = self.cicloActual)
        
        ruta = "{rutaLogs}{separador}{nombre}".format(rutaLogs = self.rutaLog, separador = self.variablesGlobales.separadorCarpetas, nombre = nombre)
        
        cv2.imwrite(ruta, foto)
        
        return nombre
    
    def almacenarPaso(self,tiempo ,estado, fotoMascara, fotoRaw, acciones, terminal, refuerzo):

        self.episodio_tiempo.append(tiempo)
        self.episodio_estados.append(estado)
        self.episodio_acciones.append(acciones)
        self.episodio_terminales.append(terminal)
        self.episodio_refuerzos.append(refuerzo)
        
        #Guardar la foto y la máscara, guardamos el enlace a la foto correspondiente en la lista 
        nombre = self._guardarFoto(fotoMascara, "mask")
        self.episodio_fotosMasc.append(nombre)
        
        nombre = self._guardarFoto(fotoRaw, "raw")
        self.episodio_fotosRaw.append(nombre)
        self.cicloActual +=1
        
    def guardarEpisodio(self, guardarAgente):
        
        if guardarAgente:
            self.agente.guardarTablaQ(self.rutaLog)

        #Creamos el array de datos en formato CSV
        df = pd.DataFrame({
            'tiempo': self.episodio_terminales,
            'estados': self.episodio_estados,
            'fotosMasc': self.episodio_fotosMasc,
            'fotosRaw': self.episodio_fotosRaw,
            'acciones': self.episodio_acciones,
            'terminales': self.episodio_terminales,
            'refuerzos': self.episodio_refuerzos,
        })
        
        nombreArchivo = '{carpeta}{separador}log.csv'.format(carpeta=self.rutaLog, separador=self.variablesGlobales.separadorCarpetas)

        formatoCSV = df.to_csv(nombreArchivo)
        if (formatoCSV is not None):
            print("se han guardado los datos de validación en:", nombreArchivo)
