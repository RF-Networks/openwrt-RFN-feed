#include "lrffp.h"
#include "DeviceFactory.h"

Device* DeviceFactory::getDevice(int deviceId) {
	Uploader* up;
	switch (deviceId) {
		case DEVICE_TAG_READER_ROUTER:
			up = new Uploader();
			return new Device(up);
			break;
		case DEVICE_COORDINATOR:
			up = new Uploader();
			return new Device(up);
			break;
		case DEVICE_STAR:
			up = new Uploader();
			return new Device(up);
			break;
		default:
			return NULL;
	}
}

void DeviceFactory::destroyDevice(Device *dev) {
    if (NULL != dev) {
        delete dev;
        dev = NULL;
    }
}

