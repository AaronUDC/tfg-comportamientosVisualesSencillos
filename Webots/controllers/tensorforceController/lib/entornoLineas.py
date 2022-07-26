from time import sleep
from tensorforce.environments import Environment

import numpy as np
from lib.singleton import SingletonVariables
import lib.apiControl

class EntornoLineas(Environment):

    def __init__(self, controladorRobot):
        super().__init__()

        self.controladorRobot = controladorRobot

        self.variablesGlobales = SingletonVariables()

        self.estados = self.controladorRobot.getDictEstados() #Obtener la definición de los estados del hilo de procesado
        self.acciones = dict(type = 'int', num_values=5) #Definir las acciones posibles

        self.primeraVez = True

    def states(self):
        #dict(type='float', shape=(8,))
        return self.estados

    def actions(self):
        #dict(type='int', num_values=4)
        return self.acciones

    # Optional: should only be defined if environment has a natural fixed
    # maximum episode length; otherwise specify maximum number of training
    # timesteps via Environment.create(..., max_episode_timesteps=???)
    def max_episode_timesteps(self):
        return super().max_episode_timesteps()

    # Optional additional steps to close environment
    def close(self):
        


        super().close()

    def reset(self):

        if self.variablesGlobales.parado:
            #print("se ha detenido el robot")
            self.controladorRobot.ejecutarAccion(5)

        sleep(0.05)
        #self.reanudarRobot()
        self.controladorRobot.reset()
        next_state, viendoLinea, lastImg = self.controladorRobot.getEstado()
        return next_state

    def execute(self, actions):
        
        terminal = False
        #print("execute")
        self.controladorRobot.ejecutarAccion(actions)
        '''if not self.variablesGlobales.parado:
            # Ejecutamos una acción
            
        else:
            self.primeraVez = False'''
        #Actualizamos el robot
        self.controladorRobot.update()
        
        #Obtenemos el estado actual
        #next_state = self.hiloProcesado.getEstadoAct()
        next_state, viendoLinea, lastImg = self.controladorRobot.getEstado()
        
        #Establecer recompensas
        if (self.controladorRobot.getSensorLinea())or self.variablesGlobales.parado:
            #Si se ha salido de la línea, es un estado terminal
            reward = -20
            terminal = True  
        elif not viendoLinea:
            #Penalizar si no se puede ver la linea
            reward = -10
        else:
            #Recompensa por seguir la linea normal
            reward = 0.5
        
        return next_state, terminal, reward
