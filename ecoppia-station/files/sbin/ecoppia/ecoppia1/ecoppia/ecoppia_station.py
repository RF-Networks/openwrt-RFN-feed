#!/usr/bin/env python

print ("script started !")

import os
import sys
import threading
import signal
import serial
import time
import socket
import copy

from _ssl import SSLError



from ecoppia.globals import *
from ecoppia.lib.reset_facilitator import *

import ecoppia.connectors.server_connectors.tcp_connector  as tcp
import ecoppia.connectors.server_connectors.mqtt_connector  as mqtt
import ecoppia.connectors.server_connectors.shadow_connector  as shadow


import ecoppia.connectors.local_connectros.weather_connector as weather


from ecoppia.handlers.thread_handler import *
from ecoppia.handlers.keep_alive_handler import *
from ecoppia.handlers.putty_handler import *
from ecoppia.handlers.upgrade_handler import *
from ecoppia.handlers.reset_handler import *
from ecoppia.handlers.rf_new_handler import *
from ecoppia.handlers.rf_handler import *

from ecoppia.connectors.local_connectros.tcp_to_serial import TcpListener

class Station:
    #@staticmethod
	def start(self):
		try:
			app_log.fatal("wellcome " + software_version)
			reset_facilitator = ResetFacilitator()

			tcp_conn = tcp.TcpConnector()
			tcp_conn.subscribe(PuttyHandler())
			tcp_conn.subscribe(KeepAliveHandler())
			thread.start_new_thread(tcp_conn.doRun, ())

			shadow_connector = shadow.ShadowConnector()
			mqtt_connector = mqtt.MqttConnector(reset_facilitator)
			#TCP TO TELIT
			if TcpListenerEnable :
				reset_facilitator.Disable()
				TL = TcpListener(reset_facilitator)
				instance=threading.Thread(target=TL.doRun)
				instance.start()
			else:
				rf = ThreadHandler(RfNewHandler(reset_facilitator))
				shadow_connector.subscribe(rf)
				mqtt_connector.subscribe(rf)
			
			station_status_log.fatal("software version = " + software_version + "  TcpListenerEnable = " + str(TcpListenerEnable))


			shadow_connector.subscribe(ThreadHandler(EnableWeather(reset_facilitator)))
			shadow_connector.subscribe(ThreadHandler(DisconnectedWatchdog(mqtt_connector)))
			#shadow_connector.subscribe(ThreadHandler(SubscriberByShadow(mqtt_connector)))
			mqtt_connector.subscribe(ThreadHandler(UpgradeHandler()))
			mqtt_connector.subscribe(ThreadHandler(MqttKeepaliveHandler()))
			mqtt_connector.subscribe(ThreadHandler(ResetHandler()))

			try:
				mqtt_connector.AWSIoTMQTTClient = shadow_connector.run_client()
				mqtt_connector.run()

				d = Dal()
				if(d.get_configuration('IsWeatherEnable') == 'True'):
					self.init_weather()
					weather_conn = weather.WeatherConnector(mqtt_connector)

			except SSLError as sslerror:
				app_log.exception("SSLError !!!")
				reset_facilitator.DoApplicationReset()

			except Exception:
				app_log.exception("Connector failed")
				dal = Dal()
				resetCounter =  0
				try: 
					resetCounter = int(dal.get_configuration('resetCounter'))
				except Exception as e:
					resetCounter =  0
				if(resetCounter > 10):
					app_log.info("hard reset, resetCounter: " + str(resetCounter))
					dal.update_configuration('resetCounter', 0)
					reset_facilitator.ClearHardResetDB()
					reset_facilitator.DoHardReset()
				else:
					app_log.info("app reset, resetCounter: " + str(resetCounter))
					dal.update_configuration('resetCounter', resetCounter + 1)
					reset_facilitator.DoApplicationReset()

			app_log.fatal("MAIN METHOD - before main_loop_event.wait()")
			reset_facilitator.main_loop_event.wait()
			app_log.fatal("MAIN METHOD - after main_loop_event.wait()")
			os._exit(1)
			app_log.fatal("MAIN METHOD - after os._exit(1)")

		except Exception:
			app_log.exception("main method failed")

	def signal_term_handler(self, signal, frame):
		ser.close()
		ser = None
		exit(0)

	def init_weather(self):
		try:
			import mraa
			cmd = 'mt7688_pinmux set spi_cs1 gpio'
			os.system(cmd)
			pin = mraa.Gpio(6)
			pin.dir(mraa.DIR_OUT)
			pin.write(0)
			signal.signal(signal.SIGTERM, self.signal_term_handler)
			signal.signal(signal.SIGTSTP, self.signal_term_handler)

		except Exception:
			app_log.exception("init_weather failed")

s = Station()
s.start()



