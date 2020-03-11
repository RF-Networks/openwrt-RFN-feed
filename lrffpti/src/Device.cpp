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

#include <thread>
#include <chrono>
#include "Device.h"

Device::Device(Uploader *uploader) :
		uploader(uploader), type(1), speed(LibSerial::BaudRate::BAUD_19200), is_hex(false) {

}

Device::~Device() {
	if (serial.IsOpen())
		serial.Close();
}

bool Device::isInBootloader() {
	return uploader->isInBootloader(this);
}

bool Device::initialize(ifstream &stream, const char *deviceName) {
	if (!openDevice(deviceName))
		return false;
	serial.SetBaudRate(speed);
	serial.SetCharacterSize(LibSerial::CharacterSize::CHAR_SIZE_8);
	serial.SetStopBits(LibSerial::StopBits::STOP_BITS_1);
	serial.SetParity(LibSerial::Parity::PARITY_NONE);
	return uploader->initializeStream(stream, is_hex);
}

bool Device::openDevice(const char *deviceName) {
	try {
		serial.Open(deviceName);
		return serial.IsOpen();
	} catch (const LibSerial::OpenFailed &ex) {
		ALOGD("Open error: %s", ex.what());
	}
	return false;
}

bool Device::changeBaudRate(LibSerial::BaudRate br) {
	serial.SetBaudRate(br);
	return true;
}

SerialStream* Device::getSerialStream() {
	return &serial;
}

bool Device::sendSerialCommand(uint8_t *data, ssize_t size, uint8_t *reply, uint8_t reply_size) {
	size_t bytesAvailable = 0;
	uint8_t tmp[256];
	uint32_t delay = BYTES_IN_BUFFER_DELAY * ((reply_size > 2)? 3 : 1);
	if (data == nullptr || size < 1 || !serial.IsOpen())
		return false;
	serial.FlushIOBuffers();

//	ALOGD("-> %s\n", array_as_hex_string(data, size).c_str());
	serial.write((const char*)data, size);
	serial.DrainWriteBuffer();

	do {
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
		bytesAvailable = serial.GetNumberOfBytesAvailable();
		delay--;
	} while (bytesAvailable < reply_size && delay);

	if (bytesAvailable > sizeof(tmp)) {
		bytesAvailable = sizeof(tmp);
	}

	if (bytesAvailable > 1) {
		serial.read((char*)tmp, bytesAvailable);
//		ALOGD("<- %s\n", array_as_hex_string(&tmp[0], bytesAvailable).c_str());

		if (reply != nullptr) {
			if (bytesAvailable < reply_size)
				reply_size = bytesAvailable;
			memcpy(reply, tmp, reply_size);
		}
		return true;
	}
	return false;
}

bool Device::uploadStream() {
	serial.SetBaudRate(LibSerial::BaudRate::BAUD_115200);
	return uploader->uploadStream(this);
}

