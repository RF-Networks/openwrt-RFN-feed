import os
import sys
#import logging
from ecoppia.globals import *
import socket
import thread
import math
import threading
import time
import select
import struct
import binascii
import traceback

from Queue import Queue
from threading import Thread
import serial
from ecoppia.lib.package_info import *
from exceptions import *


def to_hex(str):
    res = ' '.join("{:02X}".format(ord(x)) for x in str)
    return res

class RfConnector:
    def __init__(self):
        self.ser_socket = None
        self.description = ""
    def description(self):
        return self.ser_socket.port

    def doSend(self, data):
        self.ser_socket.write(data)
        app_log.warning("Serial Connector Send:" + to_hex(data) )


    def doReceive(self, num_of_bytes = 1, timeout = None):
        self.ser_socket.timeout = timeout
        r =  self.ser_socket.read(num_of_bytes)
        app_log.debug("doReceive: " + str(r))
        return r
    def doReceiveCR(self,timeout = 1 ,CR = '\r'):
        self.ser_socket.timeout = timeout
        r = self.ser_socket.read_until(CR)
        app_log.warning("doReceiveCR: "  + to_hex(r))
        if len(r)== 0:
            return r 
        if r[0] =='\x00':
            return r[1:]
        else: 
            return r
    def flushAll(self):
        try:
            bytes_to_read = self.ser_socket.inWaiting()

            if bytes_to_read > 0:

                dump_str = repr(self.ser_socket.read(bytes_to_read))             
                
                app_log.warning("Serial Connector Dump Data Detected and Flushed : {dumps}".format(dumps = dump_str))

            self.ser_socket.flushInput()
            self.ser_socket.flushOutput() 

        except Exception:
            app_log.error("Serial Connector in Flush All : " + str(traceback.format_exc()))
        else:
            app_log.info("Successfully Flush Serial Port : " + self.ser_socket.port)

    def connect(self, read_timeout, write_timeout, baudrate, port):
        self.description = port
        self.ser_socket = serial.Serial(timeout = read_timeout)
        self.ser_socket.port = port
        self.ser_socket.baudrate = baudrate
        self.ser_socket.bytesize = serial.EIGHTBITS    #number of bits per bytes
        self.ser_socket.parity = serial.PARITY_NONE    #set parity check: no parity
        self.ser_socket.stopbits = serial.STOPBITS_ONE #number of stop bits
        self.ser_socket.timeout = read_timeout #timeout block read
        self.ser_socket.xonxoff = False        #disable software flow control
        self.ser_socket.rtscts = False         #disable hardware (RTS/CTS) flow control
        self.ser_socket.dsrdtr = False         #disable hardware (DSR/DTR) flow control
        self.ser_socket.writeTimeout = write_timeout       #timeout for write

        try: 
            self.ser_socket.open()

        except Exception:
            app_log.fatal("Open Serial Port Failed : "+ str(traceback.format_exc()))
            raise
                          
        else:
            app_log.info("Successfully Open Serial Port : " + self.ser_socket.port)

            self.flushAll()

    def closeSocket(self):
        try:
            self.ser_socket.close()
            app_log.info("Serial Port Is Closed !") 

        except Exception:
            app_log.error("Close Serial Port Failed : "+ str(traceback.format_exc()))