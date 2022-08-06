
class ApiControlRobot():

    def __init__(self):
        #Inicializar el robot
        self.vuelta = 0
        self.parado = True
    
    def update(self):
        #Actualizar los sistemas del robot
        pass
    
    def parada(self):
        pass

    def reanudar(self):
        pass

    def getEstado(self):
        pass

    def getTime(self):
        pass

    def getVuelta(self):
        return self.vuelta

    def setVuelta(self, vuelta):
        self.vuelta = vuelta

    def incrementarVuelta(self, incremento):
        self.vuelta += incremento
        
    def getSensorLinea(self):
        #Obtener si los sensores de linea han detectado la linea
        pass

    def getDatosCamara(self):
        #Obtener la ultima imagen capturada por la camara
        pass
    
    def getResolucionCam(self):
        pass


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

    def pushWaypoint (self):    
        pass
    