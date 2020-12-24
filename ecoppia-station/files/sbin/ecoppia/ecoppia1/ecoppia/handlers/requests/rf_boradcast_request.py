from executable_request import *

class RfBoradcastRequest(ExecutableRequest):

    def __init__(self, command, waitForUnitResponse):
        ExecutableRequest.__init__(self)

        self.Command = command
        self.WaitForUnitResponse = waitForUnitResponse

    def execute(self):

        config_name = self.get_current_rf_configuration()

        rf_boradcast_response = RfUnitsResponse(config_name)

        global packet_id

        packet_id = (packet_id % 0xFFFF) + 1
        
        request_chunks = self.send_sync_multicast(packet_id, self.Command)
        
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

    def send_sync_multicast(self, packet_id, msg):
        
        obs = self.telit_connector.rx_msg_subject.observe_on(Scheduler.new_thread)

        obs = obs.filter(lambda x: x.packet_id == packet_id)

        obs = obs.timestamp()

        obs = obs.timeout(BACK_AND_FORTH_TIMEOUT_IN_MS, Observable.from_([]))

        con = obs.replay(None)
        
        con.connect()
                                
        sent_chunks = self.telit_connector.Send(0, packet_id, msg)

        received_chunks = []

        con.to_blocking().for_each(lambda x: received_chunks.append(ChunkReceiveResult(x.value.unit_id, x.value.chunk_num, x.value.payload, x.value.rssi, x.timestamp)))        
                  
        return BroadcastRequestChunks(sent_chunks, received_chunks)

class BroadcastRequestChunks: 
              
    def __init__(self, sent_chunks, received_chunks): 

        self.sent_chunks = sent_chunks  #list of ChunkSendResult

        self.received_chunks = received_chunks  #list of ChunkReceiveResult