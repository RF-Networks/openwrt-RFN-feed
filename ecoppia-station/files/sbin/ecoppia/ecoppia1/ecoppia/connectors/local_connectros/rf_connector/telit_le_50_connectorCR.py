import logging
import datetime
import socket
import time
import traceback
import serial
import copy

from struct import *
from threading import Thread
from exceptions import *
from threading import Event
from rx.subjects import *
from rx import Observable, Observer

from ecoppia.globals import *
from ecoppia.lib.package_info import *
from ecoppia.lib.crc16 import *

from serial_connector import RfConnector
DEFAULT_PORT = "/dev/ttyS1"
#when you run on  Computer Serial port 
#DEFAULT_PORT = "COM13"
#from tcp_connector import RfConnector
#DEFAULT_PORT = "192.168.131.15"

RF_READ_TIMEOUT_IN_SEC = 10
RF_WRITE_TIMEOUT_IN_SEC = 3
TELIT_ACK_TIMEOUT_IN_SEC = 10


TELIT_MAX_MSG_LEN = 100 #254
SLEEP_AFTER_EXCEPTION_IN_SEC = 5

UART_BOUDRATE = 19200

TELIT_CR = '\r'
TELIT_ACK_OK = 'OK' + TELIT_CR
TELIT_ACK_ERROR = 'ERROR' + TELIT_CR

def to_hex(str):
    res = ' '.join("{:02X}".format(ord(x)) for x in str)
    return res

class MatchType:
    Handled = "Handled"
    Mismatched = "Mismatched"
    Incompleted = "Incompleted"

class TelitLE50ConnectorCR():

    def __init__(self, reset_facilitator, port=DEFAULT_PORT):
        self.is_old_protocol = False
        self.reset_facilitator = reset_facilitator
        self.crc16_calculator = CRC16()
        self.rf_connector = RfConnector()        
        self.rf_connector.connect(RF_READ_TIMEOUT_IN_SEC, RF_WRITE_TIMEOUT_IN_SEC, UART_BOUDRATE, port)
        self.telit_ack_timeout_counter = 0
        self.telit_ack = None
        self.telit_ack_event = Event()
        self.rx_thread = Thread(target = self.telit_rx_monitoring)
        self.rx_thread.start()      
        self.rx_msg_subject = Subject()
        self.buffer = ''
        self.Command = ''

    def validate_crc(self, data, crc):

        return self.crc16_calculator.calculate(data) == crc

    #@staticmethod
    def telit_rx_monitoring(self):
        buf = ''
        self.buffer = ''

        telit_protocol_header_size = 3
        telit_protocol_header_end_idx = 2
        st_protocol_header_size = 5
        st_protocol_payload_len = -1
        st_protocol_packet_id_idx = 3
        st_protocol_packet_id_size = 2
        st_protocol_chunck_num_idx = 5
        st_protocol_chunck_num_size = 2
        st_protocol_payload_len_idx = 7
        st_protocol_payload_start_idx = telit_protocol_header_size + st_protocol_header_size
        st_protocol_payload_end_idx = -1
        st_protocol_crc_size = 2
        st_protocol_crc_start_idx = -1
        st_protocol_crc_end_idx = -1
        # rssi + cr
        telit_protocol_cr_size = 1
        telit_protocol_rssi_size = 1
        telit_protocol_suffix_size = telit_protocol_cr_size + telit_protocol_rssi_size + telit_protocol_cr_size
        telit_protocol_suffix_start_idx = -1
        app_log.info("Telit LE50 - RX Monitoring Thread Started ..")

        while True:
            try:
                if len(self.Command) == 0 :
                    continue
                DataRecived = self.rf_connector.doReceiveCR(0.9, TELIT_CR)
                app_log.info("DataRecived : " + str(DataRecived) +" HEX :"+to_hex(DataRecived))

                if DataRecived[0:len(TELIT_ACK_ERROR)] == TELIT_ACK_ERROR:
                    mismatch = MatchType.Handled
                    self.telit_ack = TelitResponseType.RFAckError
                    self.buffer = copy.deepcopy(DataRecived)

                if DataRecived[0:len(TELIT_ACK_OK)] == TELIT_ACK_OK:
                    self.telit_ack = TelitResponseType.RFAckOk
                    if (self.Command[0] == "A" and self.Command[1] == "T" ) or (self.Command[0] == "+" and self.Command[1] == "+"): #TelitCommand
                        mismatch = MatchType.Handled
                        self.buffer = copy.deepcopy(DataRecived)
                        #app_log.info("AT Command ->" +self.buffer )                
                    else :
                        mismatch = MatchType.Incompleted
                        buf = DataRecived
                        while True:
                            Payload = self.rf_connector.doReceiveCR( 0.9,TELIT_CR )
                            app_log.info("1Payload:" +to_hex(Payload))
                            subp_max_len = TELIT_MAX_MSG_LEN - 11
                            chunck_num = 0
                            if len(Payload) > 3:
                                #buf+=b"\x0D" 
                                chunck_num = struct.unpack('<h', Payload[st_protocol_chunck_num_idx : st_protocol_chunck_num_idx + st_protocol_chunck_num_size])[0] 
                                unit_id = struct.unpack('>H', Payload[0:telit_protocol_header_end_idx])[0]
                                packet_id = struct.unpack('>H', Payload[st_protocol_packet_id_idx: st_protocol_packet_id_idx+st_protocol_packet_id_size])[0] 
                                packet_len = struct.unpack('>B', Payload[st_protocol_payload_len_idx])[0]
                                tPayload = ""
                                app_log.info("tPayload INIT icount:" + str(len(Payload) )+ " packet_len: " + str(packet_len ) )
                                while len(tPayload)+(len(Payload)-8) <= packet_len:
                                    tPayload += self.rf_connector.doReceiveCR( 0.1,TELIT_CR )
                                    #app_log.info("tPayload:" + to_hex(tPayload) +"  tPayload len:" + str(len(tPayload))  + " packet_len: " + str(packet_len ) )
                                if( len(tPayload) + len(Payload) == packet_len+11 ) :
                                    Payload += tPayload
                                else :
                                    app_log.info("Need to add :" + str(len(tPayload) + len(Payload) - (packet_len+11) ) ) 
                                    Payload += '\x00' 
                                    Payload += tPayload
                                #app_log.info("unit_id:" + str(unit_id) + " packet_id:" + str(packet_id )+ " chunck_num: " + str(chunck_num ) + " packet_len:" + str(packet_len))
                                #Payload += self.rf_connector.doReceive(packet_len,1)
                                #Payload += self.rf_connector.doReceiveCR( 0.4,TELIT_CR )
                                app_log.info("Payload:" +to_hex(Payload) )
                                subp_max_len = TELIT_MAX_MSG_LEN - 11
                                subp = Payload[st_protocol_header_size+st_protocol_packet_id_idx:st_protocol_header_size+st_protocol_packet_id_idx+st_protocol_chunck_num_size+packet_len]
                                chunck = self.buildCmdChunck(unit_id, packet_id, chunck_num, subp)
                                app_log.info("unit_id:" + str(unit_id) + " packet_id:" + str(packet_id )+ " chunck_num: " + str(chunck_num )+ " subp:" + to_hex(subp) )
                                app_log.info("chunck:" +to_hex(chunck) )
                                buf +=  copy.deepcopy(Payload )
                                ENDTelitprotocol = self.rf_connector.doReceiveCR( 0.9,TELIT_CR )
                                buf+= copy.deepcopy(ENDTelitprotocol) 
                                if buf[-1] != b'0x0d' and buf[-3] != b'0x0d':
                                    app_log.info("chunck : " +str(chunck_num) + " Missing RSSI!!!"  )
                                    app_log.info("RSSI Recived : " + to_hex(ENDTelitprotocol)  )
                                else :
                                    app_log.info("chunck : " +to_hex(Payload) + "  RSSI!!!"  )
                                    buf +=  copy.deepcopy(Payload )
                                    #self.buffer = copy.deepcopy(buf)
                                if chunck_num < 0 :
                                    self.buffer = copy.deepcopy(buf) #+copy.deepcopy(ENDTelitprotocol)
                                    break
                        app_log.info("Unit Command ->" +to_hex(self.buffer ))
                        mismatch = MatchType.Handled

                self.Command = ''
                #app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") -  rx Monitoring Buffer: " + repr(self.buffer))  
                app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") -  rx Monitoring Buffer HEX: " + to_hex(self.buffer))                     
                self.telit_ack_event.set() 
            except Exception:
                # LOG FATAL HERE
                #print "Unexpected error:", sys.exc_info()[0]
                app_log.error("Telit LE50 (PORT: " + self.rf_connector.description + ") - RX Monitoring Thread : " + str(traceback.format_exc()))
                self.buffer = ''
                self.Command = ''
                time.sleep(SLEEP_AFTER_EXCEPTION_IN_SEC)

    def SendTelitMessage(self, msg):
        self.telit_ack_event.clear()
        self.Command = msg
        app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") - Send Message: " + to_hex(msg))
        if len(self.Command) > 5: #ATS26
            app_log.info("Command Direct -> " + self.Command)
            if self.Command.startswith( 'ATS26' ) :
                self.rf_connector.doSend(msg)
                rst=self.rf_connector.doReceiveCR(1,TELIT_CR)
                self.UnitType = "Telit"  if rst == TELIT_ACK_OK else  "Ti" 
                return TELIT_ACK_OK,TELIT_ACK_OK
        if len(self.Command) > 1:
            if (self.Command[0] == "A" and self.Command[1] == "T" ) or (self.Command[0] == "+" and self.Command[1] == "+") :
                self.Command = msg
            else :
                packet_id = struct.unpack('>h', msg[5: 7])[0] 
                #app_log.info("Sended packet_id " + str(packet_id) +" Sended Hex " + str(msg[5: 7]))
                if packet_id > 0 :            
                    self.Command = 'AT'
        self.rf_connector.doSend(msg)

        rslt = None
        if self.telit_ack_event.wait(TELIT_ACK_TIMEOUT_IN_SEC) == True:
            self.telit_ack_timeout_counter = 0
            rslt = self.telit_ack
        else:
            rslt = TelitResponseType.RFAckTimeout
            self.telit_ack_timeout_counter = self.telit_ack_timeout_counter + 1
            if TOTAL_SEQUENTIAL_ACK_TIMEOUTS_BEFORE_HARD_RESET <= self.telit_ack_timeout_counter:
                self.reset_facilitator.DoHardReset()
        rsltBuffer = copy.deepcopy(self.buffer)
        rslt_str = 'RFAckOk' if rslt == TelitResponseType.RFAckOk else 'RFAckError' if rslt == TelitResponseType.RFAckError else 'RFAckTimeout' if rslt == TelitResponseType.RFAckTimeout else ''
        #app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") - Send Message: " + to_hex(msg) + " Result: " + rslt_str + "Result Buffer: " + rsltBuffer)
        return rslt,rsltBuffer
    
    def TelitResponseType_to_strings(self,argument): 
        switcher = { 
            TelitResponseType.RFAckOk: "RFAckOk", 
            TelitResponseType.RFAckError: "RFAckError", 
            TelitResponseType.RFAckTimeout: "RFAckTimeout", 
        } 
        return switcher.get(argument, "") 
    # +++
    def StartConfigMode(self):
        return self.SendTelitMessage("+++")

    # ATO\r
    def EndConfigMode(self):
        return self.SendTelitMessage("ATO\r")


    # ATR\r
    def ResetConfiguration(self):
        return self.SendTelitMessage("ATR\r")

    # ATS{register}={value}/r
    def AtsCommnad(self, register, value):
        return self.SendTelitMessage("ATS" + str(register) + "=" + str(value) + "\r")

    def buildCmdChunck(self, unitId, packet_id, chunck_num, sub_payload):
        if self.is_old_protocol:
            return pack('>H', unitId) + '=' + pack('>H', unitId) + sub_payload + pack('>H', packet_id) + pack('>H', 0)  + '\r'

        else:
            beforeCrc = pack('<H', packet_id) + pack('<h', chunck_num) + pack('B', len(sub_payload)) + sub_payload
            crc = self.crc16_calculator.calculate(beforeCrc)
            return pack('>H', unitId) + '=' + beforeCrc + pack('<H', crc) + '\r'

    def Send(self, unitId, packetId, payload):

        chunks = []

        chunck_num = 0

        subp_max_len = TELIT_MAX_MSG_LEN - 11

        while len(payload) > 0:

            subp = payload[:subp_max_len]

            payload = payload[subp_max_len:]
            
            chunck_num = (chunck_num + 1) * -1 if len(payload) == 0 else chunck_num + 1
     
            chunck = self.buildCmdChunck(unitId, packetId, chunck_num, subp)

            rslt = self.SendTelitMessage(chunck)

            chunks.append(ChunkSendResult(subp, datetime.datetime.now(), rslt))

            if rslt == TelitResponseType.RFAckTimeout or rslt == TelitResponseType.RFAckError:
                break
  
        return chunks

    def SendBrodcast(self, packetId, payload): 
        return Send(0, packetId, payload)


class TelitResponseType:
    RFAckOk = 0
    RFAckError = 1     
    RFAckTimeout = 2  
 
class FromUnitEndReasonType:
    LastChunkReceived = 0
    Timeout = 1   
           
class ChunkMonitored:
    def __init__(self, unit_id, packet_id, chunk_num, payload, rssi):
        self.unit_id = unit_id
        self.packet_id = packet_id
        self.chunk_num = chunk_num
        self.payload = payload
        self.rssi = rssi
        
class ChunkSendResult: 
    def __init__(self, payload, time_stamp, telit_result): 
        self.payload = payload 
        self.time_stamp = time_stamp 
        self.telit_result = telit_result

class ChunkReceiveResult:
    def __init__(self, unit_id, chunck_num, payload, rssi, time_stamp):
        self.unit_id = unit_id 
        self.chunck_num = chunck_num  
        self.payload = payload
        self.rssi = rssi         
        self.time_stamp = time_stamp
                

class ChuncksObserver(Observer):
    def __init__(self):
        self.chuncks_info = []

    def on_next(self, x):
        self.chuncks_info.append((x.chunk_num, x.payload, x.rssi))        

    def on_completed(self):
        pass

    def on_error(self, err):
        pass