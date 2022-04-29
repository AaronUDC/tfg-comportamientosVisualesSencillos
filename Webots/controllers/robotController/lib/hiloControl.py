
from lib.hiloQLearning import HiloQLearning

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

class HiloControl():
	def __init__(self, hiloQLearning, controlRobot, hiloLineas):
		
		self.variablesGlobales = SingletonVariables()
		self.controlRobot = controlRobot
		self.accion = 0
		
		self.hiloQLearning = hiloQLearning
		self.hiloLineas = hiloLineas

		self.recompensa = 0
		
		self.done = False
		

	def start(self):
		Thread(target=self.update, args=()).start()
		return self
        
	def update(self):
		#while not self.done: 
		
		#Si esta parado, parar el robot e ignorar otras acciones
		if self.variablesGlobales.parado:
			return
		else:
			#self.auriga.set_speed(-50,50, callback=on_reading)
			#print("a")
			#Realizar accion
			self.controlRobot.ejecutarAccion(self.accion)
			#Actualizar recompensa
			
			estado, _, _ = self.hiloLineas.read()

			if self.hiloLineas.getNumEstados()-1 == estado:
				#self.pararRobot()
				self.hiloQLearning.setRecompensa(-20)

			else:
				self.hiloQLearning.setRecompensa(0)

	    
	def stop(self):
		self.done = True
        			
	def pararRobot(self):
		if not self.variablesGlobales.parado:
			print("se ha detenido el robot")
			self.variablesGlobales.parado = True
			self.controlRobot.setMotores(0,0)

		self.hiloQLearning.setRecompensa(-20)
		
		sleep(0.05)
		#self.reanudarRobot()
		self.controlRobot.reset()
		
	def reanudarRobot(self):
		
		self.controlRobot.reset()
		if self.variablesGlobales.parado:
			self.variablesGlobales.parado = False


						
	def setAccion(self, accion):
		self.accion = accion
		
	def salidaDeLinea(self):
		self.accion
