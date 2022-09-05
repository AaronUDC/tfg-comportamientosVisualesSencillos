
class ApiControlRobot():

    def __init__(self, velocBase, modificadorVeloc):
        #Inicializar el robot
        self.vuelta = 0
        self.parado = True

        
        self.velocBase = velocBase
        self.modificadorVeloc = modificadorVeloc

    
    def update(self):
        #Actualizar los sistemas del robot
        pass
    
    def parada(self):
        pass

    def reanudar(self):
        pass


    def getTime(self):
        pass

    def getVuelta(self):
        return self.vuelta

    def setVuelta(self, vuelta):
        self.vuelta = vuelta

    def incrementarVuelta(self, incremento):
        self.vuelta += incremento
        
    def setVelocidadBase(self, velocBase):
        self.velocBase = velocBase

    def setModificadorVelocidad(self, modificadorVeloc):
        self.modificadorVeloc = modificadorVeloc

    def incrementarVelocidades(self,incrementoBase, incrementoModif ):
        self.velocBase += incrementoBase
        self.modificadorVeloc += incrementoModif

    def getVelocidadBase(self):
        return self.velocBase

    def getModificadorVelocidad(self):
        return self.modificadorVeloc

    def getSensorLinea(self):
        #Obtener si los sensores de linea han detectado la linea
        pass

    def getImgCamara(self):
        #Obtener la ultima imagen capturada por la camara
        pass
    
    def getResolucionCam(self):
        pass

    def getDictEstados(self):
        pass

    def getEstado(self):
        pass
    
    def setAccion(self, accion):
        if not self.parado: #Si esta parado, no admitimos nuevas ordenes
            self.seleccionarAccion(accion)

    def setMotores(self, izqu, der):
        #Aplicar una velocidad a cada motor
        pass
    
    def seleccionarAccion(self, accion):
        #Ejecutar una acción
        pass

    def terminarRobot(self):
        #Finalizar los sistemas del robot.
        pass

    def reset(self):
        #Colocar el robot de nuevo en la línea
        pass

    