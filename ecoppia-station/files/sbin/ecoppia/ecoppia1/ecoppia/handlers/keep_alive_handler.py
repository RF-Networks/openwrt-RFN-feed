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

class KeepAliveHandler:

    def __init__(self):
        self.server_in_types = [SmartStPkgType.KeepAlive]
        #self.out_type = SmartStPkgType.KeepAliveAck
        self.server_context = None
        self.handlingQueue = Queue()
        self.pill2kill = threading.Event()
        self.startHandlePkgs()

    def setServerContext(self, context):
        self.server_context = context

    def processServerPackage(self, pkgInfo):
        tcp_log.debug("Process {pi}".format(pi = str(pkgInfo)))
        self.server_context.doSendPkg(PackageInfo(SmartStPkgType.KeepAliveAck, "", pkgInfo.sessionid))

    def addPkgToHandlingQueue(self, pkgInfo):
        self.handlingQueue.put(pkgInfo)

    def stopHandlePkgs(self):
        self.pill2kill.set()

    def startHandlePkgs(self):
        self.pill2kill.clear()
        thread.start_new_thread(self.managePackagesToBeHandled, ())
                
    def managePackagesToBeHandled(self):
        app_log.info("in Keep Alive Handler managePackagesToBeHandled thread started..")
        while not self.pill2kill.wait(0):
            try:
                pkgInfo = self.handlingQueue.get()
                self.processServerPackage(pkgInfo)
                self.handlingQueue.task_done()
            except Exception as e:
                app_log.error("something wrong in Keep Alive handler inside managePackagesToBeHandled, skip to next iteration.. error = {err}".format(err = str(e.args)))
            except Exception:
                e = sys.exc_info()[0]
                app_log.error("something wrong in Keep Alive handler inside managePackagesToBeHandled, skip to next iteration.. error = {err}".format(err = str(e)))
        
        app_log.info("in Keep Alive Handler managePackagesToBeHandled thread stopped !")

    def __del__(self):       
        app_log.info("KeepAliveHandler deleted")
        

        