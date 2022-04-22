
class ApiControlRobot():

    def __init__(self):
        #Inicializar el robot
        self.hiloControl = None
    
    def update(self):
        #Actualizar los sistemas del robot
        pass

    def getSensorLinea(self):
        #Obtener si los sensores de linea han detectado la linea
        pass

    def getDatosCamara(self):
        #Obtener la ultima imagen capturada por la camara
        pass
    
    def getResolucionCam(self):
        pass

    def setHiloControl(self, hiloControl):
        self.hiloControl = hiloControl

    def setMotores(self, izqu, der):
        #Aplicar una velocidad a cada motor
        pass
    
    def ejecutarAccion(self, accion):
        #Ejecutar una acción
        pass

    def terminarRobot(self):
        #Finalizar los sistemas del robot.
        pass

    #Metodos que solo tienen uso en webots para reiniciar la simulacion
    def reset(self):
        pass

    def waypoint (self):    
        pass
    