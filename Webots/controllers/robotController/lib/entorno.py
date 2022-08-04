
from lib.agenteQLearning import AgenteQLearning

from lib.singleton import SingletonVariables

from threading import Thread
import lib.apiControl

import time

from datetime import datetime
from time import gmtime, sleep, strftime

def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())
    
def on_reading(value, timeout):
    # TODO: it has to fail to acquire image at 33 miliseconds
    pass #print("%r > %r (%r)" % (timestamp(), value, timeout))

class Entorno():
	def __init__(self, controlRobot):
		
		self.variablesGlobales = SingletonVariables()
		self.controlRobot = controlRobot
		self.nAcciones = 5
		self.nEstados = self.controlRobot.procesadoLineas.getNumEstados()
		self.recompensa = 0
		
	def states(self):
		return self.nEstados
	
	def actions(self):
		return self.nAcciones
		
	def close(self):
		
		pass
		
	def reset(self):
		self.controlRobot.setAccion(6)
		
		estadoAct, _  = self.controlRobot.getEstado()
		
		return estadoAct
		
	def execute(self, accion):
		
		terminal = False
		#print("execute")
		self.controlRobot.setAccion(accion)
		
		#Actualizamos el robot
		self.controlRobot.update()
		
		#Obtenemos el estado actual
		
		next_state, viendoLinea = self.controlRobot.getEstado()

		#Establecer recompensas
		if (self.controlRobot.getSensorLinea())or self.variablesGlobales.parado:
			#Si se ha salido de la línea, es un estado terminal
			#print("PenalizacionSalida")
			reward = -20
			terminal = True  
		elif not viendoLinea:
			#Penalizar si no se puede ver la linea
			#print("PenalizacionNoVer")
			reward = -10
		else:
			#Recompensa por seguir la linea normal
			reward = 0
		
		return next_state, terminal, reward
		

