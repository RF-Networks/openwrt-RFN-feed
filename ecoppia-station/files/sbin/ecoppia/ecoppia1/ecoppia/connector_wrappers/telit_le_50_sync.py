import itertools
from operator import itemgetter

from rx import Observable
from rx.concurrency import *
from rx.concurrency.newthreadscheduler import *

from ecoppia.connector_wrappers.telit_le_50 import *

#BACK_AND_FORTH_TIMEOUT_IN_MS = 700

# -- DEBUG --
BACK_AND_FORTH_TIMEOUT_IN_MS = 5000

class TelitLE50Sync():

    def __init__(self, telit_le_50_connector):
        self.telit_le_50_connector = telit_le_50_connector

    def send_sync(self, unit_id, packet_id, msg):
        
        obs = self.telit_le_50_connector.rx_msg_subject.observe_on(Scheduler.new_thread)

        obs = obs.filter(lambda x: x.packet_id == packet_id)
        
        obs = obs.timeout(BACK_AND_FORTH_TIMEOUT_IN_MS)

        obs = obs.timestamp()

        con = obs.replay(None)
        
        d = con.connect()
                                
        sent_chunks = self.telit_le_50_connector.Send(unit_id, packet_id, msg)
        received_chunks = []
        timeout = False

        app_log.debug("send_sync, read chunk: " + str(TelitResponseType.RFAckOk))
        app_log.debug("send_sync, read chunk: " + str(TelitResponseType.RFAckOk) + " == " + str(sent_chunks[0].telit_result))
        if TelitResponseType.RFAckOk == sent_chunks[0].telit_result:
            try:

                for x in con.to_blocking():
                    app_log.debug("send_sync, read chunk: " + str(x.value.chunk_num))
                    received_chunks.append(ChunkReceiveResult(x.value.unit_id, x.value.chunk_num, x.value.payload, x.value.rssi, x.timestamp))
                    if x.value.chunk_num < 0 :
                        break
            except Exception as ex:
                if ex.message == 'Timeout':
                    app_log.error("send_sync, read chunk Timedout")
                else:
                    app_log.exception("con.to_blocking()")
                timeout = True
        
        d.dispose()
        app_log.debug("return")
        return UnicastRequestChunks(sent_chunks, received_chunks, timeout)

    def send_sync_multicast(self, packet_id, msg):
        
        obs = self.telit_le_50_connector.rx_msg_subject.observe_on(Scheduler.new_thread)

        obs = obs.filter(lambda x: x.packet_id == packet_id)

        obs = obs.timestamp()

        obs = obs.timeout(BACK_AND_FORTH_TIMEOUT_IN_MS, Observable.from_([]))

        con = obs.replay(None)
        
        con.connect()
                                
        sent_chunks = self.telit_le_50_connector.Send(0, packet_id, msg)

        received_chunks = []

        con.to_blocking().for_each(lambda x: received_chunks.append(ChunkReceiveResult(x.value.unit_id, x.value.chunk_num, x.value.payload, x.value.rssi, x.timestamp)))        
                  
        return BroadcastRequestChunks(sent_chunks, received_chunks)

class BroadcastRequestChunks: 
              
    def __init__(self, sent_chunks, received_chunks): 

        self.sent_chunks = sent_chunks  #list of ChunkSendResult

        self.received_chunks = received_chunks  #list of ChunkReceiveResult

class UnicastRequestChunks: 
              
    def __init__(self, sent_chunks, received_chunks, timeout): 

        self.sent_chunks = sent_chunks  #list of ChunkSendResult

        self.received_chunks = received_chunks  #list of ChunkReceiveResult

        self.timeout = timeout


        






