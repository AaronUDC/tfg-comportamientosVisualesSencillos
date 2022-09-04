from ast import Bytes
from pickletools import uint8
import socketserver
import socket
from typing import final
import cv2
import numpy as np

class MyUDPHandler(socketserver.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0]

        img = np.frombuffer(data, dtype=np.uint8)
        self.server.imagen = np.reshape(img, (8,6))

class MyServer(socketserver.UDPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)

        self.imagen = None




IP_PC, PORT_PC = "192.168.1.44", 9999
IP_ROBOT, PORT_ROBOT  = "192.168.1.38", 9998

response = 1
if __name__ == "__main__":

    sockEnvios = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    with MyServer((IP_PC, PORT_PC), MyUDPHandler) as server:
        server.timeout = 1
        try:
            while True:
                server.handle_request()


                sockEnvios.sendto(np.array(([response]), dtype=np.uint8).tobytes(), (IP_ROBOT, PORT_ROBOT))

                print(server.imagen)
                
                #print("Timeout")
        finally:
            server.server_close()