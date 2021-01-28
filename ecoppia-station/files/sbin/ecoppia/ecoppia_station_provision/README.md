# Station register
Station register is a Python scripts that creates a Iot Thing, registers it with standard certification and polices.
The policy is a global policy that suites the Station requirements.
The basic certification is created in the AWS IoT section and called Bootstrap certification.
The script connects to AWS creates a Thing, named as the next available Thing.

## Usage
 * Login to the station
 * Copy this folder (`ecoppia_station_provision`) to `/sbin/ecoppia/` 
 * Run the script:
```bash
cd /sbin/ecoppia
python -m ecoppia_station_provision
```

Successful run ends with a message showing MAC address + thing name

## Script process
The script connect to AWS with a simple bootstrap certification that do not have much permeations.\
Via the AWS fleet management system it rotates the certificate with a new template certification that has all the necessary permeations for the station to work correctly.\
The process hooks with a Lambda function that checks if the WIFI mac address of the station has been previously registered, if it has been registered the function fetch's the original thing name else it creates a new Thing name, audits the date and returns with that thing name.
Then the script rotates the bootstrap certification with a new certification that is connected to the Thing. The original bootstrap certification would be deleted from the station.

## Certification recovery
In case there is a problem with the certification and we want to recover the certifications.
You need to copy the a set of new bootstrap certifications to the device at 
```bash
/sbin/ecoppia/ecoppia_station_provision/cert
```
and restart the script.

```bash
cd /sbin/ecoppia
python -m ecoppia_station_provision
```

The script will recognize the existing address and will generate appropriate certificates and plant them in the right place.

