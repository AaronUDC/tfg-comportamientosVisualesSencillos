


from threading import Thread


class HiloProcesadoImg():

    def __init__(self,apiControl, dimensiones):

        self.apiControl = apiControl
        self.dimensiones = dimensiones

        self.stopped = False

    def start(self):
            # start the thread to read frames from the video stream
            Thread(target=self.update, args=()).start()
            return self

    def processImage(self, image):
        pass

    def update(self):
        while not self.stopped:
            img = self.apiControl.getDatosCamara()

            self.processImage(img)

    def getNumEstados(self):
        return None
    
    def getDictEstados(self):
        return None

    def printUltimaFotog(self):
        pass

    def read(self):

        return None,None,None

    def getEstado(self,image):
        return None
        
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True