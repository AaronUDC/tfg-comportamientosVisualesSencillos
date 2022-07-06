




#from lib.apiWebots import ApiWebots
#from lib.apiControl import ApiControlRobot

from tensorforce import Agent
from lib.evaluacion import Evaluador
from lib.entornoLineas import EntornoLineas
from lib.singleton import SingletonVariables
from lib.procesadoLineas.procesadoMascaras import ProcesadoMascaras
from lib.procesadoLineas.procesadoImagenBin import ProcesadoImagenBin

import time
from datetime import datetime
from time import gmtime, strftime

import argparse
import pathlib
import configparser
import platform

import numpy as np

import pygame
from pygame.locals import *


NUM_VUELTAS = 3

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


def cambiarCapturaFotos():
    global variablesGlobales

    if variablesGlobales.guardarFotos:
        variablesGlobales.guardarFotos = False
        print("Se ha parado la captura de fotos")
    else:
        variablesGlobales.guardarFotos = True
        print("Captura de fotos iniciada")

def main(entorno, agente):
    global done, parado, variablesGlobales, evaluadorRobot
    recompensa= 0
    estados = entorno.reset()
    terminal = False
    
    crucetaSuelta = True
    while not done:
        
        eventos = pygame.event.get()
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
                    hiloProcesadoLineas.printUltimaFotog()
                elif event.key == pygame.K_p:
                    #Hacer un print de la tabla Q
                    print("Datos del conocimiento")
                    print("Recompensa =", recompensa)
                    print("Estados =", estados)
                    print("Acciones =", acciones)
                    print(agente.get_architecture())
                    print(agente.get_specification())
                    
                    #print(hiloQLearning.tablaQ)
                    
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0: #Btn A
                    #Volver a permitir el movimiento
                    if variablesGlobales.parado:
                        #Reanudar la ejecucion de la parte del bucle que ejecuta acciones y aprende
                        #hiloControl.reanudarRobot()
                        variablesGlobales.parado = False
                        
                elif event.button == 1: #Btn B
                    #Parada de emergencia
                    if not variablesGlobales.parado:
                        #Ordenar la detencion del bucle
                        #hiloControl.pararRobot()
                        variablesGlobales.parado = True

                elif event.button == 2:# Btn X
                    #Guardar el ultimo frame
                    print("Se ha almacenado la imagen")
                    hiloProcesadoLineas.printUltimaFotog()
                elif event.button == 3: # Btn Y
                    #Hacer un print de la tabla Q
                    '''print("Datos del conocimiento")
                    print("Recompensa =", recompensa)
                    print("Estados =", estados)
                    print("Acciones =", acciones)
                    '''
                    print("Arquitectura")
                    print(agente.get_architecture())
                    print("Especificacion")
                    print(agente.get_specification())
                    print("Tensores")
                    print(agente.tracked_tensors())
                    
                    print("Evaluacion")
                    print("Recompensa acumulada descontada gamma=", gamma)
                    print(evaluadorRobot.getRecompensaAcumuladaDescontada(gamma))
                    print("Refuerzoas negativos:", evaluadorRobot.getNumRefuerzosNegativos())
                    print("Estados terminales:", evaluadorRobot.getNumEstadosTerminales())

                elif event.button == 6:	#Btn BACK
                    done = True

                elif event.button == 4: #Btn LB
                    cambiarCapturaFotos()

        
        #TODO: Actualizar la velocidad base y de giro con la cruceta del mando
             
        (x,y) = mando.get_hat(0)
        if x == 0 and y==0:
            crucetaSuelta = True

        if (x != 0 or y != 0):
            if crucetaSuelta:
                controlRobot.incrementarVelocidades(y,x)
                print("Velocidad base:", controlRobot.getVelocidadBase(),"Modificador velocidad: ", controlRobot.getModificadorVelocidad())
            crucetaSuelta = False
        if not variablesGlobales.parado:

            acciones = agente.act(states= estados)
            estadoAnt= estados
            estados, terminal, recompensa = entorno.execute(actions = acciones)

            #print(estados)

            evaluadorRobot.almacenarPaso(controlRobot.getTime(),estadoAnt, acciones, terminal, recompensa)

            agente.observe(terminal = terminal, reward = recompensa)
            

        if terminal: 
            estados = entorno.reset()
            terminal = False

        if controlRobot.getVuelta() >= NUM_VUELTAS:
            done = True




def seleccionarApiControl():

    if apiSt == 'apiWebots':
        from lib.apiWebots import ApiWebots
        return ApiWebots()
    elif apiSt == 'apiAuriga':
        from lib.apiAuriga import ApiAuriga
        return ApiAuriga()

    from lib.apiControl import ApiControlRobot
    return ApiControlRobot() # Por defecto devolvemos una api que no hace nada



if __name__ == '__main__':
    try:

        parseArgs()
        
        pygame.init()
        #screen = pygame.display.set_mode((400,400))

        # Cogemos el reloj de pygame 
        reloj = pygame.time.Clock()

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

        hiloProcesadoLineas = ProcesadoImagenBin(controlRobot,controlRobot.getResolucionCam())
        hiloProcesadoLineas.start()
        #hiloControl = HiloControl(hiloQLearning, controlRobot, hiloLineas)

        entorno = EntornoLineas(controlRobot,hiloProcesadoLineas)

        
        if rutaAgente is None:
            print("Creando un agente nuevo")
            agente = Agent.create(agent= agenteDefecto, environment= entorno)
        else:
            print("Cargando agente ", nombreAgente,' de ', rutaAgente)
            agente = Agent.load(directory = rutaAgente, filename= nombreAgente)

        main(entorno, agente)

    finally:

        print('Finalizando la ejecución')

        if guardarAgente:
            print(agente.save(directory="tmp", filename="tensorforce"))

        if guardarEvaluacion:
            evaluadorRobot.guardarEpisodio(rutaEvaluacion)

        entorno.close()
        agente.close()

        hiloProcesadoLineas.stop()
        controlRobot.terminarRobot()
