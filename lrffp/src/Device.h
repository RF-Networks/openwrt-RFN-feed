#ifndef DEVICE_H_
#define DEVICE_H_

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <stdint.h>

#include <sys/ioctl.h>
#include <sys/types.h>
#include <fcntl.h>
#include <termios.h>
#include "Uploader.h"
#include "log.h"
#include "lrffpError.h"

using namespace std;

#define PORT_OPEN_DELAY (100 * 1000)
#define BYTES_IN_BUFFER_DELAY 2000000

class Device {
protected:
	Uploader* uploader;
	int type;
	int fd_device;
	int counter;
	int err;
	int speed;
	int maxRetry;
	int telit_firmware;
public:
	Device(Uploader* uploader) :
		uploader(uploader) ,
				type(1),
				fd_device(-1),
				counter(1000),
				err(E_SUCCESS),
				speed(1),
				maxRetry(3),
				telit_firmware(0) {}
	virtual ~Device();

	virtual bool initialize(ifstream &stream, const char* deviceName);
	virtual bool enterBootMode();
	virtual bool uploadStream(bool enterflashMode);

	void setType(int t) {
		type = t;
	}
	uint8_t getType(void) const { return type; }

	void setSpeed(int s) {
		speed = s;
	}
	void setFirmwareType(int ft) {
		telit_firmware = ft;
	}
	void setRS485GPIO(int gpio) {
		if (gpio < 0)
			return;
		uploader->rs485dir = new GPIO(gpio);
		if (uploader->rs485dir != nullptr)
			uploader->rs485dir->Direction(GPIODirection::GPIO_OUT);
	}
	uint8_t getFirmwareType(void) const { return telit_firmware; }
	int getFileDescriptor(void) const { return fd_device; }

	bool openDevice(const char* deviceName);
	bool changeBaudRate(uint8_t br);
};

#endif /* DEVICE_H_ */
