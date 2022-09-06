
import os

import pandas as pd
import numpy as np

from datetime import datetime

CARPETA_LOG = "logs_Servers"
class EvaluacionServer: 
	
	def __init__(self):
		
		
		self.logEnvios = list()

	def almacenarEnvio(self,tiempoEnvio, estado):
		datosEnvio = {
			"tiempoEnvio": tiempoEnvio,
			"tiempoRecepcion": None,
			"tiempoServer": None,
			"estado":estado,
			"accion": None,
			"recibido": False
			}
			
		self.logEnvios.append(datosEnvio)
			
		
	def almacenarPaso(self, tiempoEnvio, tiempoRecepcion, tiempoServer, estado, accion):
		
		datosEnvio = {
			"tiempoEnvio": tiempoEnvio,
			"tiempoRecepcion": tiempoRecepcion,
			"tiempoServer": tiempoServer,
			"estado":estado,
			"accion": accion,
			"recibido": True
			}
		self.logEnvios.append(datosEnvio)
		
	def guardarLog(self):

		hora = datetime.now()
		horaSt= hora.strftime('%Y.%m.%d_%H.%M.%S')

		rutaEvaluacion = '{carpeta}/logServer_{fecha}'.format(carpeta=CARPETA_LOG,fecha= horaSt)

		if not os.path.exists(rutaEvaluacion):
			os.makedirs(rutaEvaluacion)
			print("se ha creado una carpeta en:", rutaEvaluacion)
		

		#Creamos el array de datos en formato CSV
		df = pd.DataFrame(self.logEnvios)

		nombreArchivo = 'logServer_{fecha}.csv'.format(fecha= horaSt)

		formatoCSV = df.to_csv('{carpeta}/{nombre}'.format(carpeta=rutaEvaluacion,nombre=nombreArchivo))
		if (formatoCSV is not None):
			print("se han guardado los datos de evaluación en:", nombreArchivo)
