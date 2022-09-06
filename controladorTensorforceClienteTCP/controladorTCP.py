
import numpy as np
import socket
import socketserver
import pygame
import time
import math
import threading

from camaraPreprocesado import CamaraPreprocesado
from aurigapy.aurigapy import AurigaPy
from evaluacionServer import EvaluacionServer

IP_PC, PORT_PC = "192.168.1.44", 9999
IP_ROBOT, PORT_ROBOT = "", 9998
PORT_MANDO = 9997

TIME_STEP = 15

VEL_BASE = 45*3

RESOLUCION_RESIZ = (10,8)

accionActual = 5

GUARDAR_LOGS = True

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/ttyUSB0"

done = False

##SERVER RECEPCIÓN MANDO

class UDPHandlerMando(socketserver.BaseRequestHandler):

	def handle(self):
		global accionActual
		data = self.request[0]
		accion = np.frombuffer(data, dtype= np.uint8)
		if accion[0] == 1: #Orden de parada
			self.server.parada = True
			self.server.reset = True
			accionActual = 5
		else: # Orden de reanudar la marcha
			self.server.parada = False
			self.server.reset = True
        
class ServerMando(socketserver.ThreadingUDPServer,socketserver.UDPServer):
	def __init__(self, server_address, RequestHandlerClass):
		super().__init__(server_address, RequestHandlerClass)
		
		self.parada = False
		self.reset = False


### ACTUADORES

def onReading(value, timeout):
    
    print("%r > %r (%r)" % (funcionInexistente, value, timeout))
    
def hiloAuriga():
	relojMotores = pygame.time.Clock()
	while not done:
		relojMotores.tick(TIME_STEP+5)
		
		ejecutarAccion(accionActual)

def setMotores(izqu, der):
	auriga.set_speed(izqu,der, callback= onReading)

def ejecutarAccion(accion):
	velAng = 0
	
	if accion == 0:
		velAng = 15 #Girar fuerte a la izquierda
	
	elif accion == 1:
		velAng = 12 #Girar a la izquierda
	
	elif accion == 2:
		velAng = 0 #Avanzar

	elif accion == 3:
		velAng = -12 #Girar a la derecha
	
	elif accion == 4:
		velAng = -15 #Girar fuerte a la derecha
	
	elif accion == 5:
		setMotores(0,0) 
		return
		
	#print(velAng)
	l = (VEL_BASE - (14.5/2) * velAng)/ 3 # (VelBase - (distanciaRuedas/2) * velAng) / radioRuedas 
	r = (VEL_BASE + (14.5/2) * velAng)/ 3 # (VelBase + (distanciaRuedas/2) * velAng) / radioRuedas 
	
	setMotores(-l,r)
	
	
def setAccion(accion):
	# Actualizar accion solo si no se encuentra parado
	global accionActual
	if not serverMando.parada: 
		accionActual = accion


### TIMESTAMPS Y CONVERSION A BYTES

def timestampMilis():
	#Obtener la fecha y hora actual en milisegundos
	milis = math.floor(time.process_time() * 1000)
	return int(milis)

def millisToBytes(millis):
	#Convertir un int representando los milisegundos desde Epoch a una cadena de 8 bytes.
	return millis.to_bytes(8,byteorder="big")

def bytesToMillis(millisBytes):
	#Convertir una cadena de bytes a un int
	return int.from_bytes(millisBytes, byteorder = "big")
	
### COMUNICACIÓN CON EL SERVIDOR

def enviarFoto(imgProcesada):
	
	imgBytes = imgProcesada.tobytes()
	
	#Juntar los datos de la imagen y el timestamp actual en un paquete de bytes
	dataBytes = bytearray(imgBytes)
	
	millisEnvio = timestampMilis()
	millisEnvioBytes = bytearray(millisToBytes(millisEnvio))
	
	dataBytes.extend(millisEnvioBytes)
	#Enviar los datos al servidor del PC
	print("Enviando",millisEnvio)
	socketAprendizaje.send(dataBytes)
	
	return millisEnvio,imgBytes
	
	
def recibirAccion():
	#Esperar por la respuesta del servidor
	
	data = socketAprendizaje.recv(17)
	
	#print("recibido",time.process_time())
	#print(data)
	
	#Descodificar la información
	millisRecepcion = timestampMilis()	#Timestamp de recepción

	millisEnvio = bytesToMillis(data[-16:-8]) #Timestamp del envío original
	
	tiempoServidor = bytesToMillis(data[-8:]) #Tiempo de procesado en el servidor
	
	accion = np.frombuffer(data[:-16], dtype= np.uint8) #Descodificar accion a realizar
	
	return millisEnvio, millisRecepcion, tiempoServidor, accion[0]

#Inicializar pygame para usar el reloj
pygame.init()
reloj = pygame.time.Clock()

#Inicializar AurigaPy		
auriga = AurigaPy(debug=False)
print(" Conectando..." )
auriga.connect(usb)
print(" Conectado!" )


#Inicializar hilo de la camara
camara = CamaraPreprocesado(resolution = (80,64),outResolution = RESOLUCION_RESIZ, framerate = TIME_STEP+5).start()

time.sleep(1.5)

#Inicializar logs
logs = EvaluacionServer()

#Inicializar socket TCP para conectarse al PC
socketAprendizaje = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketAprendizaje.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
socketAprendizaje.setsockopt(socket.IPPROTO_TCP, socket.SO_PRIORITY, 6)


print("Iniciando servidor del mando")
#Thread del server que recoge inputs del mando en el PC.
serverMando = ServerMando((IP_ROBOT,PORT_MANDO), UDPHandlerMando)
serverMando.daemon_threads = True
        
threadServerMando = threading.Thread(target = serverMando.serve_forever)
threadServerMando.setDaemon(True)

#Thread de los motores
threadMotoresAuriga = threading.Thread( target = hiloAuriga)

try:
	#Iniciar los threads
	threadServerMando.start()
	threadMotoresAuriga.start()
	
	print("Conectando con el servidor")
	socketAprendizaje.connect((IP_PC, PORT_PC))
	
	print("¡Conectado! Iniciando Loop")
	while not done:
		reloj.tick(TIME_STEP)
		if serverMando.parada == False:
			serverMando.reset = False
			
			img, imgProcesada = camara.read()
	
			if img is None: 
				continue

			millisEnvio, imgBytes = enviarFoto(imgProcesada) #Capturar, preprocesar y enviar la foto
			
			#Guardar el envio en el log
			logs.almacenarEnvio(millisEnvio,imgBytes)

			try:

				#Esperar por la respuesta del servidor
				millisEnvio, millisRecepcion, tiempoServidor, accion  = recibirAccion()
				
				logs.almacenarPaso(millisEnvio,millisRecepcion,
					tiempoServidor,imgBytes,accion) #Almacenar la recepcion en el log
					
				print(accion)
	
				if serverMando.parada == False:
					#Actualizar la acción si no se ha ordenado parada.
					setAccion(accion)
					
				
			except:
				#En caso de Timeout del servidor u otro error
				print("Error")
				setAccion(5)
				serverMando.parada = True
				done = True
		else:
			#En el caso de haber orden de parada nos ponemos a la espera
			
			#print("Esperando")
			# En el primer ciclo de espera, 
			# enviar una imagen y quedarse esperando el resto de ciclos
			if serverMando.reset == True:

				img, imgProcesada = camara.read()
				if img is None: 
					continue
				
				enviarFoto()
				serverMando.reset = False

			setAccion(5) #Parar

finally:
	accionActual = 5
		
	done = True
	
	try:
		threadMotoresAuriga.join()
		
		if GUARDAR_LOGS:
			logs.guardarLog()
	finally:
		
		#Terminar sistemas
		
		print("Cerrando")
		camara.stop()
	
		#auriga.reset_robot()
		auriga.close()
	
		#threadServerMando.join(1)
		#server.shutdown()
