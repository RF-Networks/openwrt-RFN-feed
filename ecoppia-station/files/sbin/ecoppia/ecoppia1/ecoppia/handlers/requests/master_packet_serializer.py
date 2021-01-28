import time
import json
import re

from ecoppia.handlers.requests.rf_configuration_request import *
from ecoppia.handlers.requests.rf_boradcast_request import *
from ecoppia.handlers.requests.rf_unicast_request import *


class MasterPacketSerializer(object):

    @staticmethod
    def deserialize(obj):
        
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
            elif type == 'CommandBufferUnit':
                return RfNewRequestPerCommand(obj['Command'], obj['Units'])
            elif type == 'ConfigRfCommand':
                return RfConfigCommand(obj['ATS'], obj['Value'])
            elif type == 'WorkPlanItem':
                return RfJob(parse_time(obj['StartTime']), parse_time(obj['EndTime']) , obj['Period'],obj['Job'])
            elif type == 'SmartStationBrokerPacket':
                return PackageInfo(obj['Type'], obj['Payload'] , obj['SessionId'], obj['Version'])

    @staticmethod
    def serialize(obj):
        ##"""JSON serializer for objects not serializable by default json

        if isinstance(obj, dt.date):
            serial = obj.isoformat()
            return serial

        if isinstance(obj, dt.time):
            serial = obj.isoformat()
            return serial

        return obj.__dict__

    @staticmethod
    def parse_time(time_str):
        
        search_obj = re.search(r'((2[0-3]|[0-1][0-9]):([0-5][0-9]):([0-5][0-9]))', time_str, re.M | re.I)

        if search_obj:

            h = int(search_obj.group(2))
            m = int(search_obj.group(3))
            s = int(search_obj.group(4))
            
            return time(h, m, s)