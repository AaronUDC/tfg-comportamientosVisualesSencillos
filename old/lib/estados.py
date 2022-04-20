
import pygame
import random
from lib.aurigapy.aurigapy import *
import time

import lib.acciones as acciones

class Estado():
    
    def __init__(self, auriga, color):
        self.auriga = auriga
        self.color = color

        self.onStart()

    def onStart(self):
        (r,g,b) = self.color
        self.auriga.set_led_onboard(0,r,g,b)
        self.auriga.play_sound()
    
    def onEnd(self):
        return

    def update(self,eventos,estadoCam,sensores):
        return

class ControlManual(Estado):

    def __init__(self, auriga):
        #Estado Rojo
        Estado.__init__(self,auriga, (255,0,0))
        self.vert = 0
        self.horiz = 0

    
    def onEnd(self):
        acciones.pararRobot(self.auriga)

    def update(self, eventos, estadoCam,sensores):
        ##Controlar esto como con movimiento WASD
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.vert = 1
                if event.key == pygame.K_s:
                    self.vert = -1
                if event.key == pygame.K_a:
                    self.horiz = -1
                if event.key == pygame.K_d:
                    self.horiz = 1       

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.vert = 0
                if event.key == pygame.K_s:
                    self.vert = 0
                if event.key == pygame.K_a:
                    self.horiz = 0
                if event.key == pygame.K_d:
                    self.horiz = 0  
        
        acciones.ejecutarAccion(self.auriga,(self.horiz,self.vert))


class QLearningManual(Estado):
    
    def __init__(self, auriga, tablaQ, randomProb, estadoCam,numRandomActions):

        Estado.__init__(self,auriga,(0,0,255))

        self.tablaQ = tablaQ
        self.randomProb = randomProb
        self.estadoAnterior = estadoCam
        self.numRandomActions = numRandomActions
        self.ultimaDireccion = (0,0)
        self.ultimoCiclo= time.time()
        self.tiempoEsperaRecompensa = 0.5
        
        self.esperandoRecompensa = False
        self.tablaActualizada = False
        self._actualizarTabla(estadoCam,1)


    def _actualizarTabla(self,estadoCam, recompensa):
        
        #Actualizar el qvalor y escoger una accion
        
        #Seleccionamos la mejor accion o una aleatoria con una probabilidad determinada.
        if random.random() < self.randomProb: 
            accion = random.randint(0,4)
        else:
            accion = self.tablaQ.getMejorAccion(self.estadoAnterior)
        
        #Ejecutar una accion
        self.ultimaDireccion = acciones.accionADireccion(accion)
        
        acciones.ejecutarAccion(self.auriga,self.ultimaDireccion)
        
        #Actualizamos los pesos de la tabla Q
        self.tablaQ.actualizarQValor(self.estadoAnterior, accion, recompensa, estadoCam) 

        self.estadoAnterior = estadoCam
        #Actualizamos la probabilidad de seleccionar una accion aleatoria
        self.randomProb = self.randomProb - 1.0/self.numRandomActions
        self.randomProb = max(min(self.randomProb, 1.0), 0.0)
        

    def update(self,eventos, estadoCam,sensores):

    
        if self.esperandoRecompensa:
            for event in eventos:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n: #Pulsando N en el teclado penalizamos la ultima accion
                        #Parte para deshacer la ultima accion
                        print(self.ultimaDireccion, (self.ultimaDireccion[0]*-1,self.ultimaDireccion[1]*-1))
                        acciones.ejecutarAccion(self.auriga, (self.ultimaDireccion[0]*-1,self.ultimaDireccion[1]*-1))
                        time.sleep(self.tiempoEsperaRecompensa*2)
                        
                        self._actualizarTabla(estadoCam,-10)
                        self.esperandoRecompensa = False
                        self.ultimoCiclo = time.time()
                    elif event.key == pygame.K_m: #Pulsando M en el teclado premiamos la ultima accion
                        self._actualizarTabla(estadoCam,1)
                        self.esperandoRecompensa = False
                        self.ultimoCiclo = time.time()
        else:
            #Esperamos un pequeño lapso de tiempo para que se realice una accion
            if time.time() - self.ultimoCiclo > self.tiempoEsperaRecompensa:
                self.esperandoRecompensa = True 
                acciones.pararRobot(self.auriga)
            
    def onEnd(self):
        acciones.pararRobot(self.auriga)
class AprendizajeAutomaticoTablaQ(Estado):
    
    def __init__(self, auriga, tablaQ, randomProb, estadoCam,numRandomActions, mando):
        Estado.__init__(self,auriga,(0,0,0))

        self.tablaQ = tablaQ
        self.randomProb = randomProb
        self.estadoAnterior = estadoCam
        self.numRandomActions = numRandomActions
        self.ultimaDireccion = (0,0)
        self.quieto = False
        self.recompensado = False
        self.mando = mando
        #self.buffAcciones = []
        #self.tamBuffAcciones = 10
        
    def _comprobarSensoresLinea(self,sensores):
        #print(ap)
        return sensores[0] != 0 or sensores[1] != 0 
    
    
    def update(self,eventos, estadoCam,sensores):
       
        if self._comprobarSensoresLinea(sensores) or self.mando.get_button(1):
            self.quieto = True
        else:
            recompensa = 1
            self.recompensado = False
        if self.quieto:
            acciones.ejecutarAccion(self.auriga, (0,0))
            
            '''for event in eventos:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.quieto = False
                        recompensa = -10
                        print(self.randomProb)
                        self.recompensado = False
               '''         
            if self.mando.get_button(0):
                self.quieto = False
                recompensa = -10
                print(self.randomProb)
                self.recompensado = False
            
        
        if not self.recompensado and not self.quieto:
            accion = self.tablaQ.getMejorAccion(estadoCam) #Obtenemos la mejor accion segun el estado actual
            
            if random.random() < self.randomProb: 
                accion = random.randint(0,4)
            else:
                accion = self.tablaQ.getMejorAccion(self.estadoAnterior)
                
            
            
            #Ejecutar una accion
            self.ultimaDireccion = acciones.accionADireccion(accion)
            
            acciones.ejecutarAccion(self.auriga,self.ultimaDireccion)
            
            #Actualizamos los pesos de la tabla Q
            self.tablaQ.actualizarQValor(self.estadoAnterior, accion, recompensa, estadoCam) 

            self.estadoAnterior = estadoCam
            #Actualizamos la probabilidad de seleccionar una accion aleatoria
            self.randomProb = self.randomProb - 1.0/self.numRandomActions
            self.randomProb = max(min(self.randomProb, 1.0), 0.0)
            
            self.recompensado = True
        
        
    
    def onEnd(self):
        acciones.pararRobot(self.auriga)
   
class ControlAutomaticoTablaQ(Estado):
    
    def __init__(self, auriga, tablaQ):
        Estado.__init__(self,auriga,(0,255,0))

        self.tablaQ = tablaQ
        
    
    def update(self,eventos, estadoCam):

        accion = self.tablaQ.getMejorAccion(estadoCam) #Obtenemos la mejor accion segun el estado actual
        
        
        
    
    def onEnd(self):
        acciones.pararRobot(self.auriga)
    
