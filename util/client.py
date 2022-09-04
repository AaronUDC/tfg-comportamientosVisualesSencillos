

from ctypes.wintypes import HICON
from pickletools import uint8
import socket
import socketserver
import sys
import cv2
from cv2 import IMREAD_GRAYSCALE
import numpy as np
import time
class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """
    def handle(self):
        data = self.request[0]
        self.server.response = np.frombuffer(data, dtype=np.uint8)[0]

        
class MyServer(socketserver.UDPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.timeout = 2
        self.response = 0

    def handle_timeout(self):
        self.response = -1

img_path = "D:/Documentos/Cole/Carrera/5/TFG/tfg-comportamientosVisualesSencillos/Webots/controllers/tensorforceController/evaluacion/agenteDeepQLearning_03_10.07.2022_16.32.28/states/state_agenteDeepQLearning_03_10.07.2022_16.32.28.000954.png"

IP_PC, PORT_PC = "192.168.1.44", 9999
IP_ROBOT, PORT_ROBOT  = "192.168.1.44", 9998
data = cv2.imread(img_path,IMREAD_GRAYSCALE)
dataBytes = data.tobytes()

y = np.frombuffer(dataBytes, dtype=data.dtype)
print(type(dataBytes))
# SOCK_DGRAM is the socket type to use for UDP sockets
sockOut = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockIn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# As you can see, there is no connect() call; UDP has no connections.
# Instead, data is directly sent to the recipient via sendto().

server = MyServer((IP_ROBOT,PORT_ROBOT), MyUDPHandler)
try:
    while True:
        sockOut.sendto(dataBytes, (IP_PC, PORT_PC))
        server.handle_request()

        print("Sent:     {}".format(dataBytes))
        print("Received: {}".format(server.response))
        #time.sleep(0.3)
finally:

    server.server_close()