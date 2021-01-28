# ------------------------------------------------------------------------------
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0 
# ------------------------------------------------------------------------------
# Demonstrates how to call/orchestrate AWS fleet provisioning services
#  with a provided bootstrap certificate (aka - provisioning claim cert).
#   
# Initial version - Raleigh Murch, AWS
# email: murchral@amazon.com
# ------------------------------------------------------------------------------
import traceback
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

import time
import logging
import json 
import os
import shutil
import threading
from datetime import datetime
import glob

# https://www.instructables.com/Printing-Colored-Text-in-Python-Without-Any-Module/
TRED =  '\033[31m' # Red Text
TGREEN =  '\033[32m' # Green Text
ENDC = '\033[m' # reset to the defaults


class ProvisioningHandler:

    def __init__(self, config):
        """Initializes the provisioning handler
        
        Arguments:
            file_path {string} -- path to your configuration file
        """

        self.logger = logging.getLogger(__name__)
        
        self.secure_cert_path = config.SECURE_CERT_PATH
        self.eccopia_cert_path = config.ECCOPIA_CERT_PATH
        self.iot_endpoint = config.IOT_ENDPOINT
        self.template_name = config.PRODUCTION_TEMPLATE
        self.rotation_template = config.CERT_ROTATION_TEMPLATE
        self.claim_cert = config.CLAIM_CERT
        self.secure_key = config.SECURE_KEY
        self.root_cert = config.ROOT_CERT

        # Get configuration directory
        self.configuration_directory = config.CONFIGUTATION
        self.wlan0MacAddress = self.read_mac(config)
        self.unique_id = self.wlan0MacAddress
    
        # Sample Provisioning Template requests a serial number as a 
        # seed to generate Thing names in IoTCore. Simulating here.

        # ------------------------------------------------------------------------------
        #  -- PROVISIONING HOOKS EXAMPLE --
        # Provisioning Hooks are a powerful feature for fleet provisioning. Most of the
        # heavy lifting is performed within the cloud lambda. However, you can send
        # device attributes to be validated by the lambda. An example is shown in the line
        # below (.hasValidAccount could be checked in the cloud against a database). 
        # Alternatively, a serial number, geo-location, or any attribute could be sent.
        # 
        # -- Note: This attribute is passed up as part of the register_thing method and
        # will be validated in your lambda's event data.
        # ------------------------------------------------------------------------------

        self.primary_MQTTClient = None
        self.thing_MQTTClient = None
        self.test_MQTTClient = None
        self.callback_returned = False
        self.message_payload = {}
        self.isRotation = False
        self.thingName = None
        self.topic = None
        self.primaryConnected = False
        self.thingConnected = False

    def read_mac(self, config):
        # Get MAC address.
        for macfile in (config.MAC_FILENAME, config.FALLBACK_MAC_FILENAME):
            try:
                with open(macfile, 'r') as f:
                    return f.readlines()[0].strip(' \t\n\r').upper()
            except IOError:
                self.logger.info('failed to read MAC address from {}'.format(macfile))

    def core_connect(self):
        """ Method used to connect to AWS IoTCore Service. Endpoint collected from config.
        
        """
        if self.isRotation:
            self.logger.info('##### CONNECTING WITH EXISTING CERT #####')
            self.get_current_certs()
        else:
            self.logger.info('##### CONNECTING WITH PROVISIONING CLAIM CERT #####')

        # Define ENDPOINT, CLIENT_ID, PATH_TO_CERT, PATH_TO_KEY, PATH_TO_ROOT
        ENDPOINT = self.iot_endpoint
        CLIENT_ID = self.unique_id
        PATH_TO_CERT = "{}/{}".format(self.secure_cert_path, self.claim_cert)
        PATH_TO_KEY = "{}/{}".format(self.secure_cert_path, self.secure_key)
        PATH_TO_ROOT = "{}/{}".format(self.secure_cert_path, self.root_cert)
        
        self.primary_MQTTClient = AWSIoTMQTTClient(CLIENT_ID)
        self.primary_MQTTClient.configureEndpoint(ENDPOINT, 8883)


        self.primary_MQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
        
        self.primary_MQTTClient.configureAutoReconnectBackoffTime(1, 128, 20)
        self.primary_MQTTClient.configureOfflinePublishQueueing(-1)
        self.primary_MQTTClient.configureDrainingFrequency(2)
        self.primary_MQTTClient.configureConnectDisconnectTimeout(10)
        self.primary_MQTTClient.configureMQTTOperationTimeout(5)


        self.primaryConnected = self.primary_MQTTClient.connect()
        if not self.primaryConnected:
            self.logger.info("Not connected!")
        else:
            self.logger.info("Connected!")

    def on_connection_interrupted(self, connection, error, **kwargs):
        self.logger.critical('connection interrupted with error {}'.format(error))

    def on_connection_resumed(self, connection, return_code, session_present, **kwargs):
        self.logger.info('connection resumed with return code {}, session present {}'.format(return_code, session_present))

    def get_current_certs(self):
        non_bootstrap_certs = glob.glob('{}/[!boot]*.crt'.format(self.secure_cert_path))
        non_bootstrap_key = glob.glob('{}/[!boot]*.key'.format(self.secure_cert_path))

        #Get the current cert
        if len(non_bootstrap_certs) > 0:
            self.claim_cert = os.path.basename(non_bootstrap_certs[0])

        #Get the current key
        if len(non_bootstrap_key) > 0:
            self.secure_key = os.path.basename(non_bootstrap_key[0])

    def enable_error_monitor(self):
        """ Subscribe to pertinent IoTCore topics that would emit errors
        """

        template_reject_topic = "$aws/provisioning-templates/{}/provision/json/rejected".format(self.template_name)
        certificate_reject_topic = "$aws/certificates/create/json/rejected"
        
        template_accepted_topic = "$aws/provisioning-templates/{}/provision/json/accepted".format(self.template_name)
        certificate_accepted_topic = "$aws/certificates/create/json/accepted"

        subscribe_topics = [template_reject_topic, certificate_reject_topic, template_accepted_topic, certificate_accepted_topic]

        for mqtt_topic in subscribe_topics:
            self.logger.info("Subscribing to topic '{}'...".format(mqtt_topic))
            mqtt_topic_subscribe_future = self.primary_MQTTClient.subscribe(mqtt_topic, 1, self.basic_callback)
            if not mqtt_topic_subscribe_future:
                self.logger.critical ("Failled to subscribt to {}".format(mqtt_topic))
            self.topic = template_accepted_topic


    def get_official_certs(self, callback, isRotation=False):
        """ Initiates an async loop/call to kick off the provisioning flow.

            Triggers:
               on_message_callback() providing the certificate payload
        """
        if isRotation:
            self.template_name = self.rotation_template
            self.isRotation = True
        self.orchestrate_provisioning_flow(callback)            


    def create_config(self):
        self.logger.info("Create config")
        try:
            os.stat(self.configuration_directory)
        except Exception:
            os.mkdir(self.configuration_directory)
        stationName = self.thingName[5:]

        # write config file
        with open("{}/config.py".format(self.configuration_directory), "w") as f: 
            f.write("NAME = '{}'".format(stationName) + os.linesep)
            f.write("ENV = 'PROD'" + os.linesep)
            f.write("PUTTY_IP = '127.0.0.1'" + os.linesep)
            f.write("PUTTY_PORT = 22" + os.linesep)

        # change AP name according to station name
        os.system("uci set wireless.ap.ssid='{}'".format(stationName))
        os.system("uci set wireless.ap.encryption='psk2'")
        os.system("uci set wireless.ap.key='ecoppiA!Gateway'")
        os.system("uci commit")
        os.system("luci-reload")
        os.system("/etc/init.d/network restart")

    def backupExistingCertifacates(self):
        self.logger.info("Backup Existing Certifacates")
        existingCertifacates = os.listdir(self.eccopia_cert_path)
        if len(existingCertifacates) > 0 and not os.path.exists("{}/backup".format(self.eccopia_cert_path)):
            os.makedirs("{}/backup".format(self.eccopia_cert_path))
        for certifacate in existingCertifacates:
            if os.path.isfile("{}/{}".format(self.eccopia_cert_path, certifacate)):  
                try:
                    shutil.move("{}/{}".format(self.eccopia_cert_path, certifacate), "{}/backup/{}".format(self.eccopia_cert_path, certifacate))
                except Exception as e:
                    self.logger.critical ("Exception {} ocored when moving file: {}".format(str(traceback.format_exc()), certifacate))

    def placeNewCertifacates(self):
        self.logger.info("Place New Certifacates")
        os.rename("{}/{}".format(self.secure_cert_path, self.new_key_name), "{}/{}-private.pem{}".format(self.eccopia_cert_path, self.thingName, os.path.splitext(self.new_key_name)[1]))
        os.rename("{}/{}".format(self.secure_cert_path, self.new_cert_name), "{}/{}-certificate.pem{}".format(self.eccopia_cert_path, self.thingName, os.path.splitext(self.new_cert_name)[1]))
        os.system("cp {0}/{1} {2}/{1}".format(self.secure_cert_path, self.root_cert, self.eccopia_cert_path))
        self.new_key_name = "{}-private.pem{}".format(self.thingName, os.path.splitext(self.new_key_name)[1])
        self.new_cert_name = "{}-certificate.pem{}".format(self.thingName, os.path.splitext(self.new_cert_name)[1])

    def deleteBootstapCertifacates(self):
        self.logger.info("Delete Bootstap Certifacates")
        os.remove("{}/{}".format(self.secure_cert_path, self.claim_cert))
        os.remove("{}/{}".format(self.secure_cert_path, self.secure_key))
        os.remove("{}/{}".format(self.secure_cert_path, self.root_cert))

        
    def orchestrate_provisioning_flow(self, callback):
        # Connect to core with provision claim creds
        self.core_connect()

        # Monitor topics for errors
        self.enable_error_monitor()

        # Make a publish call to topic to get official certs
        #self.primary_MQTTClient.publish("$aws/certificates/create/json", "{}", 0)
        self.logger.info("publish to $aws/certificates/create/json")
        publishRslt = self.primary_MQTTClient.publish("$aws/certificates/create/json","{}",0)
        if not publishRslt:
            self.logger.info("Failed to publisg - $aws/certificates/create/json")
        time.sleep(1)

        # Wait the function return until all callbacks have returned
        # Returned denoted when callback flag is set in this class.
        while not self.callback_returned:
            self.logger.info("provisioning callback has not returned ...")
            time.sleep(2)

        if self.primaryConnected:
            self.primary_MQTTClient.disconnect()
        if self.thingConnected:
            self.thing_MQTTClient.disconnect()

        if 'statusCode' not in self.message_payload:
            self.deleteBootstapCertifacates()
            time.sleep(2)

        callback(self.message_payload)

    def on_message_callback(self, payload):
        """ Callback Message handler responsible for workflow routing of msg responses from provisioning services.
        
        Arguments:
            payload {bytes} -- The response message payload.
        """
        json_data = json.loads(payload)
        #self.logger.info("json_data: {}".format(json_data))
        # A response has been recieved from the service that contains certificate data. 
        if 'certificateId' in json_data:
            self.logger.info('##### SUCCESS. SAVING KEYS TO DEVICE! #####')
            print('##### SUCCESS. SAVING KEYS TO DEVICE! #####')
            self.assemble_certificates(json_data)
        
        # A response contains acknowledgement that the provisioning template has been acted upon.
        elif 'deviceConfiguration' in json_data:
            if self.isRotation:
                self.logger.info('##### ACTIVATION COMPLETE #####')
                print('##### ACTIVATION COMPLETE #####')
            else:
                self.logger.info('##### CERT ACTIVATED AND THING {} CREATED #####'.format(json_data['thingName']))
                print('##### CERT ACTIVATED AND THING {} CREATED #####'.format(json_data['thingName']))
                self.thingName = str(json_data['thingName'])
                self.topic = "PROD/LoopBack/" + self.thingName
                
                self.backupExistingCertifacates()
                self.placeNewCertifacates()
                self.validate_certs()

        elif 'service_response' in json_data:
            self.logger.info(json_data)
            print('##### SUCCESSFULLY USED PROD CERTIFICATES #####')
            print(TGREEN + '##### STATION SUMMARY: name: {} MAC: {} #####'.format(self.thingName, self.wlan0MacAddress) + ENDC)

        else:
            self.logger.info(json_data)

    def assemble_certificates(self, payload):
        """ Method takes the payload and constructs/saves the certificate and private key. Method uses
        existing AWS IoT Core naming convention.
        
        Arguments:
            payload {string} -- Certifiable certificate/key data.

        Returns:
            ownership_token {string} -- proof of ownership from certificate issuance activity.
        """

        ### Cert ID 
        cert_id = payload['certificateId']
        self.new_key_root = cert_id[0:10]

        self.new_cert_name = '{}-certificate.pem.crt'.format(self.new_key_root)
        ### Create certificate
        f = open('{}/{}'.format(self.secure_cert_path, self.new_cert_name), 'w+')
        f.write(payload['certificatePem'])
        f.close()
        

        ### Create private key
        self.new_key_name = '{}-private.pem.key'.format(self.new_key_root)
        f = open('{}/{}'.format(self.secure_cert_path, self.new_key_name), 'w+')
        f.write(payload['privateKey'])
        f.close()

        ### Extract/return Ownership token
        self.ownership_token = payload['certificateOwnershipToken']
        
        # Register newly aquired cert
        self.register_thing(self.wlan0MacAddress, self.ownership_token)

    def register_thing(self, serial, token):
        """Calls the fleet provisioning service responsible for acting upon instructions within device templates.
        
        Arguments:
            serial {string} -- unique identifer for the thing. Specified as a property in provisioning template.
            token {string} -- The token response from certificate creation to prove ownership/immediate possession of the certs.
            
        Triggers:
            on_message_callback() - providing acknowledgement that the provisioning template was processed.
        """
        if self.isRotation:
            self.logger.info('##### VALIDATING EXPIRY & ACTIVATING CERT #####')
            print('##### VALIDATING EXPIRY & ACTIVATING CERT #####')
        else:
            self.logger.info('##### CREATING THING ACTIVATING CERT #####')
            print('##### CREATING THING ACTIVATING CERT #####')

        register_template = {"certificateOwnershipToken": token, "parameters": {"MacAddress": serial, "CertDate": datetime.now().isoformat()}}
       
        #Register thing / activate certificate
        publishRslt = self.primary_MQTTClient.publish("$aws/provisioning-templates/{}/provision/json".format(self.template_name), json.dumps(register_template), 0)
        if not publishRslt:
            self.logger.critical("Failed to publish - {}".format(self.topic))
        time.sleep(2)
 
    def validate_certs(self):
        """Responsible for (re)connecting to IoTCore with the newly provisioned/activated certificate - (first class citizen cert)
        """
        self.logger.info('##### CONNECTING WITH OFFICIAL CERT #####')
        print('##### CONNECTING WITH OFFICIAL CERT #####')
        self.cert_validation_test()
        
        self.new_cert_pub_sub()

        self.logger.info("##### ACTIVATED AND TESTED CREDENTIALS #####")
        print(TGREEN + "##### ACTIVATED AND TESTED CREDENTIALS #####")
        self.logger.info("##### CREDENTIALS  SAVED TO {} #####".format(self.eccopia_cert_path))
        print("##### CREDENTIALS  SAVED TO {} #####".format(self.eccopia_cert_path) + ENDC)
        self.create_config()

    def basic_callback(self, client, userdata, message):
        self.logger.info("Basic callback message topic is: {}".format(message.topic))
        try:
            self.message_payload = json.loads(message.payload)
            self.on_message_callback(message.payload)
            
            if message.topic == self.topic:
                # Finish the run successfully
                self.logger.info("Successfully provisioned")
                self.callback_returned = True
            elif ( message.topic == "$aws/provisioning-templates/{}/provision/json/rejected".format(self.template_name) or self.topic == "$aws/certificates/create/json/rejected"):
                self.logger.info("Failed provisioning! MAC Address - {}.".format(self.wlan0MacAddress))
                print(TRED + "Failed provisioning! MAC Address - {}.".format(self.wlan0MacAddress)  + ENDC)
                os.remove("{}/{}".format(self.secure_cert_path, self.new_key_name))
                os.remove("{}/{}".format(self.secure_cert_path, self.new_cert_name))
                self.callback_returned = True
        except Exception as e:
            self.logger.info("Failed provisioning! MAC Address - {}.".format(self.wlan0MacAddress)) 
            print(TRED + "Error in basic_callback message.topic - {} ".format(message.topic) + str(traceback.format_exc()) + ENDC)
            sys.exit(-1)

    def cert_validation_test(self):
        ENDPOINT = self.iot_endpoint
        CLIENT_ID = self.thingName
        PATH_TO_CERT = "{}/{}".format(self.eccopia_cert_path, self.new_cert_name)
        PATH_TO_KEY = "{}/{}".format(self.eccopia_cert_path, self.new_key_name)
        PATH_TO_ROOT = "{}/{}".format(self.eccopia_cert_path, self.root_cert)
        
        self.thing_MQTTClient = AWSIoTMQTTClient(CLIENT_ID)
        self.thing_MQTTClient.configureEndpoint(ENDPOINT, 8883)
        self.thing_MQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
        self.thing_MQTTClient.configureAutoReconnectBackoffTime(1, 128, 20)
        self.thing_MQTTClient.configureConnectDisconnectTimeout(6)
        self.thing_MQTTClient.configureMQTTOperationTimeout(20)
        self.thing_MQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.thing_MQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz

        self.thingConnected = self.thing_MQTTClient.connect()
        if self.thingConnected:
            self.logger.info("Connected with production certificates to thing {}".format(CLIENT_ID))
        else:
            self.logger.info("Not Connected with production certificates!")

    def new_cert_pub_sub(self):
        self.logger.info("Subscribing to topic {} ...".format(self.topic))
        try:
            result = self.thing_MQTTClient.subscribe(self.topic, 1, self.basic_callback)
            if not result:
                self.logger.info("Can not subscribe to: {}".format(self.topic))
            time.sleep(2)
        except Exception as e:
            self.logger.critical("Error in new_cert_pub_sub message.topic - {} ".format(self.topic) + str(traceback.format_exc()))
            sys.exit(-1)
        # Wait for subscription to succeed
        self.logger.info("publish after 5 sec. to {}".format(self.topic))
        publishRslt = self.thing_MQTTClient.publish(self.topic, json.dumps({"service_response": "RESPONSE FROM PREVIOUSLY FORBIDDEN TOPIC", "ThingName" : self.thingName}), 0)
        if not publishRslt:
            self.logger.info("Failed to publish - {}".format(self.topic))
