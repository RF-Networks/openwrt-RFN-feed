from ecoppia.connector_wrappers.telit_le_50 import *
from ecoppia.connector_wrappers.telit_le_50_sync import *
from ecoppia.lib.sqlite_facilitator import *
from ecoppia.lib.cyclic_scheduler import *

import sys
import base64
from time import gmtime, strftime
import sqlite3

packet_id = 0
RESET_CONFIG_TIME_SEC = 2

# ONE REQUEST AT A TIME ONLY FROM A SINGLE THREAD ON A QUEUING PRINCIPLE BASIS

class ExecutableRequest:
        
    def get_current_rf_configuration(self):
        d = Dal()
        return d.get_configuration('RF')

    def update_rf_configuration(self, rf_config_name):
        d = Dal()
        return d.update_configuration('RF', rf_config_name)


    # To Be Override    
    def execute(self):
        pass

class RFWorkPlanRequest(ExecutableRequest):

    def __init__(self, rf_jobs):

        self.rf_jobs = rf_jobs
        self.rf_scheduler = None

    def execute(self):

        self.rf_scheduler.stop_all()

        self.rf_scheduler.start()

        for job in self.rf_jobs:

            self.rf_scheduler.create_task(job)

class RfJob(CyclicJob):

    def __init__(self, start_time, stop_time, period, job):

        CyclicJob.__init__(self, start_time, stop_time, period, 'RfJob')

        self.job = job

    def execute(self):

        self.job.execute()

class RfConfigurationRequest(ExecutableRequest):

    def __init__(self, name, commands, doResetBeforeConfig):

        self.Name = name
        self.Commands = commands #RfConfigCommand
        self.DoResetBeforeConfig = doResetBeforeConfig
        self.sync_telit_connector = None

    def execute(self):

        telit_connector = self.sync_telit_connector.telit_le_50_connector
        
        self.update_rf_configuration(self.Name)

        response = RfConfigUpdateResponse(self.Name, True)

        response.Name = self.Name

        if self.DoResetBeforeConfig:
            
            rslt1 = telit_connector.StartConfigMode()

            rslt2 = telit_connector.ResetConfiguration()

            time.sleep(RESET_CONFIG_TIME_SEC)

            rslt3 = telit_connector.EndConfigMode()

            if rslt1 != TelitResponseType.RFAckOk or rslt2 != TelitResponseType.RFAckOk or rslt3 != TelitResponseType.RFAckOk:
                response.Success = False

        rslt = telit_connector.StartConfigMode()
        
        if rslt != TelitResponseType.RFAckOk:

            response.Success = False

        for command in self.Commands:
                        
            rslt = telit_connector.AtsCommnad(command.ATS, command.Value)

            if rslt != TelitResponseType.RFAckOk:

                response.Success = False

            response.add_to_commands(RfConfigResultCommand(strftime("%Y-%m-%d %H:%M:%S", gmtime()), command.ATS, command.Value))

        rslt = telit_connector.EndConfigMode()   
             
        if rslt != TelitResponseType.RFAckOk:

            response.Success = False        


        return response

class RfUnicastRequest(ExecutableRequest):

    def __init__(self, commands):

        self.Commands = commands #RfNewRequestPerCommand
        self.sync_telit_connector = None

    def execute(self):

        config_name = self.get_current_rf_configuration()

        rf_unicast_response = RfUnitsResponse(config_name)

        for cmd in self.Commands:

            for unit_id in cmd.Units:
                  
                global packet_id
                              
                packet_id = (packet_id % 0xFFFF) + 1
                 
                request_chunks = self.sync_telit_connector.send_sync(unit_id, packet_id, cmd.Command)                                

                response_type = FromUnitEndReasonType.Timeout if request_chunks.timeout else FromUnitEndReasonType.LastChunkReceived 

                to_unit_data = ToUnitData(unit_id)
                
                from_unit_data = FromUnitData(unit_id, response_type)

                for chunk in request_chunks.sent_chunks:
                                                            
                    to_unit_data.add_chunk(ToUnitChunk(chunk.time_stamp, base64.b64encode(chunk.payload), chunk.telit_result))
                 
                for chunk in request_chunks.received_chunks:
                                                                                
                    from_unit_data.add_chunk(FromUnitChunk(chunk.time_stamp, abs(chunk.chunck_num), base64.b64encode(chunk.payload), chunk.rssi)) 

                rf_unicast_response.add_to_unit_data(to_unit_data)

                rf_unicast_response.add_from_unit_data(from_unit_data)

        return rf_unicast_response

class RfBoradcastRequest(ExecutableRequest):

    def __init__(self, command, waitForUnitResponse):

        self.Command = command
        self.WaitForUnitResponse = waitForUnitResponse
        self.sync_telit_connector = None

    def execute(self):

        config_name = self.get_current_rf_configuration()

        rf_boradcast_response = RfUnitsResponse(config_name)

        global packet_id

        packet_id = (packet_id % 0xFFFF) + 1
        
        request_chunks = self.sync_telit_connector.send_sync_multicast(packet_id, self.Command)
        
        to_unit_data = ToUnitData(0)

        for chunk in request_chunks.sent_chunks:  
                                                                      
            to_unit_data.add_chunk(ToUnitChunk(chunk.time_stamp, base64.b64encode(chunk.payload), chunk.telit_result))

        rf_boradcast_response.add_to_unit_data(to_unit_data)

        unit_id_to_chunks = {}

        for chunk in request_chunks.received_chunks:
            
            if chunk.unit_id in unit_id_to_chunks:

                unit_id_to_chunks[chunk.unit_id].append(chunk)

            else:

                unit_id_to_chunks[chunk.unit_id] = [chunk]

        for uid in unit_id_to_chunks:

            sorted_chunks = sorted(unit_id_to_chunks[uid], key=lambda chunk: chunk.chunck_num)

            response_type = FromUnitEndReasonType.Timeout if sorted_chunks[0].chunck_num > 0 else FromUnitEndReasonType.LastChunkReceived
            
            from_unit_data = FromUnitData(uid, response_type)
            
            for chunk in sorted_chunks:

                from_unit_data.add_chunk(FromUnitChunk(chunk.time_stamp, abs(chunk.chunck_num), base64.b64encode(chunk.payload), chunk.rssi)) 

            rf_boradcast_response.add_from_unit_data(from_unit_data)
        
        return rf_boradcast_response

class RfNewRequestPerCommand:

    def __init__(self, command, units):

        self.Command= command 
        self.Units = units

class RfConfigCommand:

    def __init__(self, ats, value):

        self.ATS= ats
        self.Value = value

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
