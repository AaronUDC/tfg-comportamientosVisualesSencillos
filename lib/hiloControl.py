
from lib.hiloLineasCamara import HiloLineasCam
from lib.hiloQLearning import HiloQLearning

from lib.singleton import SingletonVariables

from threading import Thread
from lib.aurigapy.aurigapy import *

import time

from datetime import datetime
from time import gmtime, strftime

def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())
    
def on_reading(value, timeout):
    # TODO: it has to fail to acquire image at 33 miliseconds
    pass #print("%r > %r (%r)" % (timestamp(), value, timeout))

class HiloControl():
	def __init__(self, hiloQLearning, auriga):
		
		self.variablesGlobales = SingletonVariables()
		self.auriga = auriga
		self.accion = 0
		
		self.hiloQLearning = hiloQLearning
		
		self.recompensa = 1
		
		self.done = False
		
		
	def ejecutarAccion(self, auriga, accion, inversa = False):
		mod = 1
		if inversa:
			mod = -1
		#print(accion)
		if accion == 0:
			auriga.set_speed(-50 * mod, 50 * mod, callback=on_reading) #Avanzar

		elif accion == 1:
			
			auriga.set_speed(-40 * mod, 80 * mod, callback=on_reading) #Girar a la derecha

		elif accion == 2:
			auriga.set_speed(-80 * mod, 40 * mod, callback=on_reading) #Girar a la izquierda

		elif accion == 3:
			auriga.set_speed(-10 * mod, 100 * mod, callback=on_reading) #Girar fuerte a la derecha

		elif accion == 4:
			auriga.set_speed(-100 * mod, 10 * mod, callback=on_reading) #Girar fuerte a la izquierda
	
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
			self.ejecutarAccion(self.variablesGlobales.auriga, self.accion)
			#Actualizar recompensa
			
			self.hiloQLearning.setRecompensa(1)

	    
	def stop(self):
		self.done = True
        			
	def pararRobot(self):
		if not self.variablesGlobales.parado:
			print("se ha detenido el robot")
			self.variablesGlobales.parado = True
			self.auriga.set_speed(0,0, callback=on_reading)
		
		self.hiloQLearning.setRecompensa(-10)			
	
	def reanudarRobot(self):
		if self.variablesGlobales.parado:
			self.variablesGlobales.parado = False
				
	def setAccion(self, accion):
		self.accion = accion
		
	def salidaDeLinea(self):
		self.accion
