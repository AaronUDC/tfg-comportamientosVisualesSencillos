# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
import numpy as np
import time
import math

class HiloLineasCam():
	
	def __init__(self, resolution=(80, 64), framerate=32, angulos = np.array([-30, -10,-3.75, 0, 3.75, 10, 30])):
        # initialize the camera and stream
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.camera.rotation=180
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)
		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = None
		self.stopped = False

		# Inicializar los datos para el procesado de la imagen a un estado
		self.angulos = angulos
		self.indicesAngulos = np.arange(angulos.size)
		self.indicesLado = np.arange(1,4)
		self.dimensiones = resolution
		# Variables para poder guardar la ultima imagen capturada en memoria
		self.lastImg = None
		self.nFoto = 0
		self.angulo = 0 #Angulo calculado
		self.index = 0 #Indice del estado
		
		#Datos para calcular tiempos de procesado
		'''
		self.media = 0
		self.calculos = 0
		self.suma = 0
		'''
		
        
	def start(self):
            # start the thread to read frames from the video stream
            Thread(target=self.update, args=()).start()
            return self
            
	def update(self):
        # keep looping infinitely until the thread is stopped
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame = f.array
			self.rawCapture.truncate(0)
			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				return

			imgs=np.array(self.frame ) #Convertirla en un array de numpy para que sea compatible
			# con las operaciones de openCV
			
			#Analisis del tiempo requerido para el procesado
			#t1 = time.time()
			
			# Agregamos un desenfoque gausiano para minimizar los artefactos pequenos
			imgs = cv2.GaussianBlur(imgs,(5,5),0, borderType = cv2.BORDER_REPLICATE)
			
			#Cambiamos el espacio de color a HSV
			imgHSV = cv2.cvtColor(imgs, cv2.COLOR_RGB2HSV)
			
			(h,s,v) = cv2.split(imgHSV)
			
			mask = cv2.adaptiveThreshold(v, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 41,10)
			widePercent = 0.1

			#Recorte de la zona central inferior de la imagen
			mask = mask[int((self.dimensiones[1])*0.3): int(self.dimensiones[1]-1), int(self.dimensiones[0]*(widePercent/2)):int(self.dimensiones[0]*(1-widePercent/2))]             
			
			#Girar la imagen 90º para simplificar el calculo del angulo
			mask = cv2.rotate(mask, cv2.ROTATE_90_CLOCKWISE)
			
			'''
			canny= cv2.Canny(mask,30,150, None,3)
			lines = cv2.HoughLines(canny, 1 , np.pi / 180, 20,None, 0, 0)

			x1 = 0
			x2 = 0

			y1 = 0
			y2 = mask.shape[1]

			#Calcular la línea media
			if lines is not None:
				for i in range(0, len(lines)):
					rho = lines[i][0][0]
					theta = lines[i][0][1]

					a = math.cos(theta)
					b = math.sin(theta)
					x0 = a * rho
					y0 = b * rho

					pt1 = (int(x0 + 2000*(-b)), int(y0 + 2000*(a)))

					pt1 = (x0 + 1*(-b), y0 + 1*(a))

					pend = (pt1[1]-y0)/(pt1[0]-x0)

					x1 = (((y1-y0)/pend) + x0) + x1
					x2 = (((y2-y0)/pend) + x0) + x2

				x1 = int(x1/len(lines))
				x2 = int(x2/len(lines))
			
			
				'''
			#Invertir la mascara
			mask = 255-mask
			
			mask2 = np.zeros_like(mask)
			
			#Obtener contornos
			cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			
			cnts = cnts[0] if len(cnts) == 2 else cnts[1]
			
			if cnts == None or len(cnts) == 0:
				#Si no se ha detectado nada, se asigna un 
				#estado que se corresponde con el ultimo de la lista
				self.index = self.angulos.size * 3
			else:
				
				mayorArea = 0
				mayorContorno = None
				
				#Obtener el mayor contorno (Que deberia corresponder al camino)
				for c in cnts:
					if mayorArea <= cv2.contourArea(c):
						mayorArea = cv2.contourArea(c)
						mayorContorno = c
				
				cv2.drawContours(mask2, [mayorContorno], 0, (255), cv2.FILLED)
				
				if cv2.contourArea(mayorContorno) < mask.size * 0.1:
					#Si lo que se ha detectado es demasiado pequeño, se asigna un 
					#estado que se corresponde con el ultimo de la lista
					self.index = self.angulos.size * 3
					self.angulo = cv2.contourArea(mayorContorno)
				
				else:
					(rows, cols) = mask.shape
					[vx, vy, x, y] = cv2.fitLine(mayorContorno, cv2.DIST_L1, 0, 0.01, 0.01)
					
					#Obtener el punto mas a la izquierda y mas a la derecha
					lefty = int((-x * vy/vx) +y)
					righty = int(((cols-x)* vy/vx) +y)
					
					#Calculo del angulo de la linea
					self.angulo = math.atan2(vy,vx) *180/np.pi
				
					indice = round(np.interp(self.angulo,self.angulos,self.indicesAngulos))

					#Comprobar en que tercio de la vertical se encuentra
					#el punto mas pegado al borde izquierdo
					lado = 1
					if lefty < mask.shape[1]*0.33: 
						lado = 0
					elif lefty > mask.shape[1] * 0.66:
						lado = 2

					#Asiganmos el estado segun el indice del angulo y el lado en el que se encuentra
					self.index = indice + (self.angulos.size * lado)
					
				
					cv2.line(mask2,(cols-1, righty),(0,lefty), (127), 1)
			'''
			#Analisis del tiempo requerido para la ejecucion
			t2 = time.time()
			self.suma += (t2 - t1)
			self.calculos += 1
			
			self.media = self.suma/self.calculos
			'''
			'''
			
			self.angulo = math.atan2((x1-x2),-(y1-y2)) *180/np.pi

			indice = round(np.interp(self.angulo,self.angulos,self.indicesAngulos))

			#Comprobar en que tercio de la coordenada horizontal se encuentra
			#el punto mas pegado al borde inferior
			lado = 1
			if x2< mask.shape[0]*0.33: 
				lado = 0
			elif x2 > mask.shape[0] * 0.66:
				lado = 2

			#Asiganmos el estado segun el indice del angulo y el lado en el que se encuentra
			self.index = indice + (self.angulos.size * lado)
			''
			else:
				#Si no se ha detectado ninguna linea, se asigna un 
				#estado que se corresponde con el ultimo de la lista
				self.index = self.angulos.size * 3
			'''
				#actualizamos la ultima imagen almacenada
			self.lastImg = mask2
    
	def getNumEstados(self):
		return self.angulos.size * 3 + 1

	def printUltimaFotog(self):
		#Guardar la ultima imagen almacenada en un archivo, incluyendo el angulo e indice asignado.
		cv2.imwrite('{n}_{angulo:.2f}_{index}.jpg'.format(n=self.nFoto, angulo=self.angulo, index=self.index),self.lastImg)
		self.nFoto += 1
		#print("Tiempo medio (s): ", self.media, " fps: ", 1/self.media)

	def read(self):
		# return the frame most recently read
		return self.index


	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
