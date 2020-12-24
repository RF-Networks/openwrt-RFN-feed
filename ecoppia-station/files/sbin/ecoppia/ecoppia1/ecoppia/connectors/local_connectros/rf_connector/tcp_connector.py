from ecoppia.globals import *
import socket

class RfConnector:
    def __init__(self):
        self.ser_socket = None

    def doSend(self, data):
        self.ser_socket.send(data)

    def doReceive(self, num_of_bytes = 1, timeout = None):
        #self.ser_socket.timeout = timeout
        return self.ser_socket.recv(num_of_bytes)

    def connect(self, read_timeout, write_timeout, baudrate, port):
        self.description = port
        self.ser_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           
        self.ser_socket.connect((port, 10001))


    #def closeSocket(self):
    #    try:
    #        self.ser_socket.close()
    #        app_log.info("Serial Port Is Closed !") 

    #    except Exception:
    #        app_log.error("Close Ser