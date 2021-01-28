import thread
import serial
import time
import os
import sys
import signal
import json

from exceptions import *
from threading import Thread, Event
from Queue import Queue

from rx.subjects import Subject

from ecoppia.globals import *
from ecoppia.lib.package_info import *

class WeatherConnector:

    def __init__(self, mqtt_connector):
        app_log.info("weather_connector")
        self.mqtt_connector = mqtt_connector
        self.subject = Subject()
        self.subject.buffer_with_time(60 * 1000).subscribe(self.handle_weather_data)
        thread.start_new_thread(self.read_device_data, ())

    def handle_weather_data(self, data):
        try:
            # Telegram #6
            weather_data = {
                    "Wind"                  : self.read_value_last(data,  1, 5),
                    "WindDirection"         : self.read_value_last(data,  7, 3),
                    "Temperature"           : self.read_value_last(data, 11, 5), 
                    "RelativeHumidity"      : self.read_value_last(data, 17, 3), 
                    "AirPressure"           : self.read_value_last(data, 21, 6), 
                    "BrightnessNorth"       : self.read_value_last(data, 29, 6), 
                    "BrightnessEast"        : self.read_value_last(data, 35, 6), 
                    "BrightnessSouth"       : self.read_value_last(data, 42, 6), 
                    "BrightnessWest"        : self.read_value_last(data, 49, 6), 
                    "BrightnessMax"         : self.read_value_last(data, 56, 6), 
                    "BrightnessDirection"   : self.read_value_last(data, 63, 3), 
                    "PreciptationEvent"     : self.read_value_max(data, 67, 1), 
                    "PreciptationIntensity" : self.read_value_max(data, 69, 7), 
                    "PreciptationTotal"     : self.read_value_max(data, 77, 6), 
                    "Synop"                 : self.read_value_last(data, 84, 2), 
                    "Latitude"              : self.read_value_last(data, 87, 10), 
                    "Longitude"             : self.read_value_last(data, 98, 11), 
                    "Height"                : self.read_value_last(data, 110, 4), 
                    "SunPositionElevation"  : self.read_value_last(data, 115, 5), 
                    "SunPositionAzimuth"    : self.read_value_last(data, 121, 5), 
                    "Date"                  : data[-1][127: 127 +8],
                    "Time"                  : data[-1][136: 136 +8],
                    "RawData"           : data[-1]}
        
            json_var = json.dumps(weather_data)
            json_str = str(json_var)
            weather_log.info(json_str)
            self.mqtt_connector.doPublishWeather(json_str)
        except Exception,e:
            weather_log.exception("handle_weather_data failed")

    def read_value_last(self, data, start, length):
        try:
            last=  float(data[-1][start : start + length])
            return last
        except Exception,e:
            weather_log.exception("handle_weather_data failed")
            return "invalid"

    def read_value_avg(self, data, start, length):
        try:
            values = [float(i[start : start + length]) for i in data]
            avg = round(sum(values) / float(len(values)), 3)
            return avg
        except Exception,e:
            weather_log.exception("handle_weather_data failed")
            return "invalid"

    def read_value_max(self, data, start, length):
        try:
            values = [float(i[start : start + length]) for i in data]
            maxvalue = max(values)
            return maxvalue
        except Exception,e:
            weather_log.exception("handle_weather_data failed")
            return "invalid"

    def read_device_data(self):
        try:
            weather_log.info("read device data")
            ser = None
            while True:
                try:
                    ser = serial.Serial('/dev/ttyS2', 9600 , timeout=.6)
                    while True:
                        data = ser.read(150)
                        if len(data) == 150:
                            weather_log.info(data)
                            self.subject.on_next(data)
                            time.sleep(.02)
                        else:
                            weather_log.debug(data)
                except Exception,e:
                    weather_log.exception("weather ser.read() failed")
                    if ser is not None:
                        ser.close()
                        ser = None
                    time.sleep(.02)
        except Exception,e:
            weather_log.exception("weather handler failed")


