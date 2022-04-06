
from threading import Thread

from lib.aurigapy.aurigapy import *
import numpy as np
import time

import pygame

class HiloSensores:
	
	def __init__(self,auriga):
		
		self.auriga = auriga
		self.stopped = False
		
		self.sensores = np.ones((5,2))
		self.reloj = pygame.time.Clock()

		
	def start(self):
            # start the thread to read frames from the video stream
            Thread(target=self.update, args=()).start()
            return self

	def update(self):
		while not self.stopped:
			sensoriz = self.auriga.get_line_sensor(6)
			sensorder = sensoriz #self.auriga.get_line_sensor(7)
			
			print(sensoriz)
			if sensoriz != None and sensorder != None:
				self.sensores[:-1] = self.sensores[1:]
				self.sensores[-1][0] = sensoriz
				self.sensores[-1][1] = sensorder
				
			
	def read(self):
		#devolver el ultimo estado de los sensores
		return self.sensores
        
	def stop(self):
        # indicate that the thread should be stopped
		self.stopped = True
