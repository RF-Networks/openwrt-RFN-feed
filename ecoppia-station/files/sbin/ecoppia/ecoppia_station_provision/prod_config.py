import os 
HERE_DIR = os.path.dirname(os.path.realpath(__file__))

# Set the path to the location containing your certificates (root, private, claim certificate)
SECURE_CERT_PATH = os.path.join(HERE_DIR, 'certs')

# Set the path to the location containing eccopia certificates (root, private, claim certificate)
ECCOPIA_CERT_PATH = "/sbin/ecoppia/certificates"

# Specify the names for the root cert, provisioning claim cert, and the private key.
ROOT_CERT = "VeriSign-Primary-Certification-Authority-G5.pem"
CLAIM_CERT = "bootstrap-certificate.pem.crt"
SECURE_KEY = "bootstrap-private.pem.key"

# Set the name of your IoT Endpoint
IOT_ENDPOINT = "a317cwwoz1cdjc.iot.us-west-2.amazonaws.com"

# Include the name for the provisioning template that was created in IoT Core
PRODUCTION_TEMPLATE = "Station_Certification_Template"
CERT_ROTATION_TEMPLATE = "Rotation_Certification_Template"

# name of the mac address file name
MAC_FILENAME= "/sys/class/net/wlan0/address"
FALLBACK_MAC_FILENAME= "/sys/class/net/ra0/address"

# configuration path
CONFIGUTATION = "/sbin/ecoppia/configuration"

