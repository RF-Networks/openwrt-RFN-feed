from executable_request import *

class RfUnicastRequest(ExecutableRequest):

    def __init__(self, commands):
        ExecutableRequest.__init__(self)
        self.Commands = commands #RfNewRequestPerCommandcommand

    def execute(self):

        config_name = self.get_current_rf_configuration()

        rf_unicast_response = RfUnitsResponse(config_name)

        for cmd in self.Commands:
            self.telit_connector.is_old_protocol = not cmd.AddCrc

            for unit_id in cmd.Units:
                global packet_id
                packet_id = (packet_id % 0xFFFF) + 1
                request_chunks = self.send_sync(unit_id, packet_id, cmd.Command)
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

    def send_sync(self, unit_id, packet_id, msg):
        
        obs = self.telit_connector.rx_msg_subject.observe_on(Scheduler.new_thread)
        obs = obs.filter(lambda x: x.packet_id == packet_id)
        obs = obs.timeout(BACK_AND_FORTH_TIMEOUT_IN_MS)
        obs = obs.timestamp()
        con = obs.replay(None)
        d = con.connect()
                                
        sent_chunks = self.telit_connector.Send(unit_id, packet_id, msg)
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

class RfNewRequestPerCommand:
    def __init__(self, command,addCrc, units):
        self.Command = command 
        self.AddCrc = addCrc
        self.Units = units

class UnicastRequestChunks: 
    def __init__(self, sent_chunks, received_chunks, timeout):
        self.sent_chunks = sent_chunks  #list of ChunkSendResult
        self.received_chunks = received_chunks  #list of ChunkReceiveResult
        self.timeout = timeout