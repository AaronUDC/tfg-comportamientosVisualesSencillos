

class Evaluador:

    def __init__(self, nombreAgente):
        self.nombreAgente = nombreAgente
        self.episodio_tiempo = list()
        self.episodio_estados = list()
        self.episodio_acciones = list()
        self.episodio_terminales = list()
        self.episodio_refuerzos = list()



    def almacenarPaso(self,tiempo ,estado, acciones, terminal, refuerzo):

        self.episodio_tiempo.append(tiempo)
        self.episodio_estados.append(estado)
        self.episodio_acciones.append(acciones)
        self.episodio_terminales.append(terminal)
        self.episodio_refuerzos.append(refuerzo)

    def getRecompensaAcumuladaDescontada(self, gamma = 1):
        #Con un gamma de 1, no hay descuento.
        suma= 0.0

        for i, refuerzo in enumerate(self.episodio_refuerzos, start = 1):
            suma += (gamma**i) * refuerzo
        
        return suma

    def getNumEstadosTerminales(self):
        #Contarmos las veces que tenemos un true en la lista.
        return  sum(self.episodio_terminales)
    
    def getNumRefuerzosNegativos(self):
        #Contar las veces que se da un refuerzo inferior a 0
        #print(self.episodio_refuerzos)
        return sum(refuerzo > 0 for refuerzo in self.episodio_refuerzos) 


    def guardarEnDisco(self, ruta):
        #TODO: Funcion que almacena los datos en un archivo en el disco (Pensar el formato del archivo)

        pass
        
        
        