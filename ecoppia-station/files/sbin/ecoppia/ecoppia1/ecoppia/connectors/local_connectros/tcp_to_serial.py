#!/usr/bin/env python


import os
import sys
import threading
import signal
import time


from ecoppia.globals import *
from ecoppia.lib.reset_facilitator import *
from ecoppia.lib.package_info import *


from ecoppia.connectors.local_connectros.rf_connector.telit_le_50_connectorCR import TelitLE50ConnectorCR

SLEEP_AFTER_EXCEPTION_IN_SEC = 5


class TcpListener:
    
    def __init__(self,reset_facilitator):
        app_log.exception("TcpListener Start")
        self.TCP_PORT = 10001
        self.BUFFER_SIZE = 1024  # Normally 1024, but we want fast response
        self._reset_facilitator = reset_facilitator
        self.conn = None

    def doRun(self):
        while 1:
            try:
                TelitConnector = TelitLE50ConnectorCR(self._reset_facilitator)

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                app_log.exception("socket Opend")
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', self.TCP_PORT))
                app_log.exception("TcpListener bind")
                s.settimeout(30000)
                s.listen(1)
                self.conn, self.addr = s.accept()
                self._reset_facilitator.Disable()
                app_log.exception("Connection address:"+ str(self.addr))

                while 1:
                    data = self.conn.recv(self.BUFFER_SIZE) 
                    if not data: break
                    akn,buff = TelitConnector.SendTelitMessage(data)
                    #app_log.exception("Data buffer Back:" +str(buff))
                    self.conn.send(buff) 

                    #app_log.exception("Data buffer Back:"+ buff + " +Data Recived :"+ data)
                      # echo
                    #app_log.exception("Data Sent Back:"+ buff)
                if self.conn != None :
                    self.conn.close()
                    self.conn = None
                self._reset_facilitator.Enable()
            except Exception:
                app_log.exception("TcpListener exception")
                if self.conn != None :
                    self.conn.close()
                    self.conn =None
                self._reset_facilitator.Enable()




  