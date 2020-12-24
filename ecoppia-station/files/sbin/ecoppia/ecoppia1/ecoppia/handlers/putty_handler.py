#import logging
import sys
from ecoppia.globals import *
import socket
import thread
import math
import threading
import time
import select
import Queue
from Queue import *
from threading import Thread
from threading import Timer
from ecoppia.lib.package_info import *

from ecoppia.connectors.local_connectros.putty_connector import *

class PuttyHandler:

    def __init__(self):
        self.server_in_types = [SmartStPkgType.PuttyToSmartSt]      
        self.server_context = None
        self.putty_in_types = [SmartStPkgType.PuttyFromSmartSt]
        self.putty_context = None

        self.handlingQueue = Queue()
        self.pill2kill = threading.Event()
        self.startHandlePkgs()


    def setServerContext(self, context):
        self.server_context = context

    def setPuttyContext(self, context):
        self.putty_context = context

    def processServerPackage(self, pkgInfo):
        bytearr = bytearray(pkgInfo.payload)
        #bytearr = bytearray()
        #bytearr.extend(pkgInfo.payload)
        sessionId = str(bytearr[0:16])
        data = bytearr[16:]

        if self.putty_context == None or self.putty_context.sessionId != sessionId:
            try:
                if self.putty_context != None:
                    self.putty_context.stop()
                self.putty_context = PuttyConnector(self, sessionId)
                self.putty_context.run()
                app_log.info("New Session Id received, stop current connector session reconnect and start listen to incoming data..")  
            except Exception:
                e = sys.exc_info()[0]
                app_log.error("putty handler, error in create and run PuttyConnector"+str(e))
                if self.putty_context != None:
                    self.putty_context.stop()
                    self.putty_context = None
                raise Exception("putty handler, error in create and run PuttyConnector")                  

        try:
            self.putty_context.doSend(str(data))
        except Exception:
            app_log.error("putty handler in processServerPackage, error in sending the data")
            raise Exception("putty handler in processServerPackage, error in sending the data")


    def handlePuttyPackage(self ,sessionId, payload):
        pkg = PackageInfo(SmartStPkgType.PuttyFromSmartSt, sessionId + payload)
        self.server_context.doSendPkg(pkg)


    def addPkgToHandlingQueue(self, pkgInfo):
        self.handlingQueue.put(pkgInfo)

    def stopHandlePkgs(self):
        self.pill2kill.set()

    def startHandlePkgs(self):
        self.pill2kill.clear()
        thread.start_new_thread(self.managePackagesToBeHandled, ())
                
    def managePackagesToBeHandled(self):
        app_log.info("in Putty Handler managePackagesToBeHandled thread started..")
        while not self.pill2kill.wait(0):
            try:
                pkgInfo = self.handlingQueue.get()
                self.processServerPackage(pkgInfo)
                self.handlingQueue.task_done()
            except Exception as e:
                app_log.error("putty handler, error inside iteration in managePackagesToBeHandled, error = " + str(e.args))
            except Exception:
                app_log.error("putty handler, error inside iteration in managePackagesToBeHandled")

        app_log.info("in Putty Handler managePackagesToBeHandled thread stopped !")

    def __del__(self):       
        app_log.info("PuttyHandler deleted")