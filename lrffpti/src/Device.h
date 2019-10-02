/*
 * Copyright (c) 2016, RF Networks Ltd.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code are not permitted.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of RF Networks Ltd. nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

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
	bool is_hex;
public:
	Device(Uploader* uploader) :
		uploader(uploader) ,
				type(1),
				fd_device(-1),
				counter(1000),
				err(E_SUCCESS),
				speed(1),
				maxRetry(3),
				is_hex(false) {}
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
	void setIsHex(bool ft) {
		is_hex = ft;
	}
	void setRS485GPIO(int gpio) {
		if (gpio < 0)
			return;
		uploader->rs485dir = new GPIO(gpio);
		if (uploader->rs485dir != nullptr)
			uploader->rs485dir->Direction(GPIODirection::GPIO_OUT);
	}
	bool getIsHex(void) const { return is_hex; }
	int getFileDescriptor(void) const { return fd_device; }

	bool openDevice(const char* deviceName);
	bool changeBaudRate(uint8_t br);
};

#endif /* DEVICE_H_ */

