from time import sleep
from tensorforce.environments import Environment

import numpy as np
from lib.singleton import SingletonVariables
import lib.apiControl

class EntornoLineas(Environment):

    def __init__(self, controladorRobot):
        super().__init__()

        self.controlRobot = controladorRobot

        self.variablesGlobales = SingletonVariables()

        self.dictEstados = self.controlRobot.getDictEstados() #Obtener la definición de los estados del hilo de procesado
        print(self.dictEstados)
        self.acciones = dict(type = 'int', num_values=5) #Definir las acciones posibles

        self.primeraVez = True

    def states(self):
        #dict(type='float', shape=(8,))
        return self.dictEstados

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

        
        #self.controlRobot.setAccion(5)
        
        self.controlRobot.reset()
        
        next_state, viendoLinea = self.controlRobot.getEstado()
        
        return next_state

    def execute(self, actions):
        
        terminal = False
        #print(actions)
        self.controlRobot.setAccion(actions)

        #Actualizamos el robot
        self.controlRobot.update()
        
        #Obtenemos el estado actual
        #next_state = self.hiloProcesado.getEstadoAct()
        next_state, viendoLinea = self.controlRobot.getEstado()
        #print(viendoLinea)
        #Establecer recompensas
        if (self.controlRobot.getSensorLinea())or self.variablesGlobales.parado:
            #Si se ha salido de la línea, es un estado terminal
            #print("PenalizacionSalida")
            reward = -20
            terminal = True  
        elif not viendoLinea:
            #Penalizar si no se puede ver la linea
            #print("PenalizacionNoVer")
            reward = -10
        else:
            #Recompensa por seguir la linea normal
            reward = 0.5
        
        return next_state, terminal, reward
