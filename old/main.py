
#from picamera import PiCamera

from time import sleep
from lib.aurigapy.aurigapy import *
from time import *
from time import gmtime, strftime

import pygame
from pygame.locals import *

from lib.estados import *
from lib.qLearning import TablaQ

from lib.hiloCamara import HiloCamara
from lib.hiloLineas import HiloLineas
from lib.hiloSensores import HiloSensores

def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

## pygame: keys
pygame.init()
screen = pygame.display.set_mode((400,400))

# Cogemos el reloj de pygame
reloj = pygame.time.Clock()

###  robot
ap = AurigaPy(debug=False)

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/ttyUSB0"

resolucionCam = (80, 64)

cam = HiloCamara(resolucionCam).start()

print("%r Conectando..." % timestamp())
ap.connect(usb)
print("%r Conectado!" % timestamp())

lineas = HiloLineas(cam, resolucionCam).start()

#sensores = HiloSensores(ap).start()


joystickEnabled = False
mando = None
pygame.joystick.init()
if pygame.joystick.get_count()>0:
    mando = pygame.joystick.Joystick(0)
    mando.init()
    joystickEnabled = True
    print("mandoActivado")


horiz = 0
vert = 0
done = False

rA = 0.7 #Ratio de aprendizaje
gamma = 0.82
randomProb = 1.0

#estado = ControlManual(ap)

tablaQ = TablaQ(lineas.getNumEstados(),5,rA,gamma)

angulo, estadoCam = lineas.read()

estado = AprendizajeAutomaticoTablaQ(ap,tablaQ,randomProb,estadoCam,1000, mando)
try:
    print(tablaQ.tablaQ)
    print(ap.get_line_sensor(6))
    print(ap.get_line_sensor(7))

    while not done:
        reloj.tick(30)
        
        
        eventos = pygame.event.get()

        angulo, estadoCam = lineas.read()
        #print(reloj.get_fps())
        
        sensoriz = ap.get_line_sensor(6)
        sensorder = ap.get_line_sensor(7)
        if sensoriz == None or sensorder == None:
            sensores = (3,3)
        else:
            sensores = (int(sensoriz),int(sensorder))

        estado.update(eventos,estadoCam, sensores)

        for event in eventos:
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                #Cambios de modo
                '''
                if event.key == pygame.K_1 and not isinstance(estado, ControlManual):
                    #Modo de control manual
                    estado.onEnd()
                    estado = ControlManual(ap)

                elif event.key == pygame.K_2 and not isinstance(estado, QLearningManual):
                    #Modo aprendizaje por refuerzo pulsando M o N para seleccionar la recompensa
                    estado.onEnd()
                    estado = QLearningManual(ap,tablaQ,randomProb,estadoCam,2000)
                
                elif event.key == pygame.K_3 and not isinstance(estado, AprendizajeAutomaticoTablaQ):
                    #Modo control automatico usando la tabla Q
                    estado.onEnd()
                    estado = AprendizajeAutomaticoTablaQ(ap,tablaQ,randomProb,estadoCam,1000, mando)
'''
                if event.key == pygame.K_p:
                    #Print tablaQ
                    print(tablaQ.tablaQ)
                    #print(sensores.read())
                    #print(reloj.get_fps())
                elif event.key == pygame.K_o:
                    lineas.printUltimaFotog()
                    
                #Control general
                if event.key == pygame.K_ESCAPE: 
                    #Salir del programa pulsando ESC
                    done = True

finally:
    
    
    lineas.stop()
    cam.stop()


    print("Stoppping robot ...")
    ap.set_speed(speed_left = 0, speed_right = 0)
    print("Closing...")

    ap.reset_robot()
    print("Reset robot...")
    ap.close()
    print("Closed robot...")


