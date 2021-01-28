#import logging
#import datetime
#import socket
#import time
#import traceback
#import serial
#from struct import *
#from threading import Thread
#from exceptions import *
#from threading import Event
#from rx.subjects import *
#from rx import Observable, Observer

#from ecoppia.globals import *
#from ecoppia.lib.package_info import *
#from ecoppia.lib.crc16 import *

##from ecoppia.connectors.rf_connector.serial_connector import RfConnector
##DEFAULT_PORT = "/dev/ttyS1"
#from ecoppia.connectors.rf_connector.tcp_connector import RfConnector
#DEFAULT_PORT = "192.168.131.18"

#RF_READ_TIMEOUT_IN_SEC = 1
#RF_WRITE_TIMEOUT_IN_SEC = 1
#TELIT_ACK_TIMEOUT_IN_SEC = 1


#TELIT_MAX_MSG_LEN = 100 #254
#SLEEP_AFTER_EXCEPTION_IN_SEC = 60

#UART_BOUDRATE = 19200

#TELIT_CR = '\r'
#TELIT_ACK_OK = 'OK' + TELIT_CR
#TELIT_ACK_ERROR = 'ERROR' + TELIT_CR

#def to_hex(str):
#    res = ' '.join("{:02X}".format(ord(x)) for x in str)
#    return res

#class MatchType:
#    Handled = "Handled"
#    Mismatched = "Mismatched"
#    Incompleted = "Incompleted"

#class TelitLE50():

#    def __init__(self, port=DEFAULT_PORT):
#        self.crc16_calculator = CRC16()

#        self.rf_connector = RfConnector()        
#        self.rf_connector.connect(RF_READ_TIMEOUT_IN_SEC, RF_WRITE_TIMEOUT_IN_SEC, UART_BOUDRATE, port)
        
#        self.telit_ack = None
#        self.telit_ack_event = Event()

#        self.rx_thread = Thread(target = self.telit_rx_monitoring)
#        self.rx_thread.start()      
                
#        self.rx_msg_subject = Subject()

#    def validate_crc(self, data, crc):

#        return self.crc16_calculator.calculate(data) == crc


#    def telit_rx_monitoring(self):
#        buf = ''
        
#        telit_protocol_header_size = 3
#        telit_protocol_header_end_idx = 2
#        st_protocol_header_size = 5
#        st_protocol_payload_len = -1
#        st_protocol_packet_id_idx = 3
#        st_protocol_packet_id_size = 2
#        st_protocol_chunck_num_idx = 5
#        st_protocol_chunck_num_size = 2
#        st_protocol_payload_len_idx = 7
#        st_protocol_payload_start_idx = telit_protocol_header_size + st_protocol_header_size
#        st_protocol_payload_end_idx = -1
#        st_protocol_crc_size = 2
#        st_protocol_crc_start_idx = -1
#        st_protocol_crc_end_idx = -1
#        # rssi + cr
#        telit_protocol_cr_size = 1
#        telit_protocol_rssi_size = 1
#        telit_protocol_suffix_size = telit_protocol_cr_size + telit_protocol_rssi_size + telit_protocol_cr_size
#        telit_protocol_suffix_start_idx = -1
  
#        app_log.info("Telit LE50 - RX Monitoring Thread Started ..")

#        while True:

#            try:

#                mismatch = MatchType.Mismatched
#                to_read = 3

#                if len(buf) == 0:
#                    mismatch = MatchType.Handled

#                if (mismatch != MatchType.Handled):
#                    if TELIT_ACK_OK.startswith(buf[0:len(TELIT_ACK_OK)]):

#                        if buf[0:len(TELIT_ACK_OK)] == TELIT_ACK_OK:
#                            mismatch = MatchType.Handled
#                            self.telit_ack = TelitResponseType.RFAckOk
#                            self.telit_ack_event.set() 
#                            app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") - Buffer Matched Telit Acknowledgement: " + repr(buf))
#                            buf = buf[len(TELIT_ACK_OK): ]
#                        else:
#                            mismatch = MatchType.Incompleted
#                            to_read = len(TELIT_ACK_OK) - len(buf)
                    
#                if (mismatch != MatchType.Handled):
#                    if TELIT_ACK_ERROR.startswith(buf[0:len(TELIT_ACK_ERROR)]):

#                        if buf[0:len(TELIT_ACK_ERROR)] == TELIT_ACK_ERROR:
#                            mismatch = MatchType.Handled
#                            self.telit_ack = TelitResponseType.RFAckError
#                            self.telit_ack_event.set() 
#                            app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") - Buffer Matched Telit Acknowledgement: " + repr(buf))
#                            buf = buf[len(TELIT_ACK_ERROR): ]
#                        else:
#                            mismatch = MatchType.Incompleted
#                            to_read = len(TELIT_ACK_ERROR) - len(buf)

#                if (mismatch == MatchType.Mismatched):
#                    #station-unit protocol message
#                    unit_id = 0
#                    packet_id = 0
#                    chunck_num = 0
#                    payload = ''
#                    rssi = 0

#                    buf_len = telit_protocol_header_size

#                    if len(buf) < buf_len:
#                        mismatch = MatchType.Incompleted
#                    else:
#                        if buf[telit_protocol_header_end_idx] != '=':
#                            mismatch = MatchType.Mismatched
#                        else:
#                            unit_id = struct.unpack('>H', buf[0:telit_protocol_header_end_idx])[0] 

#                            buf_len += st_protocol_header_size
#                            if len(buf) < buf_len:
#                                mismatch = MatchType.Incompleted
#                            else:
#                                packet_id = struct.unpack('<H', buf[st_protocol_packet_id_idx : st_protocol_packet_id_idx + st_protocol_packet_id_size])[0]  
#                                chunck_num = struct.unpack('<h', buf[st_protocol_chunck_num_idx : st_protocol_chunck_num_idx + st_protocol_chunck_num_size])[0]   
#                                st_protocol_payload_len = struct.unpack('B', buf[st_protocol_payload_len_idx])[0] 
                        
#                                buf_len += st_protocol_payload_len + st_protocol_crc_size
#                                if len(buf) < buf_len:
#                                    mismatch = MatchType.Incompleted
#                                else:
#                                    st_protocol_payload_end_idx = st_protocol_payload_start_idx + st_protocol_payload_len - 1
#                                    st_protocol_crc_start_idx = st_protocol_payload_end_idx + 1
#                                    st_protocol_crc_end_idx = st_protocol_crc_start_idx + st_protocol_crc_size - 1                                                 
                        
#                                    for_crc_vaildation = buf[telit_protocol_header_size : st_protocol_payload_end_idx + 1]
#                                    crc = struct.unpack('<H', buf[st_protocol_crc_start_idx : st_protocol_crc_end_idx + 1])[0]
#                                    if not self.validate_crc(for_crc_vaildation, crc):
#                                        mismatch = MatchType.Mismatched
#                                    else:
#                                        payload = buf[st_protocol_payload_start_idx : st_protocol_payload_end_idx + 1]
                        
#                                        buf_len += telit_protocol_suffix_size
#                                        if len(buf) < buf_len:
#                                            mismatch = MatchType.Incompleted
#                                        else:
#                                            telit_protocol_suffix_start_idx = st_protocol_crc_end_idx + 1
                         
#                                            rssi = struct.unpack('B', buf[telit_protocol_suffix_start_idx + telit_protocol_cr_size])[0]  
#                                            cr = buf[telit_protocol_suffix_start_idx + telit_protocol_cr_size + telit_protocol_rssi_size]

#                                            if cr != TELIT_CR:
#                                                mismatch = MatchType.Mismatched
#                                            else:
#                                                self.rx_msg_subject.on_next(ChunkMonitored(unit_id, packet_id, chunck_num, payload, rssi)) 
#                                                mismatch = MatchType.Handled
#                                                app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") - Buffer Matched Pattern: unit id: " + str(unit_id) + " packet id: " + str(packet_id) + " chunk: " + str(chunck_num) + " buffer: " + to_hex(buf))
#                                                buf = buf[buf_len: ]

#                    if mismatch == MatchType.Incompleted:
#                        to_read = buf_len - len(buf)

                        
#                if (mismatch == MatchType.Mismatched):
#                    app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") Buffer Mismatch: " + to_hex(buf))
#                    buf = buf[1:]
#                    continue

#                # if buffer is empty block forever or until new character is
#                # received otherwise block till timeout or the next character
#                # received
#                time_out = None if len(buf) == 0 else RF_READ_TIMEOUT_IN_SEC

#                app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") before read timeout: " + str(time_out) + ", to_read: " + str(to_read))
#                ch = self.rf_connector.doReceive(to_read, time_out)
#                app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") doReceive: " + to_hex(ch))
                
#                if len(ch) >= 1:
#                    buf = buf + ch  
#                else:
#                    app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") - Timeout in rx Monitoring Buffer: " + repr(buf))                     
#                    buf = ''

                

#            except Exception:
#                # LOG FATAL HERE
#                #print "Unexpected error:", sys.exc_info()[0]
#                app_log.error("Telit LE50 (PORT: " + self.rf_connector.description + ") - RX Monitoring Thread : " + str(traceback.format_exc()))
#                buf = ''
#                time.sleep(SLEEP_AFTER_EXCEPTION_IN_SEC)
       





#    def SendTelitMessage(self, msg):

#        self.telit_ack_event.clear()

#        app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") - Send Message: " + to_hex(msg))

#        self.rf_connector.doSend(msg)

#        rslt = self.telit_ack if self.telit_ack_event.wait(TELIT_ACK_TIMEOUT_IN_SEC) == True else TelitResponseType.RFAckTimeout

#        rslt_str = 'RFAckOk' if rslt == TelitResponseType.RFAckOk else 'RFAckError' if rslt == TelitResponseType.RFAckError else 'RFAckTimeout' if rslt == TelitResponseType.RFAckTimeout else ''

#        app_log.info("Telit LE50 (PORT: " + self.rf_connector.description + ") - Send Message: " + to_hex(msg) + " Result: " + rslt_str)

#        return rslt


#    # +++
#    def StartConfigMode(self):

#        return self.SendTelitMessage("+++")

#    # ATO\r
#    def EndConfigMode(self):

#        return self.SendTelitMessage("ATO\r")


#    # ATR\r
#    def ResetConfiguration(self):

#        return self.SendTelitMessage("ATR\r")


#    # ATS{register}={value}/r
#    def AtsCommnad(self, register, value):

#        return self.SendTelitMessage("ATS" + str(register) + "=" + str(value) + "\r")



#    def buildCmdChunck(self, unitId, packet_id, chunck_num, sub_payload):

#        beforeCrc = pack('<H', packet_id) + pack('<h', chunck_num) + pack('B', len(sub_payload)) + sub_payload

#        crc = self.crc16_calculator.calculate(beforeCrc)

#        return pack('>H', unitId) + '=' + beforeCrc + pack('<H', crc) + '\r'

#    def Send(self, unitId, packetId, payload):

#        chunks = []

#        chunck_num = 0

#        subp_max_len = TELIT_MAX_MSG_LEN - 11

#        while len(payload) > 0:

#            subp = payload[:subp_max_len]

#            payload = payload[subp_max_len:]
            
#            chunck_num = (chunck_num + 1) * -1 if len(payload) == 0 else chunck_num + 1
     
#            chunck = self.buildCmdChunck(unitId, packetId, chunck_num, subp)

#            rslt = self.SendTelitMessage(chunck)

#            chunks.append(ChunkSendResult(subp, datetime.datetime.now(), rslt))

#            if rslt == TelitResponseType.RFAckTimeout or rslt == TelitResponseType.RFAckError:
#                break
  
#        return chunks

#    def SendBrodcast(self, packetId, payload): 
  
#        return Send(0, packetId, payload)










#    # DEBUG
#    def send_dump(self, unitId, dump):
#        dump_msg = pack('>H', unitId) + '=' + dump + '\r'
#        self.SendTelitMessage(dump_msg)

#    # last chunk is still positive
#    def send_faulty_chuncks1(self, unitId, packetId, payload):
#        chunck_num = 0

#        subp_max_len = TELIT_MAX_MSG_LEN - 11

#        while len(payload) > 0:

#            subp = payload[:subp_max_len]

#            payload = payload[subp_max_len:]
            
#            chunck_num += 1
     
#            chunck = self.buildCmdChunck(unitId, packetId, chunck_num, subp)

#            rslt = self.SendTelitMessage(chunck)

#            if rslt == TelitResponseType.RFAckTimeout or rslt == TelitResponseType.RFAckError:
#                return rslt 
  
#        return TelitResponseType.RFAckOk

#    # long delay between chuncks
#    def send_faulty_chuncks2(self, unitId, packetId, payload):
#        chunck_num = 0

#        subp_max_len = TELIT_MAX_MSG_LEN - 11

#        while len(payload) > 0:

#            subp = payload[:subp_max_len]

#            payload = payload[subp_max_len:]
            
#            chunck_num = (chunck_num + 1) * -1 if len(payload) == 0 else chunck_num + 1
     
#            chunck = self.buildCmdChunck(unitId, packetId, chunck_num, subp)

#            time.sleep(2)

#            rslt = self.SendTelitMessage(chunck)

#            if rslt == TelitResponseType.RFAckTimeout or rslt == TelitResponseType.RFAckError:
#                return rslt 
  
#        return TelitResponseType.RFAckOk


#    def send_time_out_before_chunk(self, chunk_to_be_delayed, unitId, packetId, payload):

#        chunck_num = 0

#        subp_max_len = TELIT_MAX_MSG_LEN - 11

#        while len(payload) > 0:

#            subp = payload[:subp_max_len]

#            payload = payload[subp_max_len:]
            
#            chunck_num = (chunck_num + 1) * -1 if len(payload) == 0 else chunck_num + 1

#            chunck = self.buildCmdChunck(unitId, packetId, chunck_num, subp)

#            if chunck_num == chunk_to_be_delayed:
#                print "DEBUG - wait 5 seconds before sending chunk " + str(chunck_num)
#                time.sleep(5)

#            rslt = self.SendTelitMessage(chunck)

#            if rslt == TelitResponseType.RFAckTimeout or rslt == TelitResponseType.RFAckError:
#                return rslt 
  
#        return TelitResponseType.RFAckOk



#class TelitResponseType:
#    RFAckOk = 0
#    RFAckError = 1     
#    RFAckTimeout = 2  
 
#class FromUnitEndReasonType:
#    LastChunkReceived = 0
#    Timeout = 1   
           
#class ChunkMonitored:  

#    def __init__(self, unit_id, packet_id, chunk_num, payload, rssi):
#        self.unit_id = unit_id
#        self.packet_id = packet_id
#        self.chunk_num = chunk_num
#        self.payload = payload
#        self.rssi = rssi
        
#class ChunkSendResult: 
              
#    def __init__(self, payload, time_stamp, telit_result): 
#        self.payload = payload 
#        self.time_stamp = time_stamp 
#        self.telit_result = telit_result

#class ChunkReceiveResult:  
             
#    def __init__(self, unit_id, chunck_num, payload, rssi, time_stamp):
#        self.unit_id = unit_id 
#        self.chunck_num = chunck_num  
#        self.payload = payload
#        self.rssi = rssi         
#        self.time_stamp = time_stamp
                

#class ChuncksObserver(Observer):
#    def __init__(self):
#        self.chuncks_info = []

#    def on_next(self, x):
#        self.chuncks_info.append((x.chunk_num, x.payload, x.rssi))        

#    def on_completed(self):
#        pass

#    def on_error(self, err):
#        pass
                                           