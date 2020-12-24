import time
import base64
import sys

from ecoppia.lib.sqlite_facilitator import *
from ecoppia.connectors.local_connectros.rf_connector.telit_le_50_connector import *


from rx import Observable
from rx.concurrency import *
from rx.concurrency.newthreadscheduler import *


# -- DEBUG --
BACK_AND_FORTH_TIMEOUT_IN_MS = 5000
packet_id = 0

class ExecutableRequest:

    def __init__(self):
        self.telit_connector = None
        self.WaitForUnitResponse = True
        
    def get_current_rf_configuration(self):
        d = Dal()
        return d.get_configuration('RF')

    def update_rf_configuration(self, rf_config_name):
        d = Dal()
        return d.update_configuration('RF', rf_config_name)


    # To Be Override    
    def execute(self):
        pass


class RfUnitsResponse:

    def __init__(self, config_name):

        self.StationMessageType = 1
        self.StationRfConfig = config_name                
        self.ToUnit = [] #ToUnitData
        self.FromUnit = [] #FromUnitData

    def add_to_unit_data(self, data):
        self.ToUnit.append(data)

    def add_from_unit_data(self, data):
        self.FromUnit.append(data)



class ToUnitData:
    def __init__(self, unit_id):
        self.UnitId = unit_id
        self.Chunks = [] #ToUnitChunk

    def add_chunk(self, chunk):
        self.Chunks.append(chunk)

class ToUnitChunk:
    def __init__(self, timestamp, data, telit_response):
        self.Timestamp = timestamp
        self.Data = data # base64 string
        self.TelitResponse = telit_response # emun TelitResponse

class FromUnitData:
    def __init__(self, unit_id, end_reason):
        self.UnitId = unit_id
        self.EndReason = end_reason #emun FromUnitEndReasonType
        self.Chunks = [] #FromUnitChunk

    def add_chunk(self, Chunk):
        self.Chunks.append(Chunk)

class FromUnitChunk:
    def __init__(self, timestamp, chunk_seq_num, data, rssi):
        self.Timestamp = timestamp
        self.ChunkSeqNum = chunk_seq_num
        self.Data = data # base64 string
        self.Rssi = rssi