

from threading import Thread
from tensorforce import Agent
from lib.evaluacion import Evaluador
from lib.entornoLineas import EntornoLineas
from lib.singleton import SingletonVariables
from lib.procesadoLineas.procesadoServer import ProcesadoServer
from lib.apiServerTCP import ApiServerTCP
import lib.apiServerTCP as apiServer

import time
from datetime import datetime
from time import gmtime, strftime
import threading
import socket

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
socketMando = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
    config.read('D:/Documentos/Cole/Carrera/5\TFG/tfg-comportamientosVisualesSencillos/Webots/controllers/tensorforceController/config.ini')

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

def enviarOrdenMando(orden):
    socketMando.sendto(np.array(([orden]), dtype=np.uint8).tobytes(), (controlRobot.dir[0], apiServer.PORT_MANDO))


def procesarRed():
    
    global done, parado, variablesGlobales, evaluadorRobot, entorno, agente, paradaTerminal
    recompensa= 0
    estados = entorno.reset()
    print(estados)
    terminal = False
    variablesGlobales.parado = False
    while not done:
        #print (imagen)
        if not variablesGlobales.parado:
            if paradaTerminal:
                #Si se ordena una parada desde el mando, se actúa acorde.
                print("Parada Terminal")
                paradaTerminal = False
                variablesGlobales.parado = True

            acciones = agente.act(states= estados)
            #acciones= 4
            estadoAnt= estados
            
            estados, terminal, recompensa = entorno.execute(actions = acciones)

            evaluadorRobot.almacenarPaso(controlRobot.getTime(),estadoAnt, acciones, terminal, recompensa)

            agente.observe(terminal = terminal, reward = recompensa)


            #Al ser terminal, terminamos el episodio y reiniciamos el entorno (Volver a la linea/parar)
            if terminal: 
                estados = entorno.reset()
                terminal = False

            #Si damos NUM_VUELTAS, terminamos el robot.
            if controlRobot.getVuelta() >= NUM_VUELTAS:
                done = True
        else:
            print("Esperando")
            time.sleep(0.3)



def main():
    global done, parado, variablesGlobales, evaluadorRobot, paradaTerminal

    while not done:
        
        eventos = pygame.event.get()
        for event in eventos:
            
            if event.type == pygame.QUIT:
                done = True


            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:# Btn X
                    #Guardar el ultimo frame
                    print("Se ha almacenado la imagen")
                    hiloProcesado.printUltimaFotog()
                elif event.button == 0: #Btn A
                    #Volver a permitir el movimiento

                    #Reanudar la ejecucion de la parte del bucle que ejecuta acciones y aprende
                    print("Reanudado")
                    variablesGlobales.parado = False
                    paradaTerminal = False
                      
                    enviarOrdenMando(0) 

                elif event.button == 1: #Btn B
                    #Parada de emergencias
                    #Ordenar la detencion del bucle
                    #hiloControl.pararRobot()
                    print("Parado")
                    
                    paradaTerminal = True  
                    enviarOrdenMando(1)
                elif event.button == 3: # Btn Y
                    #Hacer un print de la tabla Q
                    '''print("Datos del conocimiento")
                    print("Recompensa =", recompensa)
                    print("Estados =", estados)
                    print("Acciones =", acciones
                    print("Arquitectura")
                    print(agente.get_architecture())
                    print("Especificacion")
                    print(agente.get_specification())
                    print("Tensores")
                    print(agente.tracked_tensors())
                    '''
                    print("Parado: ", variablesGlobales.parado)
                    print("Evaluacion")
                    print("Recompensa acumulada descontada gamma=", gamma)
                    print(evaluadorRobot.getRecompensaAcumuladaDescontada(gamma))
                    print("Refuerzoas negativos:", evaluadorRobot.getNumRefuerzosNegativos())
                    print("Estados terminales:", evaluadorRobot.getNumEstadosTerminales())

                elif event.button == 6:	#Btn BACK
                    done = True

       
                
                        

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

        controlRobot = ApiServerTCP()
        hiloProcesado = ProcesadoServer(controlRobot,controlRobot.getResolucionCam())
        controlRobot.hiloProcesado = hiloProcesado
        resolucionCam = controlRobot.getResolucionCam()
        
        evaluadorRobot = Evaluador(nombreAgente)


        entorno = EntornoLineas(controlRobot)

        if rutaAgente is None:
            print("Creando un agente nuevo")
            agente = Agent.create(agent= agenteDefecto, environment= entorno)
        else:
            print("Cargando agente ", nombreAgente,' de ', rutaAgente)
            agente = Agent.load(directory = rutaAgente, filename= nombreAgente)

        threadProcesarRed = threading.Thread(target=procesarRed)
        threadProcesarRed.setDaemon(True)
        threadProcesarRed.start()
        print("Iniciado threadServidor: ", threadProcesarRed.name)

        main()

    except (KeyboardInterrupt):
        guardarAgente = False
        guardarEvaluacion = False

    finally:

        print('Finalizando la ejecución')

        if guardarAgente:
            evaluadorRobot.setAgente(agente)

        if guardarEvaluacion:
            evaluadorRobot.guardarEpisodio(rutaEvaluacion)
        
        if not guardarEvaluacion and guardarAgente:
            print(agente.save(directory="tmp", filename=nombreAgente))

        threadProcesarRed.join(2)
        
        entorno.close()
        agente.close()

        
        hiloProcesado.stop()
        controlRobot.terminarRobot()