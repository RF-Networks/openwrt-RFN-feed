/*
 * Copyright (c) 2019, RF Networks Ltd.
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

#ifndef SRC_DEVICE_H_
#define SRC_DEVICE_H_

#include <fstream>
#include <libserial/SerialStream.h>
#include "Uploader.h"
#include "log.h"

using namespace std;
using LibSerial::SerialStream;

class Device {
protected:
	Uploader* uploader;
	SerialStream serial;
	int type;
	LibSerial::BaudRate speed;
	bool is_hex;

	bool sendSerialCommand(uint8_t *data, ssize_t size, uint8_t *reply = nullptr, uint8_t reply_size = 0);
public:
	Device(Uploader* uploader);
	virtual ~Device();

	virtual bool initialize(ifstream &stream, const char* deviceName);
	virtual bool enterBootMode() = 0;
	virtual bool uploadStream();
	virtual bool isInBootloader();

	void setType(int t) {
		type = t;
	}
	uint8_t getType(void) const {
		return type;
	}
	void setSpeed(LibSerial::BaudRate s) {
		speed = s;
	}
	void setIsHex(bool ft) {
		is_hex = ft;
	}
	bool openDevice(const char* deviceName);
	bool changeBaudRate(LibSerial::BaudRate br);
	SerialStream* getSerialStream();
};

#endif /* SRC_DEVICE_H_ */
