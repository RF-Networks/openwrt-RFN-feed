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
from Queue import Queue
from threading import Thread
from configuration.config import *
from ecoppia.lib.package_info import *
from exceptions import *


class PuttyConnector:
    def __init__(self, handler, sessionId):
        self.handler = handler
        self.sessionId = sessionId
        self.putty_socket = None
        self.send_lock = threading.Lock()
        #self.transport_in_stop_event = threading.Event()
        self.pill2kill = threading.Event()

    def doSend(self, data):
        tmp = bytearray()
        tmp.extend(data)
        with self.send_lock:
            _,w,_ = select.select([], [self.putty_socket], [])
            if (len(w) > 0): 
                #logging.info('SEND TO PUTTY SOCKET (22): {0}'.format(bytearrayToStr(tmp)))         
                self.putty_socket.send(data)
            else:
                app_log.error("putty connector doSend failed (wlist is empty)")
                raise Exception("Putty Socket Send Failed (wlist is empty)")

    def doReceive(self):
        msg = bytearray()
        r,_,_ = select.select([self.putty_socket], [], [])
        if (len(r) > 0) :
            data = self.putty_socket.recv(1024)
            if(len(data) == 0):
                raise Exception('Receive 0 Bytes')            
            msg.extend(data)
            return msg
        else:
            app_log.error("putty connector doReceive failed (rlist is empty)")
            raise Exception("Putty Socket Receive Failed (rlist is empty)")


    def closeSocket(self):
        try:
            self.putty_socket.shutdown(socket.SHUT_RDWR)
        except Exception:
            app_log.error("Putty Connector, Exception in shutdown(socket.SHUT_RDWR)")		 
        try:
            self.putty_socket.close()
        except Exception:
            app_log.error("Putty Connector, Exception in socket.close()")	
        else:
            app_log.info("putty socket closed successfully!") 

        self.putty_socket = None

    def doRun(self):
        app_log.info("Putty Connector transport started..")
        self.pill2kill.clear()
        while not self.pill2kill.wait(0):
            try:
                payload = self.doReceive()                    
            except Exception:
                e = sys.exc_info()[0]
                app_log.fatal("doReceive in Putty Connector failed with error = "+str(e))
                break
            else:                                                   
                try:
                    self.handler.handlePuttyPackage(self.sessionId, payload)            
                except Exception:
                    e = sys.exc_info()[0]
                    app_log.error("handlePuttyPackage in doRun Putty Connector failed with error = "+str(e))                   
                

        self.closeSocket()
        app_log.info("in Putty Connector transport thread stopped !")
               
    def connect(self):
        app_log.info("wait for putty")
        try:                 
            self.putty_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           
            self.putty_socket.connect((PUTTY_IP, PUTTY_PORT))                                                      
        except Exception:
            app_log.error("connection to putty (" + PUTTY_IP + ":" + str(PUTTY_PORT) + ") failed !")
            raise

        app_log.info("putty (" + PUTTY_IP + ":" + str(PUTTY_PORT) + ") is connected !")
                     
    def run(self):
        app_log.info("putty connector run started..")

        self.connect()
        thread.start_new_thread(self.doRun, ())


    def stop(self):  
        self.closeSocket() 
        self.pill2kill.set()           