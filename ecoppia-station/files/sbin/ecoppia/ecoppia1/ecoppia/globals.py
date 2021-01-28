import os
import os.path
from os import listdir
from os.path import isfile, join
import logging
from logging.handlers import RotatingFileHandler
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from syslog_bridge import SysLogLibHandler

major_unit_version = b'\x03'
minor_unit_version = b'\x00'

software_version = '0.0.0.30'

TcpListenerEnable = False

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_formatter2 = logging.Formatter('%(asctime)s %(levelname)s [%(threadName)s] %(message)s')

stationFolder = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, os.pardir))
certificatesFolder = os.path.join(stationFolder, 'certificates')

# Configure App logging
app_log_file = os.path.join(stationFolder, 'ecoppia_logs','station.log')
app_log_file_handler = RotatingFileHandler(app_log_file, mode='a', maxBytes=1*250*1024, backupCount=0, encoding='utf-8', delay=0)
app_log_file_handler.setFormatter(log_formatter2)
app_log_file_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.DEBUG)
app_log.addHandler(app_log_file_handler)
app_log.addHandler(SysLogLibHandler(1, "Ecoppia station"))

#ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
#ch.setFormatter(log_formatter2)
#app_log.addHandler(ch)


station_status_log_file = os.path.join(stationFolder, 'ecoppia_logs','EcoppiaStationStatus.txt')
station_status_file_handler = logging.handlers.RotatingFileHandler(station_status_log_file, mode='w', backupCount=5)
station_status_file_handler.setFormatter(log_formatter)
station_status_file_handler.setLevel(logging.DEBUG)
should_roll_over = os.path.isfile(station_status_log_file)
if should_roll_over:  # log already exists, roll over!
    station_status_file_handler.doRollover()
station_status_log = logging.getLogger("station_status_log")
station_status_log.setLevel(logging.DEBUG)
station_status_log.addHandler(station_status_file_handler)

# Configure Weather logging
weather_log_file = os.path.join(stationFolder, 'ecoppia_logs','weather.log')
weather_log_file_handler = RotatingFileHandler(weather_log_file, mode='a', maxBytes=1*250*1024, backupCount=0, encoding=None, delay=0)
weather_log_file_handler.setFormatter(log_formatter)
weather_log_file_handler.setLevel(logging.DEBUG)

weather_log = logging.getLogger("weather_log")
weather_log.setLevel(logging.DEBUG)
weather_log.addHandler(weather_log_file_handler)
#weather_log.addHandler(ch)


# Configure Tcp logging
tcp_log_file = os.path.join(stationFolder, 'ecoppia_logs','tcp.log')
tcp_log_file_handler = RotatingFileHandler(tcp_log_file, mode='a', maxBytes=1*250*1024, backupCount=0, encoding=None, delay=0)
tcp_log_file_handler.setFormatter(log_formatter)
tcp_log_file_handler.setLevel(logging.DEBUG)

tcp_log = logging.getLogger("tcp_log")
tcp_log.setLevel(logging.DEBUG)
tcp_log.addHandler(tcp_log_file_handler)
#tcp_log.addHandler(ch)


# Configure AWS IOT Sdk logging
iot_sdk_log_file = os.path.join(stationFolder, 'ecoppia_logs','iot_sdk.log')
iot_sdk_handler = RotatingFileHandler(iot_sdk_log_file, mode='a', maxBytes=1*250*1024, backupCount=0, encoding=None, delay=0)
iot_sdk_handler.setFormatter(log_formatter)
iot_sdk_handler.setLevel(logging.INFO)

iot_log = logging.getLogger("AWSIoTPythonSDK.core")
iot_log.setLevel(logging.ERROR)
iot_log.addHandler(iot_sdk_handler)
#iot_log.addHandler(ch)

# SQLITE

SQLITE_DB_NAME = os.path.join(stationFolder, 'ecoppia_logs','STATION_ACTIVITY.db') 

# CONFIGURATIONS

DB_CONFIGURATIONS_TABLE_NAME = "CONFIGURATIONS_TBL"

DB_CONFIGURATIONS_TABLE_MAX_SIZE = 1000

# HARD RESET

DB_HARD_RESETS_TABLE_NAME = "HARD_RESET_TBL"

DB_HARD_RESETS_TABLE_MAX_SIZE = 1000

TOTAL_SEQUENTIAL_ACK_TIMEOUTS_BEFORE_HARD_RESET = 10

MINIMAL_TIME_INTERVAL_BETWEEN_HARD_RESETS = 30

MAX_TIME_DURATION_FOR_HARD_RESET_PROCESS_TO_TERMINATE = 5

MINIMAL_DISCONNECTED_TIME_TO_RESET = 60 * 3

# LOW LEVEL STREAM CONNECTION (TCP)

#internal way - from station running on my computer
#SERVER_IP = '127.0.0.1'
#SERVER_PORT = 50083

#internal way - from station connected by cable
#SERVER_IP = '192.168.100.170'
#SERVER_PORT = 50083

#external way
#SERVER_IP = '37.142.120.98' # NEW
#SERVER_PORT = 40026

#Dev Server
#SERVER_IP = '35.162.57.201' 
#SERVER_PORT = 40027

#Ecoppia Server
SERVER_IP = '54.69.18.11'
SERVER_PORT = 40027


# AWS IOT CONNECTION

#AWS_IOT_END_POINT = 'alp3my8h2g9y.iot.us-west-2.amazonaws.com'
AWS_IOT_END_POINT = 'a317cwwoz1cdjc.iot.us-west-2.amazonaws.com'
AWS_IOT_PORT = 8883

CA_SUFFIX = 'Certification-Authority-G5.pem'
CERTIFICATE_SUFFIX = 'certificate.pem.crt'
PK_SUFFIX = 'private.pem.key'

ROOTCA_PATH = ''
CERTIFICATE_PATH = ''
PRIVATEKEY_PATH = ''
crtfiles = [f for f in listdir(certificatesFolder) if isfile(join(certificatesFolder, f))]
for crtf in crtfiles:
    if(crtf.endswith(CA_SUFFIX)):
        ROOTCA_PATH = join(certificatesFolder, crtf)
    elif(crtf.endswith(CERTIFICATE_SUFFIX)):
        CERTIFICATE_PATH = join(certificatesFolder, crtf)
    elif(crtf.endswith(PK_SUFFIX)):
        PRIVATEKEY_PATH = join(certificatesFolder, crtf)
if(ROOTCA_PATH == '' or CERTIFICATE_PATH == '' or PRIVATEKEY_PATH == ''):
    raise Exception("one or more certificates or private key are missing in " + certificatesFolder)



