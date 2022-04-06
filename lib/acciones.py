from lib.aurigapy.aurigapy import *
import time
#Controles de la auriga
def moverFrente(auriga):
    auriga.set_speed(-80, 80)

def moverIzq(auriga):
    auriga.set_speed(-100, 40)

def moverDer(auriga):
    auriga.set_speed(-40, 100)

def girarIzq(auriga):
    auriga.set_speed(-90, -30)

def girarDer(auriga):
    auriga.set_speed(30, 90)

def retroceder(auriga):
    auriga.set_speed(80, -80)
    
def pararRobot(auriga):
    auriga.set_speed(0, 0)


def accionADireccion(accion):
    if accion == 0:
        return (0,1)
    elif accion == 1:
        return (1,1)
    elif accion == 2:
        return (-1,1)
    elif accion == 3:
        return (1,0)
    elif accion == 4:
        return (-1,0)

def ejecutarAccion(auriga, direccion, inversa = False):
    (horiz,vert) = direccion
    mod = 1
    if inversa:
        mod = -1
    
    if vert == 0 and horiz == 0:
        auriga.set_speed(0, 0) #Parar
        
    elif vert == 1 and horiz == 0:
        auriga.set_speed(-50 * mod, 50 * mod) #Avanzar

    elif vert == 1 and horiz == 1:
        auriga.set_speed(-20 * mod, 80 * mod) #Avanzar girando a la derecha

    elif vert == 1 and horiz == -1:
        auriga.set_speed(-80 * mod, 20 * mod) #Avanzar girando a la izquierda

    elif vert == 0 and horiz == 1:
        auriga.set_speed(-10 * mod, 80 * mod) #Girar a la derecha

    elif vert == 0 and horiz == -1:
        auriga.set_speed(-80 * mod, 10 * mod) #Girar a la izquierda
        
    elif vert == -1 and horiz == 0:
        auriga.set_speed(50 * mod, -50 * mod) #Retroceder
        
    elif vert == -1 and horiz == 1:
        auriga.set_speed(20 * mod, -80 * mod) #Retroceder girando a la derecha
    
    elif vert == -1 and horiz == -1:
        auriga.set_speed(80 * mod, -20 * mod) #Retroceder girando a la izquierda
    
