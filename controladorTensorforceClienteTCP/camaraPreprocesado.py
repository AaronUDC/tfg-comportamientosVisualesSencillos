# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
import math
import numpy as np

class CamaraPreprocesado:
    def __init__(self, resolution=(80, 64), outResolution = (10,8), framerate=32):
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
        self.processedFrame = None
        
        self.outResolution = outResolution
    def start(self):
            # start the thread to read frames from the video stream
            Thread(target=self.update, args=()).start()
            return self
    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.processedFrame = self.process_image(f.array, self.outResolution)
            self.frame = f.array
            self.rawCapture.truncate(0)
            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return
    def read(self):
        # return the frame most recently read
        return self.frame, self.processedFrame
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        
    def process_image(self, imageIn, resSalida):
        img = cv2.GaussianBlur(imageIn,(5,5),0, borderType = cv2.BORDER_REPLICATE)

        #Cambiamos el espacio de color a escala de grises
        imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        #Reescalar la imagen a la resolución de salida
        resizedImg = cv2.resize(imgGray, (resSalida[0],resSalida[1]), interpolation=cv2.INTER_LINEAR)
        
        return resizedImg
