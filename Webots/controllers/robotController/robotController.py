

#from lib.apiWebots import ApiWebots
#from lib.apiControl import ApiControlRobot

from lib.hiloLineas2 import HiloLineas2
from lib.hiloLineas import HiloLineas

from lib.hiloQLearning import HiloQLearning
from lib.hiloControl import HiloControl
from lib.singleton import SingletonVariables

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


done = False

parado = False

mando = None

joystickEnabled = False

controlRobot = None

resolucionCam = None

rA = 0.7 #Ratio de aprendizaje
gamma = 0.80

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


#Ruta a la tablaQ
path = None
guardarTabla = False

apiSt = 'apiControl'

# Inicializamos una opcion de NumPy para mostrar datos en punto flotante
# con 3 digitos decimales de precision al imprimir un array
np.set_printoptions(precision=3)

def parseArgs():
    #Parsear argumentos 
    global path, guardarTabla, apiSt


    config = configparser.ConfigParser()
    config.read('config.ini')

    if config['DEFAULT']['archivoLectura'] != '':
        path = config['DEFAULT']['archivoLectura']

    guardarTabla = config['DEFAULT'].getboolean('guardarTabla')


    #print(path)
    

    apiSt = config['DEFAULT']['API']

    parser = argparse.ArgumentParser(description= "Seguimiento de lineas mediante aprendizaje por refuerzo")

    parser.add_argument('--path', help='Ruta del archivo que contiene la tablaQ', nargs='?', type=argparse.FileType('r') ,dest='path')
    parser.add_argument('-s', action='store_true', help='Guardar la tabla Q al terminar la ejecución', dest='guardarTabla')

    args = parser.parse_args()

    if args.path is not None and args.path != '':
        path = args.path

    if args.guardarTabla:
        guardarTabla = args.guardarTabla
    #print(args, path, guardarTabla)



def cambiarCapturaFotos():
    global variablesGlobales

    if variablesGlobales.guardarFotos:
        variablesGlobales.guardarFotos = False
        print("Se ha parado la captura de fotos")
    else:
        variablesGlobales.guardarFotos = True
        print("Captura de fotos iniciada")

def seleccionarApiControl():

    if apiSt == 'apiWebots':
        from lib.apiWebots import ApiWebots
        return ApiWebots()
    elif apiSt == 'apiAuriga':
        from lib.apiAuriga import ApiAuriga
        return ApiAuriga()

    from lib.apiControl import ApiControlRobot
    return ApiControlRobot() # Por defecto devolvemos una api que no hace nada

def main():
    global done, parado, variablesGlobales

    while not done:
        t0 = time.time()
        controlRobot.update()

        #print(sensorDer,sensorIz)
        if controlRobot.getSensorLinea():
            hiloControl.pararRobot()
            
        t1=time.time()
        
        #Gestion de los eventos para controlar el robot
        
        
        hiloControl.update()
        t2=time.time()
        
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
                    hiloLineas.printUltimaFotog()
                elif event.key == pygame.K_p:
                    #Hacer un print de la tabla Q
                    print("Tabla Q")
                    print(hiloQLearning.tablaQ)
                    
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0: #Btn A
                    #Volver a permitir el movimiento
                    if variablesGlobales.parado:
                        hiloControl.reanudarRobot()
                elif event.button == 1: #Btn B
                    #Parada de emergencia
                    if not variablesGlobales.parado:
                        hiloControl.pararRobot()
                elif event.button == 2:# Btn X
                    #Guardar el ultimo frame
                    print("Se ha almacenado la imagen")
                    hiloLineas.printUltimaFotog()
                elif event.button == 3: # Btn Y
                    #Hacer un print de la tabla Q
                    print("Tabla Q")
                    print(hiloQLearning.tablaQ)

                elif event.button == 6:	#Btn BACK
                    done = True

                elif event.button == 4: #Btn LB
                    cambiarCapturaFotos()
                elif event.button == 5: 
                    time1=round((t1-t0)*1000)
                    time2=round((t2 - t1) * 1000)
                    time3=round((time.time() - t2) * 1000)
                    
                    print('Tiempo para obtener sensor:', time1)
                    print('Tiempo update control:', time2)
                    print('Tiempo eventos:', time3)
                    print('Total', time1 + time2 + time3)
                    



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

        hiloLineas = HiloLineas2(controlRobot, resolucionCam).start()

        hiloQLearning = HiloQLearning(hiloLineas.getNumEstados(),5,hiloLineas,rA,gamma) 
        hiloControl = HiloControl(hiloQLearning, controlRobot, hiloLineas)

        variablesGlobales.control.setHiloControl(hiloControl)

        hiloQLearning.setHiloControl(hiloControl)

        #Cargar la tabla si se ha especificado una
        if path != None:
            
            hiloQLearning.cargarTablaQ(path)

        hiloQLearning.start()
        #hiloControl.start()

        main()

    finally:
        print('Finalizando la ejecución')
        hiloLineas.stop()
        hiloQLearning.stop()
        #hiloControl.stop()

        if guardarTabla:
            hiloQLearning.guardarTablaQ()

        controlRobot.terminarRobot()
