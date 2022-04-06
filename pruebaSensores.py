#from picamera import PiCamera

from lib.aurigapy.aurigapy import *
from lib.hiloLineasCamara import HiloLineasCam
from lib.hiloQLearning import HiloQLearning
from lib.hiloControl import HiloControl
from lib.singleton import SingletonVariables
import time
from datetime import datetime
from time import gmtime, strftime

import pygame
from pygame.locals import *

done = False

parado = False
joystickEnabled = False

sensorDer = 0
sensorIz = 0


rA = 0.7 #Ratio de aprendizaje
gamma = 0.82

variablesGlobales = SingletonVariables()

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
		
		if sensorDer == 0 or sensorDer == 1:
			hiloControl.pararRobot()
			
	if done:
		return
	
	#variablesGlobales.auriga.get_line_sensor(6, callback= on_sensor_read_r)
	
def on_sensor_read_l(value, timeout):
	global sensorIz, variablesGlobales
	
	if not timeout:
		sensorIz = int(value)
		#print("%r > %r (%r) 2" % (timestamp(), sensorIz, timeout))		
		
		if sensorIz == 0 or sensorIz == 2:
			hiloControl.pararRobot()
			
	if done:
		return
		
	#variablesGlobales.auriga.get_line_sensor(7, callback= on_sensor_read_l)


def ejecutarAccion(auriga, accion, inversa = False):
    mod = 1
    if inversa:
        mod = -1
    
    if accion == 0:
        auriga.set_speed(-50 * mod, 50 * mod) #Avanzar

    elif accion == 1:
        auriga.set_speed(-40 * mod, 80 * mod) #Girar a la derecha

    elif accion == 2:
        auriga.set_speed(-80 * mod, 40 * mod) #Girar a la izquierda

    elif accion == 3:
        auriga.set_speed(-10 * mod, 100 * mod) #Girar fuerte a la derecha

    elif accion == 4:
        auriga.set_speed(-100 * mod, 10 * mod) #Girar fuerte a la izquierda
        


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
					print("Tabla Q, Random Prob: ", hiloQLearning.randomProb)
					print(hiloQLearning.tablaQ)
			elif event.type == pygame.JOYBUTTONDOWN:
				if event.button == 0:
					#Volver a permitir el movimiento
					hiloControl.reanudarRobot()
				elif event.button == 1:
					#Parada de emergencia
					hiloControl.pararRobot()

                
		if not parado:
			#Actualizar tabla Q
			continue


if __name__ == '__main__':
	try:
		
		# Inicializar el hilo de la camara
		resolucionCam = (80, 64)

		hiloLineasCam = HiloLineasCam(resolucionCam).start()
		pygame.init()
		screen = pygame.display.set_mode((400,400))

		# Cogemos el reloj de pygame 
		reloj = pygame.time.Clock()

		ap = AurigaPy(debug=False)
		bluetooth = "/dev/tty.Makeblock-ELETSPP"
		usb = "/dev/ttyUSB0"
		
		mando = None
		pygame.joystick.init()
		if pygame.joystick.get_count()>0:
			mando = pygame.joystick.Joystick(0)
			mando.init()
			joystickEnabled = True
			print("mandoActivado")

		
		
		print(" Conectando..." )
		ap.connect(usb)
		print(" Conectado!" )
		time.sleep(0.2)
		ap.set_command(command="forward", speed=0, callback=on_reading) 
		variablesGlobales.auriga = ap
		variablesGlobales.parado = False
		
		hiloQLearning = HiloQLearning(hiloLineasCam.getNumEstados(),5,hiloLineasCam,rA,gamma, 2000) 
		hiloControl = HiloControl(hiloQLearning, ap)
		
		hiloQLearning.setHiloControl(hiloControl)
		
		hiloQLearning.start()
		#hiloControl.start()
		
		
		main(ap, hiloLineasCam, mando)
		
		
	finally:
		print('parado')
		hiloLineasCam.stop()
		hiloQLearning.stop()
		#hiloControl.stop()

		ap.set_command(command='forward',speed=0, callback=on_reading)
		time.sleep(2)
		ap.reset_robot()
		ap.close()
