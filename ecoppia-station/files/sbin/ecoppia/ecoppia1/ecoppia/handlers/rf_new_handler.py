import base64
import re
import json

from ecoppia.connectors.local_connectros. rf_connector.telit_le_50_connector  import TelitLE50Connector
from ecoppia.lib.package_info import *
from ecoppia.lib.propery_change_info import *
from ecoppia.lib.sqlite_facilitator import *
from ecoppia.handlers.requests.master_packet_serializer import *

#import _strptime
from datetime import datetime, time


class RfNewHandler(object):

    def __init__(self, reset_facilitator):
        self.server_context = None
        self.server_in_types = [SmartStPkgType.NewRFCommand]
        self.property_types = [PropertyType.RFConfig]

        self.telit_connector = TelitLE50Connector(reset_facilitator)
        #self.rf_scheduler = CyclicScheduler()


    def setShadowContext(self, context):
        self.shadow_context = context

    def setServerContext(self, context):
        self.server_context = context

    def processPropertyChange(self, pkgInfo):
        app_log.debug("Process New RF property")

        inner_payload_str = json.dumps(pkgInfo.desired, default=MasterPacketSerializer.serialize)

        request = json.loads(inner_payload_str, object_hook = MasterPacketSerializer.deserialize)
        request.telit_connector = self.telit_connector
        response = request.execute()

        self.shadow_context.doReportState(pkgInfo.type, pkgInfo.desired)

    def processServerPackage(self, pkgInfo):

        app_log.debug("Process New RF Packet")

        ackPkg = PackageInfo(SmartStPkgType.RFCommandAck, '', pkgInfo.sessionid)
        self.server_context.doSendPkg(pkgInfo, ackPkg)

        request = pkgInfo.payload
        request.telit_connector = self.telit_connector
        response = request.execute()

        if request.WaitForUnitResponse == True:
            rsltPkg = PackageInfo(SmartStPkgType.RFResponse, response, pkgInfo.sessionid)
            self.server_context.doSendPkg(pkgInfo,rsltPkg)


#        if sendSuccess: 
#            self.shadow_context.doReportState(pkgInfo.type, pkgInfo.payload)


