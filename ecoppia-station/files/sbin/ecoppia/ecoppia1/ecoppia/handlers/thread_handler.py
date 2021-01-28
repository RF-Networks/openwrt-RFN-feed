import sys
import thread
from threading import Thread, Event
from Queue import Queue
from ecoppia.globals import *
from ecoppia.lib.package_info import *
from ecoppia.lib.propery_change_info import *

class ThreadHandler:
    #msgHandler should implement the following properties and functions for message processing: server_in_types, setServerContext, processServerPackage  
    #and the following properties and functions for the shadow processing: property_types, setShadowContext, processPropertyChange, 
    def __init__(self, msgHandler):
        self.msgHandler = msgHandler
        if hasattr(msgHandler, "server_in_types"):
            self.server_in_types = msgHandler.server_in_types
        if hasattr(msgHandler, "property_types"):
            self.property_types = msgHandler.property_types
        self.handlingQueue = Queue()
        self.pill2kill = Event()
        self.startHandlePkgs()

    def setServerContext(self, context):
        self.msgHandler.setServerContext(context)

    def setShadowContext(self, context):
        self.msgHandler.setShadowContext(context)

    def startHandlePkgs(self):
        self.pill2kill.clear()
        thread.start_new_thread(self.managePackagesToBeHandled, ())

    def stopHandlePkgs(self):
        self.pill2kill.set()

    def addPkgToHandlingQueue(self, pkgInfo):
        self.handlingQueue.put(pkgInfo)

    def managePackagesToBeHandled(self):
        app_log.info("ThreadHandler managePackagesToBeHandled thread started for {handler}".format(handler = self.msgHandler.__class__.__name__))
        shouldStop = False
        while not (shouldStop or self.pill2kill.wait(0)):
            try:
                pkgInfo = self.handlingQueue.get()
                if isinstance(pkgInfo, PackageInfo):
                    shouldStop = self.msgHandler.processServerPackage(pkgInfo)
                elif isinstance(pkgInfo, PropertyChangeInfo):
                    shouldStop = self.msgHandler.processPropertyChange(pkgInfo)
                else:
                    app_log.error("unknown package type {type} inside managePackagesToBeHandled, skip to next iteration..".
                                  format(type = type(pkgInfo)))
                self.handlingQueue.task_done()
            except Exception as e:
                app_log.exception("something wrong in {handler} inside managePackagesToBeHandled, skip to next iteration..".
                              format(handler = self.msgHandler.__class__.__name__))
            except Exception:
                e = sys.exc_info()[0]
                app_log.exception("something wrong in {handler} inside managePackagesToBeHandled, skip to next iteration..".
                              format(handler = self.msgHandler.__class__.__name__))
        
        app_log.info("ThreadHandler managePackagesToBeHandled thread stopped for {handler}".format(handler = self.msgHandler.__class__.__name__))

    def __del__(self):       
        app_log.info("ThreadHandler deleted for {handler}".format(handler = self.msgHandler.__class__.__name__))
