#from picamera import PiCamera

from lib.aurigapy.aurigapy import *

from lib.hiloCamara import HiloCamara
from lib.hiloLineas import HiloLineas

from lib.hiloQLearning import HiloQLearning
from lib.hiloControl import HiloControl
from lib.singleton import SingletonVariables
import time
from datetime import datetime
from time import gmtime, strftime

import numpy as np

import pygame
from pygame.locals import *

done = False

parado = False

mando = None
joystickEnabled = False

sensorDer = 0
sensorIz = 0

# Inicializar el hilo de la camara
resolucionCam = (80, 64)

rA = 0.7 #Ratio de aprendizaje
gamma = 0.82

#Inicializamos el singleton para almacenar variables globales entre objetos
variablesGlobales = SingletonVariables()

variablesGlobales.auriga = None
variablesGlobales.parado = False


# Inicializamos una opcion de NumPy para mostrar datos en punto flotante
# con 3 digitos decimales de precision al imprimir un array
np.set_printoptions(precision=3)

def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())
    
def on_reading(value, timeout):
    # TODO: it has to fail to acquire image at 33 miliseconds
    print("%r > %r (%r)" % (timestamp(), value, timeout))


#Lectura constante de cada sensor
def on_sensor_read_r(value, timeout):
	global sensorDer, variablesGlobales
	
	if not timeout:
		sensorDer = int(value)
		#print("%r > %r (%r) 1" % (timestamp(), sensorDer, timeout))
		
		if sensorDer != 3:
			hiloControl.pararRobot()
			
	if done:
		return
	
	#variablesGlobales.auriga.get_line_sensor(6, callback= on_sensor_read_r)
	
def on_sensor_read_l(value, timeout):
	global sensorIz, variablesGlobales
	
	if not timeout:
		sensorIz = int(value)
		#print("%r > %r (%r) 2" % (timestamp(), sensorIz, timeout))		
		
		if sensorIz != 3:
			hiloControl.pararRobot()
			
	if done:
		return
		
	#variablesGlobales.auriga.get_line_sensor(7, callback= on_sensor_read_l)



def main(ap, hiloLineasCam, mando):
	global done, parado, joystickEnabled, variablesGlobales
	
	
	while not done:
		reloj.tick(30)
		
		#print(sensorDer,sensorIz)
		variablesGlobales.auriga.get_line_sensor(6, callback= on_sensor_read_r)
		variablesGlobales.auriga.get_line_sensor(7, callback= on_sensor_read_l)
	
		#Gestion de los eventos para controlar el robot
		eventos = pygame.event.get()
		
		hiloControl.update()
		
		for event in eventos:
			
			if event.type == pygame.QUIT:
				done = True
			elif event.type == pygame.KEYDOWN:
                #Eventos de teclado
                #Control general
				if event.key == pygame.K_ESCAPE: 
					#Salir del programa pulsando ESC
					done = True
				elif event.key == pygame.K_o:
					#Guardar el ultimo frame
					print("Se ha almacenado la imagen")
					hiloLineasCam.printUltimaFotog()
				elif event.key == pygame.K_p:
					#Hacer un print de la tabla Q
					print("Tabla Q")
					print(hiloQLearning.tablaQ)
					
			elif event.type == pygame.JOYBUTTONDOWN:
				if event.button == 0:
					#Volver a permitir el movimiento
					hiloControl.reanudarRobot()
				elif event.button == 1:
					#Parada de emergencia
					hiloControl.pararRobot()
				elif event.button == 4:
					#Guardar el ultimo frame
					print("Se ha almacenado la imagen")
					hiloLineasCam.printUltimaFotog()
				elif event.button == 3:
					#Hacer un print de la tabla Q
					print("Tabla Q")
					print(hiloQLearning.tablaQ)
				elif event.button == 6:	
					done = True
		if not parado:
			#Actualizar tabla Q
			continue


if __name__ == '__main__':
	try:
		
		

		hiloCam = HiloCamara(resolucionCam).start()
		pygame.init()
		#screen = pygame.display.set_mode((400,400))

		# Cogemos el reloj de pygame 
		reloj = pygame.time.Clock()

		ap = AurigaPy(debug=False)
		bluetooth = "/dev/tty.Makeblock-ELETSPP"
		usb = "/dev/ttyUSB0"
		
		pygame.joystick.init()
		if pygame.joystick.get_count()>0:
			mando = pygame.joystick.Joystick(0)
			mando.init()
			joystickEnabled = True
			print("MandoActivado")


		print(" Conectando..." )
		ap.connect(usb)
		print(" Conectado!" )
		time.sleep(0.2)
		
		ap.set_command(command="forward", speed=0, callback=on_reading) 
		
		variablesGlobales.auriga = ap
		
		hiloLineas = HiloLineas(hiloCam, resolucionCam).start()
		
		hiloQLearning = HiloQLearning(hiloLineas.getNumEstados(),5,hiloLineas,rA,gamma) 
		hiloControl = HiloControl(hiloQLearning, ap)
		
		hiloQLearning.setHiloControl(hiloControl)
		
		hiloQLearning.start()
		#hiloControl.start()
		
		
		main(ap, hiloLineas, mando)
		
		
	finally:
		print('Finalizando la ejecución')
		hiloLineas.stop()
		hiloQLearning.stop()
		#hiloControl.stop()
		hiloCam.stop()
		
		ap.set_command(command='forward',speed=0, callback=on_reading)
		time.sleep(2)
		ap.reset_robot()
		ap.close()
