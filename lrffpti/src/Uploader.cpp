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
#include "lrffptiError.h"
#include "log.h"
#include <libserial/SerialStream.h>

Uploader::Uploader() :  err(E_SUCCESS), data_crc(0), min_address(0xFFFFFFFF), max_address(0) {
	rtsdir = new GPIO(RTS_GPIO);
	rtsdir->Direction(GPIO_OUT);
	rtsdir->Value(GPIO_HIGH);
}

Uploader::~Uploader() {
	if (rtsdir != nullptr)
		delete rtsdir;
}

bool Uploader::initializeStream(ifstream &stream, bool is_hex)  {
	string line;
	unsigned int address = 0;
    unsigned int byte_count = 0;
	max_address = 0;
	min_address = 0xFFFFFFFF;
	string tmp;
	if (is_hex) {
		// Hex file
		while(getline(stream, line)) {
			address = strtol(line.substr(3, 4).c_str(), nullptr, 16);
            byte_count = strtol(line.substr(1, 2).c_str(), nullptr, 16);
			tmp = line.substr(7,2);
			if (!tmp.compare("01")) {
				break;
			} else {
				tmp = line.substr(9, line.length() - 10);
				for (int i = 0; i < (int)(byte_count); ++i) {
					data[address + i] = strtol(tmp.substr(i * 2, 2).c_str(), nullptr, 16);
					if (address + i > max_address)
						max_address = address + i;
					if (address < min_address)
						min_address = address;
				}
			}
		}
	} else {
		// Binary file
		min_address = 0;
		stream.seekg(0, stream.end);
		max_address = stream.tellg();
		stream.seekg(0, stream.beg);
		if (max_address > FIRMWARE_MAX_SIZE)
		 max_address = FIRMWARE_MAX_SIZE;
		stream.read((char*)data, max_address);
		max_address -= 1;
	}

	data_crc = crc32(0L, Z_NULL, 0);
	data_crc = crc32(data_crc, (const unsigned char*)data + min_address, max_address - min_address + 1);

	//ALOGD("Min 0x%08X, Max 0x%08X\n", min_address, max_address);
	if ((max_address > 0) && (min_address < max_address))
		err = E_SUCCESS;
	return (err == E_SUCCESS);
}

bool Uploader::isInBootloader(Device* device) {
	bool res;
	LibSerial::BaudRate br = device->getSerialStream()->GetBaudRate();
	device->getSerialStream()->SetBaudRate(LibSerial::BaudRate::BAUD_115200);
	res = establishCommunication(device);
	device->getSerialStream()->SetBaudRate(br);
	return res;
}

bool Uploader::establishCommunication(Device* device) {
	uint8_t tmp[] = { 0x03, 0x55, 0x55 };
	uint8_t tmp1[252];
	memset(tmp1, 0, sizeof(tmp1));
	sendFlashCommand(device, tmp, sizeof(tmp));
	device->getSerialStream()->write((const char*)tmp1, sizeof(tmp1));
	device->getSerialStream()->DrainWriteBuffer();

	return sendPing(device);
}

bool Uploader::sendPing(Device* device) {
	uint8_t tmp[] = { 0x03, 0x20, 0x20 };
	return sendFlashCommand(device, tmp, sizeof(tmp));
}

bool Uploader::sendFlashCommand(Device* device, uint8_t *data, ssize_t size, uint8_t *reply, uint8_t reply_size) {
	size_t bytesAvailable = 0;
	uint32_t delay = BYTES_IN_BUFFER_DELAY * ((reply_size > 2)? 3 : 1);
	uint8_t tmp[10];

	device->getSerialStream()->FlushIOBuffers();

	if (size > 2) {
		// Calculate checksum
		data[1] = calculateCS(data + 2, size - 2);
	}

//	ALOGD("-> %s\n", array_as_hex_string(data, size).c_str());

	device->getSerialStream()->write((const char*)data, size);
	device->getSerialStream()->DrainWriteBuffer();

	do {
		std::this_thread::sleep_for(std::chrono::milliseconds(1));
		bytesAvailable = device->getSerialStream()->GetNumberOfBytesAvailable();
		delay--;
	} while (bytesAvailable < reply_size && delay);

	if (bytesAvailable > sizeof(tmp)) {
		bytesAvailable = sizeof(tmp);
	}

	if (bytesAvailable > 1) {
		device->getSerialStream()->read((char*)tmp, bytesAvailable);
//		ALOGD("<- %s\n", array_as_hex_string(&tmp[0], bytesAvailable).c_str());

		if (reply != nullptr) {
			if (bytesAvailable < reply_size)
				reply_size = bytesAvailable;
			memcpy(reply, tmp, reply_size);
			return true;
		} else {
			return (tmp[1] == 0xCC);
		}
	}
	return false;
}

Uploader::Status Uploader::getStatus(Device* device) {
	uint8_t tmp[] = { 0x03, 0x00, 0x23 }, reply[] = { 0x00, 0x00, 0x00, 0x00, 0x00 }, ack[] = { 0x00, 0xCC };
	if ((!sendFlashCommand(device, tmp, sizeof(tmp), reply, sizeof(reply))) || (reply[1] != 0xCC)) {
		return Status::NO_ACK;
	}

	if (reply[3] != reply[4]) {
		// wrong CRC, send NACK
		ack[1] = 0x33;
	}
	// Reply with ACK/NACK
	device->getSerialStream()->write((const char*)ack, sizeof(ack));
	device->getSerialStream()->DrainWriteBuffer();

	return (Uploader::Status)reply[3];
}

void Uploader::setRTS(GPIOValue value) {
	rtsdir->Value(value);
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
	//tmp[11] = (device->getFirmwareType())? 0x34 : 0x33;
	tmp[12] = (offset >> 8) & 0xFF;
	tmp[13] = offset & 0xFF;
	for (int i = 14; i < 270; i++) {
		if ((unsigned int)(offset + i - 14) <= max_address)
			tmp[i] = data[offset + i - 14];
		else
			tmp[i] = 0xFF;
	}
	retry = 0;
	while (retry < 3) {
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
		tmp_crc[j] = ((unsigned int)j <= max_address - min_address) ? data[j] : 0xFF;

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

uint8_t Uploader::calculateCS(uint8_t *data, ssize_t size) {
	uint8_t cs = 0;
	for (int i=0; i < size; i++)
	{
		cs += data[i];
	}
	return cs;
}

bool Uploader::uploadStream(Device* device) {
	uint8_t dl_cmd[] = { 0x0b, 0x00, 0x21, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
	uint8_t er_cmd[] = { 0x07, 0x00, 0x26, 0x00, 0x00, 0x00, 0x00 };
	uint8_t crc_cmd[] = { 0x0F, 0x00, 0x27, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
	uint8_t rst_cmd[] = { 0x03, 0x25, 0x25 };
	uint8_t crc_reply[8];
	uint32_t pointer = min_address, len, chunk_size = 0;
	int retry = 0;
	err = E_SUCCESS;
	ALOGD("Establishing communication...\n");
	while (retry < 3) {
		if (!establishCommunication(device)) {
			err = E_CANT_ENTER_FLASH;
		} else {
			err = E_SUCCESS;
			break;
		}
		retry++;
	}
	if (retry > 2 || err == E_CANT_ENTER_FLASH) {
		err = E_CANT_ENTER_FLASH;
		return false;
	}

	len = max_address - min_address + 1;

	ALOGD("Erasing memory...\n");
	for (uint32_t i = (pointer / 4096.0F); i < (uint32_t)ceil(max_address / 4096.0F); i++, pointer += 0x1000) {
		// Erase page
		ALOGD("Erasing page %d (0x%06X - 0x%06X)\n", i + 1, pointer, pointer + 0xFFF);
		memcpy(er_cmd + 3, &pointer, 4);
		reverse(er_cmd + 3, er_cmd + 7);
		retry = 0;
		while (retry < 3) {
			if ((!sendFlashCommand(device, er_cmd, sizeof(er_cmd))) || (getStatus(device) != Status::SUCCESS)) {
				err = E_CANT_ERASE_FLASH;
			} else {
				err = E_SUCCESS;
				break;
			}
			retry++;
		}
		if (retry > 2 || err == E_CANT_ERASE_FLASH) {
			err = E_CANT_ERASE_FLASH;
			return false;
		}
	}
	ALOGD("Memory erased.\n");

	ALOGD("Flashing firmware %d bytes...\n", len);
	pointer = min_address;
	memcpy(dl_cmd + 3, &pointer, 4);
	reverse(dl_cmd + 3, dl_cmd + 7);
	memcpy(dl_cmd + 7, &len, 4);
	reverse(dl_cmd + 7, dl_cmd + 11);
	while (retry < 3) {
		if ((!sendFlashCommand(device, dl_cmd, sizeof(dl_cmd))) || (getStatus(device) != Status::SUCCESS)) {
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

	do
	{
		chunk_size = min_address + len - pointer;
		if (chunk_size > 252)
			chunk_size = 252;

		// Build chunk
		uint8_t* chunk = new uint8_t[chunk_size + 3];
		chunk[0] = chunk_size + 3;
		chunk[2] = 0x24;
		memcpy(chunk + 3, data + pointer, chunk_size);

		// Send data
		ALOGD("Flashing %d bytes (0x%06X - 0x%06X)...\n", chunk_size, pointer, pointer + chunk_size - 1);

		retry = 0;
		err = E_SUCCESS;
		while (retry < 3) {
			if (!sendFlashCommand(device, chunk, chunk_size + 3)) {
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
		pointer += chunk_size;
	} while (pointer < (min_address + len));
	ALOGD("Firmware flashed %d bytes.\n", pointer);

	ALOGD("Comparing CRC...\n");
	pointer = min_address;
	memcpy(crc_cmd + 3, &pointer, 4);
	reverse(crc_cmd + 3, crc_cmd + 7);
	memcpy(crc_cmd + 7, &len, 4);
	reverse(crc_cmd + 7, crc_cmd + 11);

	while (retry < 3) {
		if ((!sendFlashCommand(device, crc_cmd, sizeof(crc_cmd), crc_reply, sizeof(crc_reply))) || (crc_reply[1] != 0xCC) || (crc_reply[2] != 0x06)) {
			err = E_CRC_COMPARE_FAILURE;
		} else {
			err = E_SUCCESS;
			uint8_t ack[] = { 0x00, 0xCC };
			if (crc_reply[3] != calculateCS(crc_reply + 4, 4)) {
				// wrong CRC, send NACK
				ack[1] = 0x33;
			}
			// Reply with ACK/NACK
			device->getSerialStream()->write((const char*)ack, sizeof(ack));
			device->getSerialStream()->DrainWriteBuffer();
			break;
		}
		retry++;
	}
	if (retry > 2 || err == E_CRC_COMPARE_FAILURE) {
		err = E_CRC_COMPARE_FAILURE;
		return false;
	}

	uint32_t t_crc;
	reverse(crc_reply + 4, crc_reply + 8);
	memcpy(&t_crc, crc_reply + 4, 4);

	ALOGD("CRC Calculated 0x%08X, Received 0x%08X\n", data_crc, t_crc);

	if (t_crc != data_crc) {
		err = E_CRC_COMPARE_FAILURE;
		return false;
	}
	ALOGD("CRC OK.\n");

	// Reset
	ALOGD("Exiting bootloader...\n");
	retry = 0;
	err = E_SUCCESS;
	while (retry < 3) {
		if (!sendFlashCommand(device, rst_cmd, sizeof(rst_cmd))) {
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

