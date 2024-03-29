

from lib.agenteQLearning import AgenteQLearning
from lib.entorno import Entorno
from lib.singleton import SingletonVariables
from lib.evaluacion import Evaluador

import time
from datetime import datetime
from time import gmtime, strftime
import threading

import argparse
import pathlib
import configparser
import platform

import numpy as np

import pygame
from pygame.locals import *

NUM_VUELTAS = 5

done = False

parado = False

mando = None

joystickEnabled = False

RA = 0.5 #Ratio de aprendizaje
GAMMA = 0.80

#Inicializamos el singleton para almacenar variables globales entre objetos
variablesGlobales = SingletonVariables()

variablesGlobales.parado = False
variablesGlobales.guardarFotos = False
variablesGlobales.version = '1'

#Comprobar el sistema operativo para adaptar como se crean las rutas de archivos
if platform.system() == 'Windows': 
    variablesGlobales.separadorCarpetas = "\\"
else:
    variablesGlobales.separadorCarpetas = '/'

paradaTerminal = False

#Variables de configuración
rutaAgente = None
nombreAgente = 'agent'
guardarAgente = False
agenteDefecto = ''
apiSt = 'apiControl'

#Variables para la evaluacion
guardarEvaluacion = False
rutaEvaluacion = None
evaluadorRobot = None
# Inicializamos una opcion de NumPy para mostrar datos en punto flotante
# con 3 digitos decimales de precision al imprimir un array

np.set_printoptions(precision=3, floatmode= "fixed")

agente = None
entorno = None
controlRobot = None

def parseConfig():
    #Parsear argumentos 
    global rutaAgente, guardarAgente, guardarEvaluacion, apiSt,nombreAgente, agenteDefecto, rutaEvaluacion


    config = configparser.ConfigParser()
    config.read('config.ini')

    if config['DEFAULT']['directorioAgente'] != '':
        rutaAgente = config['DEFAULT']['directorioAgente']

    if config['DEFAULT']['nombreAgente'] != '':
        nombreAgente = config['DEFAULT']['nombreAgente']

    if config['DEFAULT']['agenteDefecto'] != '':
        agenteDefecto = config['DEFAULT']['agenteDefecto']

    
    guardarAgente = config['DEFAULT'].getboolean('guardarAgente')

    guardarEvaluacion = config['EVALUACION'].getboolean('guardarEvaluacion')
    
    if config['EVALUACION']['rutaEvaluacion'] != '':
        rutaEvaluacion = config['EVALUACION']['rutaEvaluacion']

    apiSt = config['DEFAULT']['API']

    #print(args, path, guardarTabla)

def seleccionarApiControl():
    api = None

    if apiSt == 'apiWebots':
        from lib.apiWebots import ApiWebots
        api =  ApiWebots()

    elif apiSt == 'apiAuriga':
        from lib.apiAuriga import ApiAuriga

        api = ApiAuriga()

    else:
        from lib.apiControl import ApiControlRobot
        api = ApiControlRobot()

    return api

def bucleAprendizaje():
    
	global done, parado, variablesGlobales, entorno, agente, paradaTerminal
	recompensa= 0
	estados = entorno.reset()
	agente.act(estados)

	print("Estado inicial: ", estados)
	terminal = False
	recompensa = None
	variablesGlobales.parado = True
	while not done:
		#print (imagen)
		if not variablesGlobales.parado:
			
			#Al ser terminal, terminamos el episodio y reiniciamos el entorno (Volver a la linea/parar)
			if terminal: 
				estados = entorno.reset()
				terminal = False
			
			if paradaTerminal:
				#Si se ordena una parada desde el mando, se actúa acorde.
				print("Parada Terminal")
				paradaTerminal = False
				variablesGlobales.parado = True

			acciones = agente.act(estados)

			estadoAnt= estados
			
			if guardarEvaluacion:
				mask = controlRobot.preprocesado.lastImg
				raw = controlRobot.preprocesado.lastRawImg
			
			estados, terminal, recompensa = entorno.execute(acciones)
			            
			if guardarEvaluacion:
				evaluadorRobot.almacenarPaso(controlRobot.getTime(), estadoAnt, mask, raw, acciones, terminal, recompensa)

			agente.observe(terminal, recompensa,estados)

		else:
			controlRobot.update()
            


def controlManual():
	global done, variablesGlobales, paradaTerminal, controlRobot

	while not done:
		time.sleep(0.03)
		eventos = pygame.event.get()
		for event in eventos:
			
			if event.type == pygame.QUIT:
				done = True

			elif event.type == pygame.JOYBUTTONDOWN:
				if event.button == 2:# Btn X
					#Guardar el ultimo frame
					print("Parado: ", variablesGlobales.parado)
					print("Evaluacion")
					
					print("Recompensa acumulada descontada gamma=", agente.gamma)
					print(evaluadorRobot.getRecompensaAcumuladaDescontada(agente.gamma))
					print("Refuerzos negativos:", evaluadorRobot.getNumRefuerzosNegativos())
					print("Estados terminales:", evaluadorRobot.getNumEstadosTerminales())
					
					
				elif event.button == 0: #Btn A
					#Volver a permitir el movimiento

					#Reanudar la ejecucion de la parte del bucle que ejecuta acciones y aprende
					print("Reanudado")
					variablesGlobales.parado = False
					paradaTerminal = False
					  
					controlRobot.reanudar()

				elif event.button == 1: #Btn B
					#Parada de emergencias
					print("Parado")
					
					paradaTerminal = True  
					#Activar parada
					controlRobot.parada()
					
				elif event.button == 3: # Btn Y
					#Hacer un print de la tabla Q
					print("TablaQ\n",agente.tablaQ)

				elif event.button == 6:	#Btn BACK
					done = True
		
		if controlRobot.getVuelta() >= NUM_VUELTAS:
			done = True


if __name__ == '__main__':
	
	try:
		
		## Parseo del archivo de configuracion
		parseConfig()
		
		## Inicializacion de Pygame y el joystick
		pygame.init()

		pygame.joystick.init()
		if pygame.joystick.get_count()>0:
			mando = pygame.joystick.Joystick(0)
			mando.init()
			joystickEnabled = True
			print("MandoActivado")
			

		time.sleep(0.2)
		
		#Inicializar los módulos del controlador

		controlRobot = seleccionarApiControl()

		entorno = Entorno(controlRobot)

		#Inicializar el agente
		if rutaAgente is None: 
			print("Creando un agente nuevo")
			agente = AgenteQLearning(entorno, RA, GAMMA)
		else:
			print("Cargando agente de:", rutaAgente)
			agente = AgenteQLearning(entorno, RA, GAMMA)
			agente.cargarTablaQ(rutaAgente)
		
		if guardarEvaluacion:
			evaluadorRobot = Evaluador(nombreAgente, agente, rutaEvaluacion) 
		
		threadBucleAprendizaje = threading.Thread(target= bucleAprendizaje)
		threadBucleAprendizaje.start()
			
		#Módulo de control manual
		print("Iniciando bucle del mando")
		controlManual()
		
		
		threadBucleAprendizaje.join()
		
	finally:
		#Guardar el log del entrenamiento
		if guardarEvaluacion:
			evaluadorRobot.guardarEpisodio(guardarAgente)
		elif not guardarEvaluacion and guardarAgente:
			print(agente.guardarTablaQ(directorio="tmp"))
			
		
		#Terminar los módulos
		print("Finalizando ejecucion")
		entorno.close()
		
		controlRobot.terminarRobot()
	
