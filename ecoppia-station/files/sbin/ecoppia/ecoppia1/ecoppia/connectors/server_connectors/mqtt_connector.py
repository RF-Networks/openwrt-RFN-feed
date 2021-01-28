from exceptions import *
import re
import base64
import datetime as dt
from threading import Timer

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from ecoppia.globals import *
from configuration.config import *
from ecoppia.lib.package_info import *
from ecoppia.handlers.requests.rf_configuration_request import *
from ecoppia.handlers.requests.rf_boradcast_request import *
from ecoppia.handlers.requests.rf_unicast_request import *

class MqttConnector:

    def __init__(self, reset_facilitator):
        self.reset_facilitator = reset_facilitator
        self.handlers = {}
        self._timer = None
        self.disconnected_time_to_reset = MINIMAL_DISCONNECTED_TIME_TO_RESET
        self.resetWatchdog()

    def resetWatchdog(self):
        if self._timer != None:
            self._timer.cancel()

        self._timer = Timer(self.disconnected_time_to_reset, self.watchdog)
        self._timer.start()

    def watchdog(self):
        app_log.info("**** BROKER WATCHDOG ********")
        self.reset_facilitator.DoHardReset()
        self.resetWatchdog()

    def onOnline(self):
        app_log.info("BROKER IS ONLINE")

    def onOffline(self):
        app_log.info("BROKER IS OFFLINE")

    def packBrokerPkg(self, pkgInfo):
        str = json.dumps(pkgInfo, default=self.serialize)
        return str

    def deserialize(self, obj):
        
        if '$type' in obj:

            data_type = obj['$type']

            if data_type == 'System.Byte[], mscorlib':
                return base64.b64decode(obj['$value'])

            m = re.search('Ecoppia\.CMM\.Contract\.MasterStation\.(\w*), Ecoppia\.CMM\.Service',data_type)
            type = m.group(1)

            if type == 'ConfigRfRequest':
                return RfConfigurationRequest(obj['Name'], obj['Commands'], obj['DoResetBeforeConfig'])
            elif type == 'UnicastRfRequest':
                return RfUnicastRequest(obj['Commands'])
            elif type == 'BroadcastRfRequest':
                return RfBoradcastRequest(obj['Command'], obj['WaitForUnitResponse'])
            elif type == 'WorkPlanRequest':
                return RFWorkPlanRequest(obj['Jobs'])
            elif type == 'CommandBufferUnit' and 'AddCrc' in obj:
                return RfNewRequestPerCommand(obj['Command'], obj['AddCrc'], obj['Units'])
            elif type == 'CommandBufferUnit':
                return RfNewRequestPerCommand(obj['Command'], True, obj['Units'])
            elif type == 'ConfigRfCommand':
                return RfConfigCommand(obj['ATS'], obj['Value'])
            elif type == 'WorkPlanItem':
                return RfJob(self.parse_time(obj['StartTime']), self.parse_time(obj['EndTime']) , obj['Period'],obj['Job'])
            elif type == 'SmartStationBrokerPacket' and 'Site' in obj:
                return PackageInfo(obj['Type'], obj['Payload'] , obj['SessionId'], obj['Version'], obj['CallbackQueue'], obj['Site'])
            elif type == 'SmartStationBrokerPacket' and 'CallbackQueue' in obj:
                return PackageInfo(obj['Type'], obj['Payload'] , obj['SessionId'], obj['Version'], obj['CallbackQueue'], '')
            elif type == 'SmartStationBrokerPacket':
                return PackageInfo(obj['Type'], obj['Payload'] , obj['SessionId'], obj['Version'], '', '')

    def parse_time(self, time_str):
        
        search_obj = re.search(r'((2[0-3]|[0-1][0-9]):([0-5][0-9]):([0-5][0-9]))', time_str, re.M | re.I)

        if search_obj:

            h = int(search_obj.group(2))
            m = int(search_obj.group(3))
            s = int(search_obj.group(4))
            
            return time(h, m, s)

    def serialize(self,obj):
        ##"""JSON serializer for objects not serializable by default json

        if isinstance(obj, dt.date):
            serial = obj.isoformat()
            return serial

        if isinstance(obj, dt.time):
            serial = obj.isoformat()
            return serial

        return obj.__dict__
    
    def doPublishWeather(self, data):
        self.doPublish('ByStation','Weather', data)

    def doPublishToSite(self, site, queue, data):
        topicType = 'SmartStationToMaster'

        if(len(queue) > 0):
            topicExtension = 'Queue/' + queue
            if(len(site) > 0):
                topicType = 'BySite'
                topicExtension = site + '/' + topicExtension
        else:
            topicExtension = ''

        self.doPublish(topicType, topicExtension, data)
        
    def doPublish(self, topicType, topicExtension, data):
        try:
            topic = ENV 
            topic += "/" + topicType 
            topic += "/" + NAME
            #topic += "/" + 'tg_site01' 
            if len(topicExtension) > 0:
                topic = topic + "/" + topicExtension

            subscriptionRslt = self.AWSIoTMQTTClient.publish(topic, data, 0)

            if(subscriptionRslt):
                app_log.info(topic + " Published Successfully")
                #PO = 89
            else:
                app_log.error(topic + " COULD NOT BE Published !")
        except Exception as e:
            app_log.error("server connector, error in doPublish , " + str(traceback.format_exc()))  
            raise      
        except Exception:
            e = sys.exc_info()[0]              
            app_log.error("server connector, error in doPublish , " + str(traceback.format_exc()))
            raise
            
    def doSendPkg(self, requestPkgInfo, pkgInfo):
        try:
            self.doPublishToSite(requestPkgInfo.site, requestPkgInfo.callbackQueue , self.packBrokerPkg(pkgInfo))
            app_log.info(str(pkgInfo) + " Published")
        except Exception as e:
            app_log.exception("server connector, error in doSendPkg")
            raise      
        except Exception:
            e = sys.exc_info()[0]
            app_log.exception("server connector, error in doSendPkg")
            raise

    def subscribe(self, handler): 
        handler.setServerContext(self)        
        for in_type in handler.server_in_types:            
            self.handlers[in_type] = handler
            app_log.info("in server connector subscription of " + SmartStPkgType.getName(in_type) + " is completed !") 

    def brokerCallback(self, client, userdata, message):

        self.resetWatchdog()
        #app_log.info("in brokerCallback Received a new message of topic:
        #"+str(message.topic))
        try:

            pkgInfo = json.loads(message.payload, object_hook = self.deserialize)
            app_log.info("in brokerCallback Received " + str(pkgInfo))

            if pkgInfo.version == software_version:
                handler = self.handlers.get(pkgInfo.type, None)
                if handler != None:
                    handler.addPkgToHandlingQueue(pkgInfo)          
                else:
                    app_log.fatal("in brokerCallback, No Handler For Packet Type " + str(pkgInfo.type) + " Found !")
            else:
                app_log.fatal("version mismatch")
                self.doSendPkg(pkgInfo, PackageInfo(SmartStPkgType.VersionMismatch, "", pkgInfo.sessionid))
        except Exception:
            app_log.exception("brokerCallback failed")

    def run(self):
        app_log.info("server connector run started..")

        topic = ENV + "/MasterToSmartStation/" + NAME
        app_log.info("Try Subscribe :  " + topic)
        sunscriptionSuccess = self.AWSIoTMQTTClient.subscribe(topic, 1, self.brokerCallback)
        if(sunscriptionSuccess):
            app_log.info("BROKER Subscribed Successfully, " + topic)
        else:
            app_log.info("BROKER Subscription FAILED !")