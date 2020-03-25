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

#include <zlib.h>
#include <thread>
#include <chrono>
#include <algorithm>
#include <math.h>
#include "Uploader.h"
#include "Device.h"
#include "lrffpError.h"
#include "log.h"
#include <libserial/SerialStream.h>

Uploader::Uploader() : rs485dir(nullptr), err(E_SUCCESS), max_address(0) {
	rtsdir = new GPIO(RTS_GPIO);
	rtsdir->Direction(GPIO_OUT);
	rtsdir->Value(GPIO_HIGH);
}

Uploader::~Uploader() {
	if (rs485dir != nullptr)
		delete rs485dir;
	rs485dir = nullptr;
	if (rtsdir != nullptr)
		delete rtsdir;
	rtsdir = nullptr;
}

bool Uploader::initializeStream(ifstream &stream) {
	 string line;
	 unsigned int address = 0;
	 max_address = 0;
	 string tmp;
	 // Load stream
	 for (int i = 0; i < 0xFFFF; i++)
		 data[i] = 0xFF;
	 while(getline(stream, line)) {
		 address = strtol(line.substr(3, 4).c_str(), nullptr, 16);
		 tmp = line.substr(7,2);
		 if (!tmp.compare("01"))
			 break;
		 else {
			 tmp = line.substr(9, line.length() - 10);

			 //ALOGW("%s : %04X ", tmp.c_str(), address);
			 for (int i = 0; i < (int)(tmp.length() / 2); ++i) {
				 //ALOGW("%02x", strtol(tmp.substr(i * 2, 2).c_str(), nullptr, 16));
				 data[address + i] = strtol(tmp.substr(i * 2, 2).c_str(), nullptr, 16);
				 if (address + i > max_address)
					 max_address = address + i;
			 }
			 //ALOGW("\n");
		 }
		 //ALOGW("%04x\n", address);
	 }

	 if (max_address > 0)
		 err = E_SUCCESS;

	 return (err == E_SUCCESS);
}

bool Uploader::isInBootloader(Device* device) {
	bool res;
	LibSerial::BaudRate br = device->getSerialStream()->GetBaudRate();
	device->getSerialStream()->SetBaudRate(LibSerial::BaudRate::BAUD_115200);
	res = enterFlashingMode(device);
	device->getSerialStream()->SetBaudRate(br);
	return res;
}

bool Uploader::enterFlashingMode(Device* device) {
	uint8_t tmp[270];
	for (int i = 0; i < 11; i++)
		tmp[i] = 0x30;
	tmp[11] = 0x11;
	for (int i = 12; i < 270; i++)
		tmp[i] = 0xAA;
	return sendFlashCommand(device, tmp, 270);
}

bool Uploader::exitFlashingMode(Device* device) {
	uint8_t tmp[270];
	for (int i = 0; i < 11; i++)
		tmp[i] = 0x30;
	tmp[11] = 0x55;
	for (int i = 12; i < 270; i++)
		tmp[i] = 0xAA;
	return sendFlashCommand(device, tmp, 270);
}

bool Uploader::eraseMemory(Device* device) {
	uint8_t tmp[270];
	for (int i = 0; i < 11; i++)
		tmp[i] = 0x30;
	tmp[11] = 0x22;
	for (int i = 12; i < 270; i++)
		tmp[i] = 0xAA;
	return sendFlashCommand(device, tmp, 270);
}

bool Uploader::sendFirmwareChunk(Device* device, ssize_t offset) {
	uint8_t tmp[270];
	uint8_t retry;
	bool res;
	for (int i = 0; i < 11; i++)
		tmp[i] = 0x30;
	//ALOGD("Firmware type %d\n", device->getFirmwareType());
	tmp[11] = (device->getFirmwareType())? 0x34 : 0x33;
	tmp[12] = (offset >> 8) & 0xFF;
	tmp[13] = offset & 0xFF;
	for (int i = 14; i < 270; i++) {
		if ((unsigned int)(offset + i - 14) <= max_address)
			tmp[i] = data[offset + i - 14];
		else
			tmp[i] = 0xFF;
	}
	retry = 0;
	while (retry < ((rs485dir != nullptr)? 6 : 3)) {
		res = sendFlashCommand(device, tmp, 270);
		if (res) {
			return true;
		}
		retry++;
		usleep(10000);
	}
	return false;
}

bool Uploader::compareCRC(Device* device, unsigned int pointer) {
	uint32_t crc_reg = 0;
	uint32_t data_reg;
	static uint32_t help_a, help_b;
	uint8_t tmp[270];
	uint8_t tmp_crc[128 * 256];
	if (max_address < 1)
		return false;

	for (int j = 0; j < 128 * 256; j++)
		tmp_crc[j] = ((unsigned int)j <= max_address) ? data[j] : 0xFF;

	for (int i = 0; i < 256 * 128; i+=2) {
		help_a = crc_reg << 1;
		help_a &= 0x00FFFFFE; // always act as 24-bit variable
		help_b = crc_reg & (1UL << 23);
		if (help_b > 0)
			help_b = 0x00FFFFFF;
		data_reg = (((tmp_crc[i + 1]) << 8) + (tmp_crc[i]));/*0x0000FFFF;*/
		crc_reg = (help_a ^ data_reg) ^ (help_b & 0x0080001B);
		crc_reg = crc_reg & 0x00FFFFFF;
	}

	ALOGD("Calculated CRC 0x%06X\n", crc_reg & 0x00FFFFFF);
	for (int i = 0; i < 11; i++)
		tmp[i] = 0x30;
	tmp[11] = 0x66;
	tmp[12] = (pointer >> 8) & 0xFF;
	tmp[13] = pointer & 0xFF;
	tmp[14] = (uint8_t)(crc_reg & 0xFF);
	tmp[15] = (uint8_t)((crc_reg >> 8) & 0xFF);
	tmp[16] = (uint8_t)((crc_reg >> 16) & 0xFF);

	for (int i = 17; i < 270; i++)
		tmp[i] = 0xAA;
	return sendFlashCommand(device, tmp, 270);
}

bool Uploader::uploadStream(Device* device) {
	unsigned int pointer = 0;
	int retry = 0;
	err = E_SUCCESS;

	ALOGD("Erasing memory...\n");
	retry = 0;
	while (retry < 3) {
		if (!eraseMemory(device)) {
			err = E_CANT_ERASE_FLASH;
		} else {
			err = E_SUCCESS;
			break;
		}
		retry++;
	}
	ALOGD("Memory erased.\n");

	ALOGD("Flashing firmware %d bytes...\n", max_address);
	while (pointer <= max_address) {
		if (get_log_level() == LOG_LEVEL_VERBOSE)
			ALOGD("Flashing offset 0x%04X... %d%%\n", pointer, (int)(pointer * 100.0 / max_address));
		else
			ALOGI("lrffp Progress - %d%%\r", (int)(pointer * 100.0 / max_address));
		retry = 0;
		err = E_SUCCESS;
		while (retry < 3) {
			if (!sendFirmwareChunk(device, pointer)) {
				err = E_CANT_FLASH_CHUNK;
			} else {
				err = E_SUCCESS;
				break;
			}
			retry++;
		}
		if (retry > 2 || err == E_CANT_FLASH_CHUNK) {
			err = E_CANT_FLASH_CHUNK;
			return false;
		}
		pointer += 256;
	}
	ALOGD("Firmware flashed %d bytes.\n", pointer);
	if (!device->getFirmwareType()) {
		ALOGD("Comparing CRC...\n");
		retry = 0;
		while (retry < 3) {
			if (!compareCRC(device, pointer)) {
				err = E_CRC_COMPARE_FAILURE;
			} else {
				err = E_SUCCESS;
				break;
			}
			retry++;
		}
		if (retry > 2 || err == E_CRC_COMPARE_FAILURE) {
			err = E_CRC_COMPARE_FAILURE;
			return false;
		}
		ALOGD("CRC OK.\n");
	}

	ALOGD("Exiting flashing mode...\n");
	retry = 0;
	err = E_SUCCESS;
	while (retry < 3) {
		if (!exitFlashingMode(device)) {
			err = E_CANT_EXIT_FLASH;
		} else {
			err = E_SUCCESS;
			break;
		}
		retry++;
	}
	if (retry > 2 || err == E_CANT_EXIT_FLASH) {
		err = E_CANT_EXIT_FLASH;
		return false;
	}
	ALOGD("Device has exited flashing mode.\n");
	return true;
}

bool Uploader::sendFlashCommand(Device* device, uint8_t *data, ssize_t size) {
	size_t bytesAvailable = 0;
	uint8_t tmp[512];
	uint32_t delay = BYTES_IN_BUFFER_DELAY * 3;

	memset(tmp, 0, sizeof(tmp));

	device->getSerialStream()->FlushIOBuffers();

	if (rs485dir != nullptr) {
		rs485dir->Value(1);
		usleep(20);
	}

	//ALOGD("-> %s\n", array_as_hex_string(data, size).c_str());

	device->getSerialStream()->write((const char*)data, size);
	device->getSerialStream()->DrainWriteBuffer();

	if (rs485dir != nullptr) {
		rs485dir->Value(0);
	}

	// All bytes written, get reply
	do {
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
		bytesAvailable = device->getSerialStream()->GetNumberOfBytesAvailable();
		delay--;
	} while (bytesAvailable < 12 && delay);

	if (bytesAvailable > sizeof(tmp)) {
		bytesAvailable = sizeof(tmp);
	}

	if (bytesAvailable > 11) {
		device->getSerialStream()->read((char*)tmp, bytesAvailable);
		//ALOGD("<- %s\n", array_as_hex_string(&tmp[0], bytesAvailable).c_str());
		for (int i = 0; i < 11; i++) {
			if ((tmp[i] < 'a' || tmp[i] > 'z') && (tmp[i] < 'A' || tmp[i] > 'Z') && (tmp[i] < '0' || tmp[i] > '9'))
				return false;
		}
		return (!tmp[11]);
	}
	return false;
}
