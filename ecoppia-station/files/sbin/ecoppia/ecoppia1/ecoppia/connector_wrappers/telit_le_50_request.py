import sys
import base64
from time import gmtime, strftime
import sqlite3

from ecoppia.lib.sqlite_facilitator import *
from ecoppia.connector_wrappers.telit_le_50_sync import *

RESET_CONFIG_TIME_SEC = 2


class RfConfigUpdateResponse:

    def __init__(self, name, success):
        self.StationMessageType = 0
        self.Name = name
        self.Success = success
        self.Commands = [] # RfConfigResultCommand
    
    def add_to_commands(self, command):
        self.Commands.append(command)

class RfConfigResultCommand:

    def __init__(self, timestamp, ats, value):
        self.Timestamp = timestamp
        self.ATS = ats
        self.Value = value


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