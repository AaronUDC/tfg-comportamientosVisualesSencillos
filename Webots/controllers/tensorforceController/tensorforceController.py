
from tkinter.messagebox import NO
from tensorforce import Agent
from lib.evaluacion import Evaluador
from lib.entornoLineas import EntornoLineas
from lib.singleton import SingletonVariables

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

controlRobot = None

resolucionCam = None

rA = 0.7 #Ratio de aprendizaje
gamma = 1

#Inicializamos el singleton para almacenar variables globales entre objetos
variablesGlobales = SingletonVariables()

variablesGlobales.auriga = None
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
np.set_printoptions(precision=3)
agente = None
entorno = None
def parseArgs():
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

    elif apiSt == 'apiServerTCP':
        from lib.apiServerTCP import ApiServerTCP

        api = ApiServerTCP()

    else:
        from lib.apiControl import ApiControlRobot
        api = ApiControlRobot()

    return api

def bucleAprendizaje():
    
	global done, parado, variablesGlobales, entorno, agente, paradaTerminal
	recompensa= 0
	controlRobot.update()

	estados = entorno.reset()

	print("Estado inicial: \n", np.reshape(estados, (8,10,1)))

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

			acciones = agente.act(states= np.reshape(estados/255.0, (8,10,1)))

			estadoAnt= estados
            
			if guardarEvaluacion:
				evaluadorRobot.almacenarPaso(controlRobot.getTime(),estadoAnt, acciones, terminal, recompensa)

			estados, terminal, recompensa = entorno.execute(acciones)
			
			agente.observe(terminal = terminal, reward = recompensa)


		else:
			controlRobot.update()
            

def main():
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
					print("TODO")
					
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

					print("Parado: ", variablesGlobales.parado)
					print("Evaluacion")
					print("Recompensa acumulada descontada gamma=", gamma)
					print(evaluadorRobot.getRecompensaAcumuladaDescontada(gamma))
					print("Refuerzoas negativos:", evaluadorRobot.getNumRefuerzosNegativos())
					print("Estados terminales:", evaluadorRobot.getNumEstadosTerminales())
					print(agente.get_architecture())

				elif event.button == 6:	#Btn BACK
					done = True
		
		if controlRobot.getVuelta() >= NUM_VUELTAS:
			done = True


if __name__ == '__main__':
	
	try:
		
		parseArgs()
		
		pygame.init()
		   
		pygame.joystick.init()
		if pygame.joystick.get_count()>0:
			mando = pygame.joystick.Joystick(0)
			mando.init()
			joystickEnabled = True
			print("MandoActivado")
			

		time.sleep(0.2)
		
		controlRobot = seleccionarApiControl()

		variablesGlobales.control = controlRobot

		resolucionCam = controlRobot.getResolucionCam()
        
		evaluadorRobot = Evaluador(nombreAgente)

		entorno = EntornoLineas(controlRobot)


		if rutaAgente is None:
			print("Creando un agente nuevo")
			agente = Agent.create(agent= agenteDefecto, environment= entorno)
		else:
			print("Cargando agente ", nombreAgente,' de ', rutaAgente)
			agente = Agent.load(directory = rutaAgente, filename= nombreAgente)


		threadBucleAprendizaje = threading.Thread(target= bucleAprendizaje)
		threadBucleAprendizaje.start()
			
		print("Iniciando bucle del mando")

		main()

		threadBucleAprendizaje.join()

	finally:
		
		if guardarAgente:
			evaluadorRobot.setAgente(agente)

		if guardarEvaluacion:
			evaluadorRobot.guardarEpisodio(rutaEvaluacion)
		
		if not guardarEvaluacion and guardarAgente:
			print(agente.save(directory="tmp", filename=nombreAgente))

		print("Finalizando ejecucion")
		entorno.close()
		
		controlRobot.terminarRobot()
	
