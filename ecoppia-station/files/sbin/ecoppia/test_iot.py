
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

def connectCallback():
    print 'connected'

def disconnectCallback():
    print 'disconnected'

AWS_IOT_PORT = 8883

ROOTCA_PATH = 'C:\\Users\chanoch.zalcberg\\source\\repos\\Ecoppia\\EcoppiaCMM\\ecoppia_station\certificates\\VeriSign-Primary-Certification-Authority-G5.pem'

#AWS_IOT_END_POINT = 'alp3my8h2g9y-ats.iot.eu-west-3.amazonaws.com'
#PRIVATEKEY_PATH = 'C:\\Users\\chanoch.zalcberg\\Downloads\\f5d69773e4-private.pem.key'
#CERTIFICATE_PATH = 'C:\\Users\\chanoch.zalcberg\\Downloads\\f5d69773e4-certificate.pem.crt'


#PRIVATEKEY_PATH =  'C:\Users\chanoch.zalcberg\Downloads\\iot\\kokoT.private.key'
#CERTIFICATE_PATH = 'C:\Users\chanoch.zalcberg\Downloads\\iot\\kokoT.cert.pem'



AWS_IOT_END_POINT = 'a317cwwoz1cdjc.iot.us-west-2.amazonaws.com'
PRIVATEKEY_PATH = 'C:\\Users\\chanoch.zalcberg\\source\\repos\\Ecoppia\\EcoppiaCMM\\ecoppia_station\\certificates\\c3d8b30f15-private.pem.key'
CERTIFICATE_PATH = 'C:\\Users\\chanoch.zalcberg\\source\\repos\\Ecoppia\\EcoppiaCMM\\ecoppia_station\\certificates\\c3d8b30f15-certificate.pem.crt'

PRIVATEKEY_PATH = 'C:\\Users\\chanoch.zalcberg\\Downloads\\2a2fe1e7bd-private.pem.key'
CERTIFICATE_PATH = 'C:\\Users\\chanoch.zalcberg\\Downloads\\2a2fe1e7bd-certificate.pem.crt'

client = AWSIoTMQTTClient('testD')
client.configureEndpoint(AWS_IOT_END_POINT, AWS_IOT_PORT)
client.configureCredentials(ROOTCA_PATH, PRIVATEKEY_PATH, CERTIFICATE_PATH)
#client.configureConnectDisconnectTimeout(self.DEFAULT_TIMEOUT)
#client.configureMQTTOperationTimeout(self.DEFAULT_TIMEOUT)
client.onOnline = connectCallback
client.onOffline = disconnectCallback
client.connect()
ggg = client.publish('PROD/SmartStationToMaster/ES-0000-00-00-743','popo',0)
client.publish('s1/koko','popo',0)
client.publish('lolo','popo',0)

print 'after connect()'

text = raw_input("prompt")