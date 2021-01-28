#import sys
#import threading
#import time
#import select
#import struct
#import binascii
#from Queue import Queue
#from threading import Thread
#import math
#import serial
#from ecoppia.lib.package_info import *
#from exceptions import *
#import random
#from multiprocessing import Lock
#from ecoppia.globals import *
#from struct import *

#class UnitFW:
#    _FW_2 = 2
#    _FW_3 = 3


#class RFDemoSocket:
#    def __init__(self):
#        self.command = bytearray()
#        self.result = None
#        self.wait2command = threading.Event()
#        self.lock = Lock()
#        self.unitFW = UnitFW._FW_3

#        self.bl_demo = 0

#    def flushInput(self):
#        pass
#    def flushOutput(self):
#        pass

#    def write(self, command):
#        with self.lock:
#            if len(self.command) > 0:
#                app_log.error("Error : one command at a given time is allowed in RF demo connector!")
#                raise IOError("Error : one command at a given time is allowed in RF demo connector!")

#            self.bl_demo %= 5 
#            self.bl_demo += 1

#            self.command.extend(command)

#            b1 = bytearray() 
#            b2 = bytearray() 

#            if random.choice([True]):
#                b1 = bytearray(b"OK\r") 
#                b2 = bytearray()                           
#                if len(command) >= 12:

#                    if self.unitFW == UnitFW._FW_3:

#                        cmdnum = int(self.command[7])

#                        if cmdnum == 0x89:
#                            b2 = bytearray()
#                            b2.extend([self.command[0], self.command[1], 0x3D, self.command[3], self.command[4], self.command[5], self.command[6], 0x0, 0x0, 0x5, 0x0, 0x0, 0x0, 0x0])
#                            config = []
#                            for x in range(0, 175):
#                                config.append(x)
#                            b2.extend([0xB7])
#                            b2.extend(config)
#                            b2.extend([0xD, 0xFF, 0xD])  
                    
#                        elif cmdnum == 0x8A:
#                            b2 = bytearray(
#                            [                        
#                            self.command[0], self.command[1], 0x3D, self.command[3], self.command[4], self.command[5], self.command[6], 0x0, 0x0, 0x5, 0x0, 0x0, 0x0, 0x0,  0x4, 0xAA, 0xAA, 0xAA, 0x01, 0xD, 0xF0, 0xD,
#                            self.command[0], self.command[1], 0x3D, self.command[3], self.command[4], self.command[5], self.command[6], 0x0, 0x0, 0x5, 0x0, 0x0, 0x0, 0x0,  0x4, 0xAA, 0xAA, 0xAA, 0x02, 0xD, 0xF1, 0xD,
#                            self.command[0], self.command[1], 0x3D, self.command[3], self.command[4], self.command[5], self.command[6], 0x0, 0x0, 0x5, 0x0, 0x0, 0x0, 0x0,  0x4, 0xAA, 0xAA, 0xAA, 0x03, 0xD, 0xF2, 0xD                             
#                            ])
#                        else:
#                            b2 = bytearray([self.command[0], self.command[1], 0x3D, self.command[3], self.command[4], self.command[5], self.command[6], 0x0, 0x0, self.bl_demo, 0x0, 0x0, 0x0, 0x0,  0x0, 0xD, 0xFA, 0xD])
                  
#                    elif self.unitFW == UnitFW._FW_2:

#                        # cmd = unpack('H', pack('BB', self.command[5], self.command[6]))

#                        #RETURN 'AT BASE'
#                        cmdrsp = unpack('BB',pack('>H',0x02))

#                        b2 = bytearray()
#                        b2.extend([self.command[0], self.command[1], 0x3D])
#                        b2.extend([self.command[3], self.command[4], cmdrsp[0], cmdrsp[1], self.command[7], self.command[8], 0x05, 0x01])
#                        b2.extend([0xD, 0xFF, 0xD])  

#            else:
#                b1 = bytearray(b"ERROR\r") 
#                b2 = bytearray()   

#            del self.command[0:len(command)]
            
#            # When False Simulate AckTimeout
            
#            if random.choice([True]):
#                self.result = b1 + b2
#                self.wait2command.set()            
#            else:
#                b1 = bytearray() 
#                b2 = bytearray()      
#                self.result = b1+b2



#    def read(self):
        
#        self.wait2command.wait(2)
        
#        if(self.wait2command.isSet() == False):
#            raise socket.timeout
        
#        with self.lock: 
#            bytes_to_read = random.randint(1, len(self.result))
#            result_partial = self.result[0:bytes_to_read]
#            del self.result[0:bytes_to_read]

#            if self.result == None or len(self.result) == 0:
#                self.wait2command.clear()

#            return str(result_partial)



#class RFDemoConnector:
#    def __init__(self, handler):
#        self.handler = handler
#        self.send_lock = Lock()
#        self.ser_socket = None
#        self.pill2kill = threading.Event()

#    def doSend(self, data):
#        with self.send_lock:
#            self.ser_socket.write(data)

#    def doReceive(self):        
#        return self.ser_socket.read()

#    def connect(self, timeout):
#        self.ser_socket = RFDemoSocket()

#    def flushAll(self):
#        try:
#            self.ser_socket.flushInput()
#            self.ser_socket.flushOutput() 

#        except Exception:
#            e = sys.exc_info()[0]
#            app_log.error("RF connector error in flushAll... : " + str(e))
     
