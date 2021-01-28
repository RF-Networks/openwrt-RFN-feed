from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import time
import json
import logging
from threading import Timer, Event

from ecoppia.globals import *
from configuration.config import *
from ecoppia.lib.package_info import *
from ecoppia.lib.propery_change_info import *

class ShadowConnector(object):
    DEFAULT_TIMEOUT = 15 #default timout is 15 seconds

    def __init__(self):
        self.handlers = {}
        self.deviceShadowHandler = None
        self.version = -1
        self.stopGetFlag = Event()

    def run_client(self): 
        clientId = ENV + "-" + NAME
        #clientId = ENV + "/" + NAME + "/StationSide"

        myShadowClient = AWSIoTMQTTShadowClient(clientId)
        myShadowClient.configureEndpoint(AWS_IOT_END_POINT, AWS_IOT_PORT)
        myShadowClient.configureCredentials(ROOTCA_PATH, PRIVATEKEY_PATH, CERTIFICATE_PATH)
        myShadowClient.configureConnectDisconnectTimeout(self.DEFAULT_TIMEOUT)  
        myShadowClient.configureMQTTOperationTimeout(self.DEFAULT_TIMEOUT) 
        myShadowClient.onOnline = self.connectCallback
        myShadowClient.onOffline = self.disconnectCallback
        myShadowClient.connect()

        device_name = ENV + "-" + NAME
        self.deviceShadowHandler = myShadowClient.createShadowHandlerWithName(device_name, True)
        self.deviceShadowHandler.shadowRegisterDeltaCallback(self.callback)

        return myShadowClient._AWSIoTMQTTClient

    def subscribe(self, handler): 
        handler.setShadowContext(self)        
        for prop in handler.property_types:            
            self.handlers[prop] = handler
            app_log.info("in shadow subscription of {p} is completed!".format(p=prop)) 

    def connectCallback(self):
        app_log.info("Connect callback called")
        self.startGetThread()

    def disconnectCallback(self):
        app_log.info("Disconnect callback called")
        self.stopGetThread()

    def startGetThread(self):
        self.stopGetFlag.clear()
        thread.start_new_thread(self.shadowGet, ())

    def stopGetThread(self):
        self.stopGetFlag.set()

    def shadowGet(self):
        #do not start immediately, give time to setup handlers after the
        #connection established
        time.sleep(1)
        while True:
            if self.deviceShadowHandler is not None:
                try:
                    self.deviceShadowHandler.shadowGet(self.callback, self.DEFAULT_TIMEOUT)
                except Exception as e:
                    app_log.exception("failed requesting shadowGet, skip to next iteration..".
                              format(err = str(e.args)))
            if self.stopGetFlag.wait(5):
                break

    def callback(self, payload, responseStatus, token):
        # payload is a JSON string ready to be parsed using json.loads(...)
        # in both Py2.x and Py3.x
        try:
            app_log.info("Received a shadow get/delta response: " + responseStatus)
            app_log.info("Received a payload: " + str(payload))

            if not (responseStatus.startswith('delta') or responseStatus == 'accepted'):
                if responseStatus == 'rejected' and  "No shadow exists"  in str(payload):
                    self.stopGetThread()
                return

            self.stopGetThread()

            parsed = json.loads(payload, object_hook = decode_dict)
            delta = None
            desired = None
            if responseStatus.startswith('delta'):
                self.deviceShadowHandler.shadowGet(self.callback, self.DEFAULT_TIMEOUT)
                #delta = parsed["state"]
            elif responseStatus == "accepted":
                if ("delta" in parsed["state"]):
                    delta = parsed["state"]["delta"]
                    desired = parsed["state"]["desired"]
                    if self.version == -1 :
                        delta["TelitConfiguration"] = desired["TelitConfiguration"]

            if delta is not None:
                app_log.info("Delta: " + json.dumps(delta))
                newVersion = parsed["version"]
                if newVersion > self.version:
                    app_log.info("Newer version received: {ver}, old {oldVersion}. Performing upgrade".format(ver = newVersion, oldVersion = self.version))
                    self.version = newVersion
                    for type, data in delta.iteritems():
                        handler = self.handlers.get(type, None)
                        if handler != None:
                            handler.addPkgToHandlingQueue(PropertyChangeInfo(type, data, desired[type]))
                        else:
                            app_log.fatal("in Shadow Delta Callback, No Handler For Packet Type " + str(type) +"   data: "+ json.dumps(data)+"   desired:"+ json.dumps( desired) +" Found !")
                            app_log.fatal("handlers " + json.dumps(handlers) + " Found !")
                else:
                    app_log.info("Old version received: {ver}. Skipping upgrade".format(ver = newVersion))
            else:
                app_log.info("Delta: None")
        except Exception:
            weather_log.exception("shadow callback failed")

    def doReportState(self, type, data):
        reported = {
            "state": {
                "reported": {
                    type: data
                }
            }
        }

        reportedMessage = json.dumps(reported)
        app_log.info("doReportState Shadow update: " + reportedMessage)
        self.deviceShadowHandler.shadowUpdate(reportedMessage, None, self.DEFAULT_TIMEOUT)


    def doReportDesired(self, type, data):
        reported = {
            "state": {
                "desired": {
                    type: data
                }
            }
        }

        reportedMessage = json.dumps(reported)
        app_log.info("doReportDesired Shadow update: " + reportedMessage)
        self.deviceShadowHandler.shadowUpdate(reportedMessage, None, self.DEFAULT_TIMEOUT)




#from ecoppia.handlers.thread_handler import *
#import ecoppia.handlers.weather_handler
#import ecoppia.handlers.rf_new_handler
#import ecoppia.handlers.rf_handler

#class SubscriberByShadow:

#    def __init__(self, srv_connector):
#        app_log.info("SubscriberByShadow")
#        self.server_context = srv_connector
#        self.shadow_context = None
#        self.property_types = [PropertyType.StationType]
#        self.Initialized = False

#    def setShadowContext(self, context):
#        self.shadow_context = context

#    def processPropertyChange(self, pkgInfo):
#        try:
#            if self.Initialized:
#                app_log.info("Rebooting the device due to \"StationType\" updated to " + pkgInfo.payload)
#                os.system('reboot')

#            self.Initialized = True

#            if pkgInfo.payload == 'Weather':
#                self.server_context.subscribe(ThreadHandler(ecoppia.handlers.weather_handler.WeatherHandler()))

#            elif pkgInfo.payload == 'RF_Ec':
#                ecoppia.handlers.rf_new_handler.run()
#                self.server_context.subscribe(ThreadHandler(ecoppia.handlers.rf_new_handler.RfNewHandler()))

#            elif pkgInfo.payload == 'RF_Mitsubishi':
#                rfHandler = ThreadHandler(ecoppia.handlers.rf_handler.RFHandler())

#                self.subscribe(rfHandler)
#        except Exception:
#            weather_log.exception("shadow processPropertyChange failed")