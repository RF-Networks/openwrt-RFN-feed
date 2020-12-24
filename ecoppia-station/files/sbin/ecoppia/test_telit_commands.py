#!/usr/bin/env python
import sys
import socket
import time
import serial
import logging
from exceptions import *
from struct import *
from logging.handlers import RotatingFileHandler

import os
import os.path
workingdir = os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), 'ecoppia1')
sys.path.insert(0, workingdir)

from ecoppia.lib.crc16 import *

def to_hex(str):
	res = ' '.join("{:02X}".format(ord(x)) for x in str)
	return res
	
class RFConnector:

	def __init__(self):
		self.ser_socket = None
		
	def read(self):
		while(True):
			msg = self.ser_socket.read(1024)
			if(len(msg) == 0):
				break
			app_log.info('RECEIVED: ' + to_hex(msg))
			
	def send(self, data):
		app_log.info('SEND: ' + to_hex(data))
		self.ser_socket.write(data)

	def connect(self, port):
		self.ser_socket = serial.Serial()
		self.ser_socket.port = port
		self.ser_socket.baudrate = 19200
		self.ser_socket.bytesize = serial.EIGHTBITS #number of bits per bytes
		self.ser_socket.parity = serial.PARITY_NONE #set parity check: no parity
		self.ser_socket.stopbits = serial.STOPBITS_ONE #number of stop bits
		self.ser_socket.xonxoff = False	 #disable software flow control
		self.ser_socket.rtscts = False	 #disable hardware (RTS/CTS) flow control
		self.ser_socket.dsrdtr = False	   #disable hardware (DSR/DTR) flow control
		self.ser_socket.writeTimeout = 2	 #timeout for write

		try: 
			self.ser_socket.open()
		except:
			app_log.error("error open serial port , " + str(traceback.format_exc()))
			raise

		if self.ser_socket.isOpen():
			try:
				self.ser_socket.flushInput()
				self.ser_socket.flushOutput() 
			except:
				app_log.error("error flush serial port...: " + str(traceback.format_exc()))
				raise
			else:
				app_log.info("SUCCESSFULLY OPEN AND FLUSH SERIAL PORT !")
		else:
			raise IOError("cannot open serial port")
	
	def close(self):
		try:
			self.ser_socket.close()
			app_log.info("RF serial socket closed !") 
		except:
			app_log.error("Exception in ser_socket.close()")	


log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
file_handler = RotatingFileHandler('ecoppia_rf_test.log', mode='a', maxBytes=1 * 1024 * 1024, backupCount=4, encoding=None, delay=0)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

app_log = logging.getLogger('root')
app_log.setLevel(logging.DEBUG)
app_log.addHandler(file_handler)
app_log.addHandler(stream_handler)

#rf = RFConnector()
#rf.connect("/dev/ttyS1")
#rf.ser_socket.timeout = .2

#rf.send('+++')
#rf.read()
# rf.send('ATR\r')
# rf.read()
# rf.send('ATO\r')
# rf.read()
# rf.send('+++')
# rf.read()
# rf.send('ATS262=3\r')
# rf.read()
# rf.send('ATS263=3\r')
# rf.read()
# rf.send('ATS264=3\r')
# rf.read()
# rf.send('ATS202=7\r')
# rf.read()
# rf.send('ATS220=9\r')
# rf.read()
# rf.send('ATS200=2\r')
# rf.read()
# rf.send('ATS226=2\r')
# rf.read()
# rf.send('ATS223=5\r')
# rf.read()
# rf.send('ATS255=175')
# rf.read()

# rf.send('ATS200=5\r')
# rf.read()
#rf.send('ATS252=107\r')
#rf.read()
#rf.send('ATS252?\r')
#rf.read()

#rf.send('ATO\r')
#rf.read()


unit_id =  pack('>H', 5334)

packet_Id =  b'\x00\x00'
chunk_num = b'\xFF\xFF'
size = pack('>B',03)

major = pack('>B', 04)
minor = pack('>B',07)
command = b'\x84'

toSend = packet_Id + chunk_num + size + command + major + minor

crc16 = CRC16()
crc =   pack('<H', crc16.calculate(toSend))

toSend = unit_id + '=' + toSend + crc + '\r'

rf.send(toSend)

#rf.ser_socket.timeout = 60
rf.read()

rf.close()
sys.exit()