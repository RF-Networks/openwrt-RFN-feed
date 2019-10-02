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

#ifndef UPLOADER_H_
#define UPLOADER_H_

#include <fstream>
#include <iostream>
#include <string>
#include <algorithm>
#include "log.h"
#include "GPIO.h"

#define FIRMWARE_MAX_SIZE 	0x20000
#define RTS_GPIO			19

using namespace std;

class Device;

class Uploader {
	friend class Device;
protected:
	enum Status {
		SUCCESS = 0x40,
		UNKNOWN_CMD = 0x42,
		INVALID_CMD = 0x43,
		FLASH_FAIL = 0x44,
		NO_ACK = 0x00
	};

	GPIO *rs485dir;
	GPIO *rtsdir;
	ifstream fdStream;
	int err;
	uint8_t data[FIRMWARE_MAX_SIZE];
	uint32_t data_crc;
	unsigned int max_address;
	bool sendFlashCommand(Device* device, uint8_t *data, ssize_t size, uint8_t *reply = nullptr, uint8_t reply_size = 2);
	bool establishCommunication(Device* device);
	bool sendPing(Device* device);
	bool writeToMemory(Device* device, uint8_t *data, ssize_t size);
	Uploader::Status getStatus(Device* device);
	void setRTS(GPIOValue value);

	bool exitFlashingMode(Device* device);
	bool eraseMemory(Device* device);
	bool sendFirmwareChunk(Device* device, ssize_t offset);
	bool compareCRC(Device* device, unsigned int pointer);
	uint8_t calculateCS(uint8_t *data, ssize_t size);
public:
	Uploader();
	virtual ~Uploader();
	virtual bool initializeStream(ifstream &stream, bool is_hex);
	virtual bool uploadStream(Device* device, bool enterflashMode = true);
};

#endif /* UPLOADER_H_ */
