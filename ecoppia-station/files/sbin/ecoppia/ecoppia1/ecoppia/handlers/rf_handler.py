#import os
#import os.path
#from os import listdir
#from os.path import isfile, join
#import json
#import base64
#import sys
#from ecoppia.globals import *
#import socket
#import math
#import time
#import select
#import struct
#from struct import *
#import traceback
#from exceptions import *
#from ecoppia.lib.package_info import *
#from ecoppia.lib.propery_change_info import *
#from ecoppia.connectors.rf_connector import *
##from ecoppia.connectors.rf_demo_connector import *

#TX_PACKET_LENGTH = 12
#RX_PACKET_LENGTH = 18

#RX_APP_PACKET_FIRST_IDX = 3
#RX_APP_PACKET_LAST_IDX = -4

#RX_PACKET_OFFSET = 3
#RX_PACKET_UNIT_ID_IDX = RX_PACKET_OFFSET 
#RX_PACKET_UNIT_ID_LEN = 2
#RX_PACKET_PACKET_ID_IDX = RX_PACKET_OFFSET+2 
#RX_PACKET_PACKET_ID_LEN = 2
#RX_PACKET_RESPONSE_CODE_IDX = RX_PACKET_OFFSET+4 
#RX_PACKET_RESPONSE_CODE_LEN = 1
#RX_PACKET_PAYLOAD_LEN_IDX = RX_PACKET_OFFSET+11 
#RX_PACKET_PAYLOAD_LEN_LEN = 1
#RX_PACKET_RSSI_IDX = -2 
#RX_PACKET_RSSI_LEN = 1


#RX_OLD_PACKET_LENGTH = 14
#RX_OLD_PACKET_OFFSET = 3
#RX_OLD_PACKET_UNIT_ID_IDX = RX_PACKET_OFFSET 
#RX_OLD_PACKET_UNIT_ID_LEN = 2
#RX_OLD_PACKET_COMMAND_IDX = RX_PACKET_OFFSET + 2 
#RX_OLD_PACKET_COMMAND_LEN = 2
#RX_OLD_PACKET_PACKET_ID_IDX = RX_PACKET_OFFSET + 4  
#RX_OLD_PACKET_PACKET_ID_LEN = 2
#RX_OLD_PACKET_BATTERY_IDX = RX_PACKET_OFFSET + 6  
#RX_OLD_PACKET_BATTERY_LEN = 1
#RX_OLD_PACKET_STATE_IDX = RX_PACKET_OFFSET + 7  
#RX_OLD_PACKET_STATE_LEN = 1


#UNIT_CONFIG_LENGTH = 183

#UNIT_CONFIG_MANUFACTORY_ID_IDX = 0
#UNIT_CONFIG_MANUFACTORY_ID_LEN = 8
#UNIT_CONFIG_TELIT_ID_IDX = 130 - UNIT_CONFIG_MANUFACTORY_ID_LEN
#UNIT_CONFIG_TELIT_ID_LEN = 2

#RF_READ_TIMEOUT_IN_SEC = 3




#class RfUnitCommand: 
#    rfPacketId = 0

#    def __init__(self, command, rfUnitId, targetUnitId):
#        RfUnitCommand.rfPacketId = (RfUnitCommand.rfPacketId + 1) % ((1<<16) - 1)
#        self.PacketId = RfUnitCommand.rfPacketId
#        self.Command = command
#        self.RfUnitId = rfUnitId
#        self.TargetUnitId = targetUnitId

#    def buildBaseRFCommand(self):                  
#        b = bytearray()                     
#        return b

#    def getCommandName(self):
#        return ""

#    def __str__(self):
#        return ""


#class RfOldUnitCommand(RfUnitCommand):

#    def __init__(self, command, rfUnitId, targetUnitId):
#        RfUnitCommand.__init__(self, command, rfUnitId, targetUnitId)
#        self.CommandName = self.getCommandName()

#    def buildBaseRFCommand(self):        
          
#        b = bytearray()                     
#        b.extend(pack('>H', self.RfUnitId))
#        b.extend('=')
#        b.extend(pack('>H', self.TargetUnitId))
#        b.extend(pack('>H', self.Command))
#        b.extend(pack('>H', self.PacketId))
#        #state
#        b.extend(pack('B', 0)) 
#        #battery      
#        b.extend(pack('B', 0)) 

#        b.extend('\r')
#        return b

#    def getCommandName(self):
#        if self.Command == 0x81:
#            return 'START_CLEAN'
#        elif self.Command == 0x82:
#            return 'STOP_CLEAN'
#        elif self.Command == 0x84:
#            return 'GET_UNIT_STATE'     
#        elif self.Command == 0x85:
#            return 'START_MAINTENANCE'    
#        elif self.Command == 0x86:
#            return 'END_MAINTENANCE'
#        else:
#            return 'UnIdentified Command ({val})'.format(val = hex(self.Command))

#    def __str__(self):
#        return(self.getCommandName()+"  "+"".join("\\x%02x" % i for i in self.buildBaseRFCommand()))





#class RfStandartUnitCommand(RfUnitCommand): 
        
#    def __init__(self, command, rfUnitId, targetUnitId, payload):

#        RfUnitCommand.__init__(self, command, rfUnitId, targetUnitId)
#        self.CommandName = self.getCommandName()
#        self.Payload = payload

#    def buildBaseRFCommand(self):        
          
#        b = bytearray()                     
#        b.extend(pack('>H', self.RfUnitId))
#        b.extend('=')
#        b.extend(pack('>H', self.TargetUnitId))
#        b.extend(pack('>H', self.PacketId))
#        b.extend(pack('B', self.Command))
#        b.extend(major_unit_version)
#        b.extend(minor_unit_version)
#        b.extend(pack('B', len(self.Payload)))
#        b.extend(self.Payload)
#        b.extend('\r')
#        return b

#    def getCommandName(self):
#        if self.Command == 0x81:
#            return 'START_CLEAN'
#        elif self.Command == 0x82:
#            return 'STOP_CLEAN'
#        elif self.Command == 0x84:
#            return 'GET_UNIT_STATE'     
#        elif self.Command == 0x85:
#            return 'START_MAINTENANCE'    
#        elif self.Command == 0x86:
#            return 'END_MAINTENANCE'
#        elif self.Command == 0x88:
#            return 'SET_CONFIGURATION'
#        elif self.Command == 0x89:
#            return 'GET_CONFIGURATION'
#        elif self.Command == 0x8A:
#            return 'GET_UNIQUE_ID'
#        elif self.Command == 0x8B:
#            return 'SET_TELIT_ID'
#        elif self.Command == 0x8C:
#            return 'SET_CONFIG_AND_CLEAN'
#        else:
#            return 'UnIdentified Command ({val})'.format(val = hex(self.Command))

#    def __str__(self):
#        return(self.getCommandName()+"  "+"".join("\\x%02x" % i for i in self.buildBaseRFCommand()))


#class RfStationCommand: 
#    def __init__(self, command):
#        self.Command = command

#    def buildBaseRFCommand(self):       
#        return self.Command

#    def __str__(self):
#        return self.Command

#class RfUnitResultData:

#    def __init__(self, data):

#        self.FullRawData = bytearray()
#        self.UnitId = None        
#        self.PacketId = None
#        self.AppData = bytearray()
#        self.Payload = bytearray()
#        self.RSSI = 0

#        if((data is not None) and (len(data) > 0)):
#            self.FullRawData = bytearray(data)
#            self.UnitId = struct.unpack('>H', str(self.FullRawData[RX_PACKET_UNIT_ID_IDX : RX_PACKET_UNIT_ID_IDX + RX_PACKET_UNIT_ID_LEN]))[0]
#            self.PacketId = struct.unpack('>H', str(self.FullRawData[RX_PACKET_PACKET_ID_IDX : RX_PACKET_PACKET_ID_IDX + RX_PACKET_PACKET_ID_LEN]))[0]
#            self.AppData = self.FullRawData[RX_PACKET_RESPONSE_CODE_IDX : RX_PACKET_PAYLOAD_LEN_IDX]
#            self.Payload = self.FullRawData[RX_PACKET_PAYLOAD_LEN_IDX + 1: RX_PACKET_PAYLOAD_LEN_IDX + self.FullRawData[RX_PACKET_PAYLOAD_LEN_IDX] +1]
#            self.RSSI = struct.unpack('B', str(self.FullRawData[RX_PACKET_RSSI_IDX : RX_PACKET_RSSI_IDX + RX_PACKET_RSSI_LEN]))[0] 

#    def __str__(self):

#        binfo = bytearray(self.FullRawData)
#        return("".join("\\x%02x" % i for i in binfo))
   


#class RfOldUnitResultData:

#    def __init__(self, data):

#        self.FullRawData = bytearray()
#        self.UnitId = 0        
#        self.PacketId = 0
#        self.Command = 0
#        self.Battery = 0
#        self.State = 0
#        self.RSSI = 0

#        if((data is not None) and (len(data) > 0)):
#            self.FullRawData = bytearray(data)
#            self.UnitId = struct.unpack('>H', str(self.FullRawData[RX_OLD_PACKET_UNIT_ID_IDX : RX_OLD_PACKET_UNIT_ID_IDX + RX_OLD_PACKET_UNIT_ID_LEN]))[0]
#            self.Command = struct.unpack('>H', str(self.FullRawData[RX_OLD_PACKET_COMMAND_IDX : RX_OLD_PACKET_COMMAND_IDX + RX_OLD_PACKET_COMMAND_LEN]))[0]
#            self.PacketId = struct.unpack('>H', str(self.FullRawData[RX_OLD_PACKET_PACKET_ID_IDX : RX_OLD_PACKET_PACKET_ID_IDX + RX_OLD_PACKET_PACKET_ID_LEN]))[0]
#            self.Battery = struct.unpack('B', str(self.FullRawData[RX_OLD_PACKET_BATTERY_IDX : RX_OLD_PACKET_BATTERY_IDX + RX_OLD_PACKET_BATTERY_LEN]))[0]            
#            self.State = struct.unpack('B', str(self.FullRawData[RX_OLD_PACKET_STATE_IDX : RX_OLD_PACKET_STATE_IDX + RX_OLD_PACKET_STATE_LEN]))[0]            
#            self.RSSI = struct.unpack('B', str(self.FullRawData[RX_PACKET_RSSI_IDX : RX_PACKET_RSSI_IDX + RX_PACKET_RSSI_LEN]))[0] 

#    def __str__(self):

#        binfo = bytearray(self.FullRawData)
#        return("".join("\\x%02x" % i for i in binfo))




#class RfOldUnitResult:
#    def __init__(self, cmd, unit, type, data = b''):
#        self.Command = cmd
#        self.UnitId = unit
#        self.ResultType = type
#        self.ResultTypeName = RFResponsePayloadType.getName(self.ResultType)
#        self.Result = RfOldUnitResultData(data)

#class RfUnitResult:
#    def __init__(self, cmd, unit, type, data = b''):
#        self.Command = cmd
#        self.UnitId = unit
#        self.ResultType = type
#        self.ResultTypeName = RFResponsePayloadType.getName(self.ResultType)
#        self.Result = RfUnitResultData(data)


#class RfUnitsResults:
#    def __init__(self, cmd, type , rawDataList):
#        self.Command = cmd
#        self.ResultType = type
#        self.ResultTypeName = RFResponsePayloadType.getName(self.ResultType)
#        self.Results = []
#        for d in rawDataList:
#            self.Results.append(RfUnitResultData(d))

#class RfResult:
#    def __init__(self, cmd, type):
#        self.Command = cmd
#        self.ResultType = type
#        self.ResultTypeName = RFResponsePayloadType.getName(self.ResultType)
        


#class RFHandler:

#    def __init__(self, hardResetFacilitator):      
#        self.server_in_types = [SmartStPkgType.RFCommand]
#        self.property_types = [PropertyType.RFConfig]
#        self.server_context = None
#        self.shadow_context = None

#        self.rf_in_types = [SmartStPkgType.RFResponse]
#        try:
#            #self.rf_context = RFConnector(self)
#            self.rf_context = RFDemoConnector(self)
#        except Exception:          
#            app_log.error("RFConnector could't be created ! error = {err}".format(err = str(traceback.format_exc())))
#            self.rf_context = None
#            raise
#        try:            
#            self.rf_context.connect(RF_READ_TIMEOUT_IN_SEC)
#        except Exception:           
#            app_log.error("RFConnector connect failed ! error = {err}".format(err = str(traceback.format_exc())))
#            self.rf_context = None
#            raise

#        self.buffer = bytearray()
#        self.ok_buf = bytearray(b"OK\r")
#        self.error_buf = bytearray(b"ERROR\r")

#        self.hardResetFacilitator = hardResetFacilitator
#        self.rfResponseTypeAndSequenceCount = (RFResponsePayloadType.RFResponseOk, 0)

#    def setServerContext(self, context):
#        self.server_context = context

#    def setShadowContext(self, context):
#        self.shadow_context = context

#    def setRFContext(self, context):
#        self.rf_context = context

#    def hardResetRequired(self, rfResponseType):

#        self.rfResponseTypeAndSequenceCount = (rfResponseType, self.rfResponseTypeAndSequenceCount[1] + 1) if self.rfResponseTypeAndSequenceCount[0] == rfResponseType else (rfResponseType, 1)  
                
#        if self.rfResponseTypeAndSequenceCount[0] == RFResponsePayloadType.RFNoTelitAck:
#            app_log.debug("Hard Reset Required ? "+RFResponsePayloadType.getName(self.rfResponseTypeAndSequenceCount[0])+" => "+str(self.rfResponseTypeAndSequenceCount[1])+" out of possible "+str(TOTAL_SEQUENTIAL_ACK_TIMEOUTS_BEFORE_HARD_RESET))
              
#        return True if self.rfResponseTypeAndSequenceCount[0] == RFResponsePayloadType.RFNoTelitAck and self.rfResponseTypeAndSequenceCount[1] >= TOTAL_SEQUENTIAL_ACK_TIMEOUTS_BEFORE_HARD_RESET else False
            

#    def wait2status(self):
#        status = None
#        while(True):

#            if not ((self.ok_buf.startswith(self.buffer) or self.buffer.startswith(self.ok_buf) or self.error_buf.startswith(self.buffer) or self.buffer.startswith(self.error_buf))) and len(self.buffer) > 0:
#                if(len(self.buffer) > 0):
#                    app_log.debug("in RF Handler wait2status , invalid buffer [{buffer}] is ignored".format(buffer = str(self.buffer)))
#                raise BufferError()
#            elif self.buffer.startswith(self.ok_buf):
#                del self.buffer[0:len(self.ok_buf)]
#                status = str(self.ok_buf)
#                break          
#            elif self.buffer.startswith(self.error_buf):
#                del self.buffer[0:len(self.error_buf)]
#                status = str(self.error_buf)
#                break

#            data = self.rf_context.doReceive()  
#            if len(data) == 0:
#                if(len(self.buffer) > 0):
#                    app_log.debug("in RF Handler wait2status received 0 bytes, buffer [{buffer}] is ignored".format(buffer = str(self.buffer)))
#                raise IOError("in RF Handler wait2status, socket read 0 bytes")          
#            self.buffer.extend(data)

#        return status


#    def readSingleRXPkg(self, pkgPayload, isBroadcast):
#        info = None
#        payloadlen = 0
#        pp = bytearray()
#        pp.extend(pkgPayload)

#        itr = 0

#        while(True):                

#            # DEBUG
#            itr+= 1
#            hxbfr = "".join("\\x%02x" % i for i in self.buffer)
#            app_log.debug("in RF Handler readSingleRXPkg Iteration {iteration} , Buffer = {buffer} , Buffer Length = {length}".format(iteration = str(itr), buffer = hxbfr, length = str(len(self.buffer))))

#            if len(self.buffer) >= RX_PACKET_LENGTH:

#                if  (isBroadcast or (not isBroadcast and pp[3] == self.buffer[3] and pp[4] == self.buffer[4])) and self.buffer[2] == 0x3D: 
                    
#                    payloadlen = self.buffer[14]

#                    while(True):
#                        if len(self.buffer) >= RX_PACKET_LENGTH + payloadlen:

#                            if self.buffer[RX_PACKET_LENGTH + payloadlen - 3] == 0xD and self.buffer[RX_PACKET_LENGTH + payloadlen -1] == 0xD:
                    
#                                info = self.buffer[0:RX_PACKET_LENGTH + payloadlen]                                      
#                                del self.buffer[0:RX_PACKET_LENGTH + payloadlen]
#                                return info

#                            else:
#                                if(len(self.buffer) > 0):
#                                    app_log.debug("in RF Handler readSingleRXPkg , invalid buffer [{buffer}] is ignored".format(buffer = str(self.buffer))) 
#                                raise BufferError()

#                        data = self.rf_context.doReceive()    
#                        if len(data) == 0:
#                            if(len(self.buffer) > 0):
#                                app_log.debug("in RF Handler readSingleRXPkg received 0 bytes, buffer [{buffer}] is ignored".format(buffer = str(self.buffer)))
#                            raise IOError("in RF Handler readSingleRXPkg, empty buffer in socket read")          
#                        self.buffer.extend(data)

#                else: 
#                    raise BufferError()                            

#            data = self.rf_context.doReceive() 
               
#            if len(data) == 0:
#                if(len(self.buffer) > 0):
#                    app_log.debug("in RF Handler readSingleRXPkg received 0 bytes, buffer [{buffer}] is ignored".format(buffer = str(self.buffer)))
#                raise IOError("in RF Handler readSingleRXPkg, empty buffer in socket read") 
                      
#            self.buffer.extend(data)



#    def readOldSingleRXPkg(self, pkgPayload):
#        info = None
#        pp = bytearray()
#        pp.extend(pkgPayload)

#        while(True):

#            if len(self.buffer) >= RX_OLD_PACKET_LENGTH: 

#                if  pp[0] == pp[3] == self.buffer[0] == self.buffer[3] and pp[1] == pp[4] == self.buffer[1] == self.buffer[4] and self.buffer[2] == 0x3D and self.buffer[11] == 0xD and self.buffer[13] == 0xD:
                    
#                    info = self.buffer[0:RX_OLD_PACKET_LENGTH]
#                    del self.buffer[0:RX_OLD_PACKET_LENGTH]
#                    return info

#                else:
                                         
#                    raise BufferError()                            

#            data = self.rf_context.doReceive()    
#            if len(data) == 0:
#                raise IOError("in RF Handler wait2info, empty buffer in socket read")          
#            self.buffer.extend(data)






#    def wait2info(self, pkgPayload):
#        return self.readSingleRXPkg(pkgPayload, False)

#    def wait2oldInfo(self, pkgPayload):
#        return self.readOldSingleRXPkg(pkgPayload)

#    def wait2broadcast(self, pkgPayload):
#        infos = []
#        try:
#            while(True):
#                info = self.readSingleRXPkg(pkgPayload, True)
#                infos.append(info);

#        #except socket.timeout:

#        except Exception as e:
#            if(len(self.buffer) > 0):
#                app_log.error("In RF Handler wait2broadcast Exception Caught And Buffer Holds Invalid Tail , {err}".format(err = str(traceback.format_exc())))
#                return []
            
#        app_log.debug("In RF Handler wait2broadcast Completed Successfully")
#        return infos


          



#    def sendRf(self, cmd):

#        self.rf_context.flushAll()
        
#        self.rf_context.doSend(cmd.buildBaseRFCommand())    
        
#        del self.buffer[:]

        
#        dtype = None     
         
#        try:
#            status = self.wait2status()

#        except Exception:            
#            dtype = RFResponsePayloadType.RFNoTelitAck 
#            app_log.debug("RFNoTelitAck {data}".format(data = str(cmd))) 
                                  
#        else:
#            if status == "OK\r":
#                dtype = RFResponsePayloadType.RFResponseOk
#                app_log.debug("RFResponseOk From St. {data}".format(data = str(cmd)))

#            elif status == "ERROR\r":
#                dtype = RFResponsePayloadType.RFError
#                app_log.debug("RFError {data}".format(data = str(cmd)))

#        if self.hardResetRequired(dtype):
#            self.hardResetFacilitator.DoHardReset()

#        return RfResult(cmd, dtype) 


#    def sendRfAndWaitToSingleResponse(self, cmd):
#        swsr = None
#        info = None

#        sr = self.sendRf(cmd)
#        if(sr.ResultType == RFResponsePayloadType.RFResponseOk):
#            try:
#                info = self.wait2info(cmd.buildBaseRFCommand())
#            except Exception:
#                swsr = RfUnitResult(cmd, cmd.TargetUnitId, RFResponsePayloadType.RFTimeout)

#                app_log.debug("RFTimeout ({command_name}) Unit:{unit_id}".format(command_name = swsr.Command.CommandName, unit_id = swsr.Command.TargetUnitId))
#            else:
#                swsr = RfUnitResult(cmd, cmd.TargetUnitId, RFResponsePayloadType.RFResponseOk, info)
                       
#                if(swsr.Result.PacketId <> swsr.Command.PacketId):
#                    raise Exception("Received Invalid Packet Id Expect: "+swsr.Command.PacketId+" Received: "+swsr.Result.PacketId)

#                elif(swsr.Result.UnitId <> swsr.Command.TargetUnitId):
#                    raise Exception("Received Invalid Unit Id Expect: "+swsr.Command.TargetUnitId+" Received: "+swsr.Result.UnitId)

#                app_log.debug("RFResponseOk ({command_name}) {sinfo}".format(command_name = swsr.Command.CommandName, sinfo = str(swsr.Result)))
#        else:
#            swsr = RfUnitResult(cmd, cmd.TargetUnitId, sr.ResultType)

#            app_log.debug("{rf_response} ({command_name}) Unit:{unit_id}".format(rf_response = swsr.ResultTypeName ,command_name = swsr.Command.CommandName, unit_id = swsr.Command.TargetUnitId))                             
         
#        if(len(self.buffer) > 0):
#            app_log.debug("Invalid Tail Buffer [{buffer}] Is Ignored".format(buffer = str(self.buffer))) 
                                    
#        return swsr


#    def sendOldRfAndWaitToSingleResponse(self, cmd):
#        swsr = None
#        info = None

#        sr = self.sendRf(cmd)

#        if(sr.ResultType == RFResponsePayloadType.RFResponseOk):
#            try:
#                info = self.wait2oldInfo(cmd.buildBaseRFCommand())
#            except Exception:
#                swsr = RfOldUnitResult(cmd, cmd.TargetUnitId, RFResponsePayloadType.RFTimeout)

#                app_log.debug("RFTimeout ({command_name}) Unit:{unit_id}".format(command_name = swsr.Command.CommandName, unit_id = swsr.Command.TargetUnitId))
#            else:
#                swsr = RfOldUnitResult(cmd, cmd.TargetUnitId, RFResponsePayloadType.RFResponseOk, info)
                       
#                if(swsr.Result.PacketId <> swsr.Command.PacketId):
#                    raise Exception("Received Invalid Packet Id Expect: "+swsr.Command.PacketId+" Received: "+swsr.Result.PacketId)

#                elif(swsr.Result.UnitId <> swsr.Command.TargetUnitId):
#                    raise Exception("Received Invalid Unit Id Expect: "+swsr.Command.TargetUnitId+" Received: "+swsr.Result.UnitId)

#                app_log.debug("RFResponseOk ({command_name}) {sinfo}".format(command_name = swsr.Command.CommandName, sinfo = str(swsr.Result)))
#        else:
#            swsr = RfOldUnitResult(cmd, cmd.TargetUnitId, sr.ResultType)

#            app_log.debug("{rf_response} ({command_name}) Unit:{unit_id}".format(rf_response = swsr.ResultTypeName ,command_name = swsr.Command.CommandName, unit_id = swsr.Command.TargetUnitId))                             
         
#        if(len(self.buffer) > 0):
#            app_log.debug("Invalid Tail Buffer [{buffer}] Is Ignored".format(buffer = str(self.buffer))) 
                                    
#        return swsr




#    def sendRfAndWaitToMultipleResponses(self, cmd):
#        swmr = None

#        sr = self.sendRf(cmd)
#        if(sr.ResultType == RFResponsePayloadType.RFResponseOk):

#            infos = self.wait2broadcast(cmd.buildBaseRFCommand())
#            swmr = RfUnitsResults(cmd, RFResponsePayloadType.RFResponseOk, infos)

#            for rslt in swmr.Results:
#                if(rslt.PacketId <> swmr.Command.PacketId):
#                    raise Exception("Received Invalid Packet Id Expect: "+swmr.Command.PacketId+" Received: "+rslt.PacketId)
                 
#        else:
#            swmr = RfUnitsResults(cmd, sr.ResultType, [])

#        for rslt in swmr.Results:
#            app_log.debug("RFResponseOk ({command_name}) {sinfo}".format(command_name = swmr.Command.CommandName, sinfo = str(rslt)))

#        if(len(self.buffer) > 0):
#            app_log.debug("Invalid Tail Buffer [{buffer}] Is Ignored".format(buffer = str(self.buffer))) 

#        return swmr

        

#    def extractJsonCommands(self, obj):

#        cmdslist = []
#        if(obj['Type'] == SmartStRFGroup.SimpleUnitCommand):

#            cmds = []
#            cmds.extend(obj['Commands'])
#            for cmd in cmds:
#                for unitId in cmd['Units']:
#                    cmdslist.append( RfStandartUnitCommand(cmd['Command'], unitId, unitId, bytearray()))

#        elif(obj['Type'] == SmartStRFGroup.OldUnitCommand):

#            cmds = []
#            cmds.extend(obj['Commands'])
#            for cmd in cmds:
#                for unitId in cmd['Units']:
#                    cmdslist.append( RfOldUnitCommand(cmd['Command'], unitId, unitId))

#        elif(obj['Type'] == SmartStRFGroup.HandShakeUnitCommand):
                     
#            for unit in obj['Units']:
#                cmdslist.append( RfStandartUnitCommand(obj['Command'], 0, unit[0], bytearray(unit[1], 'utf-8')))

#        elif(obj['Type'] == SmartStRFGroup.ConfigUnitCommand):

#            Command = obj['Command']
             
#            for cfg in obj['Configurations']:
                                
#                ucfg = base64.b64decode(cfg['Config']) 
                                   
#                for unit in cfg['Units']:
#                    b = bytearray()
#                    b.extend(unit[1])
#                    b.extend(ucfg[0 : UNIT_CONFIG_TELIT_ID_IDX])
#                    b.extend(pack('<H', unit[0]))
#                    b.extend(ucfg[UNIT_CONFIG_TELIT_ID_IDX :])

#                    cmdslist.append(RfStandartUnitCommand(Command, unit[0], unit[0], b))

#                    #DEBUG
#                    app_log.info("Config Command Created ! Unique ID:{uniqueid} Unit ID:{unitid} Config Length:{configlen}".format(uniqueid = str(unit[1]), unitid = str(unit[0]), configlen = len(b)))      
#                    debugarr = bytearray()
#                    debugarr.extend(pack('<H', unit[0]))
#                    app_log.info("Packed Unit ID: {puid}".format(puid = "".join("\\x%02x" % i for i in debugarr)))
#                    app_log.info("Full Configuration: {fullconfig}".format(fullconfig = "".join("\\x%02x" % i for i in b)))


#        elif(obj['Type'] == SmartStRFGroup.BroadcastUnitCommand):

#            cmdslist.append(RfStandartUnitCommand(obj['Command'], 0, 0, bytearray()))

#        elif(obj['Type'] == SmartStRFGroup.ConfigStationCommand):
#            # obj is a list
#            for cmd in obj['Commands']:
#                cmdslist.append(RfStationCommand(cmd))

#        return cmdslist
            
#    def processPropertyChange(self, pkgInfo):
#        rfCmds = [RfStationCommand('+++')];
#        for cmd in pkgInfo.payload:
#            rfCmds.append(RfStationCommand(cmd + '\r'))
#        rfCmds.append(RfStationCommand('ATO\r'));

#        sendSuccess = True
#        for cmd in rfCmds:
#            app_log.info("sendRf {command}".format(command = str(cmd))) 
#            rslt = self.sendRf(cmd) 
#            if rslt.ResultType != RFResponsePayloadType.RFResponseOk:
#                sendSuccess = False
#                break                              

#        if sendSuccess: 
#            self.shadow_context.doReportState(pkgInfo.type, pkgInfo.payload)

#    def processServerPackage(self, pkgInfo):

#        # Publish RF Command Ack for every received RF command
#        # This feature is crucial in havily time consuming commands  
#        # where immidiate ack confirmation is neccessary on master side 
#        ackPkg = PackageInfo(SmartStPkgType.RFCommandAck, '', pkgInfo.sessionid)
#        self.server_context.doSendPkg(ackPkg)

#        resultList = []
#        rsltPkg = PackageInfo(SmartStPkgType.RFResponse, '', pkgInfo.sessionid)

#        jsonObj = json.loads(pkgInfo.payload, object_hook = decode_dict)
        
#        if(jsonObj['Type'] == SmartStRFGroup.SimpleUnitCommand or jsonObj['Type'] == SmartStRFGroup.HandShakeUnitCommand or jsonObj['Type'] == SmartStRFGroup.ConfigUnitCommand):            

#            rfCmds = self.extractJsonCommands(jsonObj)
#            for cmd in rfCmds:
#                app_log.info("sendRfAndWaitToSingleResponse {command}".format(command = str(cmd))) 
#                rslt = self.sendRfAndWaitToSingleResponse(cmd)                                
#                resultList.append((rslt.UnitId, rslt.ResultType , base64.b64encode(rslt.Result.AppData), base64.b64encode(rslt.Result.Payload), rslt.Result.RSSI))

#            rsltPkg.payload = json.dumps(resultList)               
#            self.server_context.doSendPkg(rsltPkg)

#        elif(jsonObj['Type'] == SmartStRFGroup.BroadcastUnitCommand):            

#            rfCmds = self.extractJsonCommands(jsonObj)
#            for cmd in rfCmds:
#                app_log.info("sendRfAndWaitToMultipleResponses {command}".format(command = str(cmd))) 
#                rslts = self.sendRfAndWaitToMultipleResponses(cmd)      
#                for rslt in rslts.Results:                          
#                    resultList.append((rslt.UnitId, rslts.ResultType, base64.b64encode(rslt.AppData), base64.b64encode(rslt.Payload), rslt.RSSI))

#            rsltPkg.payload = json.dumps(resultList)               
#            self.server_context.doSendPkg(rsltPkg)


#        elif(jsonObj['Type'] == SmartStRFGroup.ConfigStationCommand):            

#            rfCmds = self.extractJsonCommands(jsonObj)
#            for cmd in rfCmds:
#                app_log.info("sendRf {command}".format(command = str(cmd))) 
#                rslt = self.sendRf(cmd)                               
#                resultList.append({"ResponseType": rslt.ResultType, "Command": str(rslt.Command)})

#            rsltPkg.payload = json.dumps(resultList)               
#            self.server_context.doSendPkg(rsltPkg)

#        elif(jsonObj['Type'] == SmartStRFGroup.OldUnitCommand):            

#            rfCmds = self.extractJsonCommands(jsonObj)             
#            for cmd in rfCmds:
#                app_log.info("sendOldRfAndWaitToSingleResponse {command}".format(command = str(cmd)))                 
#                rslt = self.sendOldRfAndWaitToSingleResponse(cmd)                                                               
#                resultList.append((rslt.UnitId, rslt.ResultType , rslt.Result.Command, rslt.Result.State, rslt.Result.Battery, rslt.Result.RSSI))

#            rsltPkg.payload = json.dumps(resultList)                           
#            self.server_context.doSendPkg(rsltPkg)



