#include <unistd.h>
#include "Device.h"
#include "lrffp.h"
#include "Uploader.h"
#include "lrffpError.h"

Uploader::Uploader() : err(E_SUCCESS), max_address(0) {

}

Uploader::~Uploader() {

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

bool Uploader::uploadStream(Device* device, bool enterflashMode) {
	unsigned int pointer = 0;
	int retry = 0;
	err = E_SUCCESS;
	if (enterflashMode) {
		ALOGD("Entering flashing mode...\n");
		while (retry < 3) {
			if (!enterFlashingMode(device)) {
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
		ALOGD("Device is in flashing mode.\n");
	}
	ALOGD("Erasing memory...\n");
	if (!eraseMemory(device)) {
		err = E_CANT_ERASE_FLASH;
		return false;
	}
	ALOGD("Memory erased.\n");

	ALOGD("Flashing firmware %d bytes...\n", max_address);
	while (pointer <= max_address) {
		ALOGD("Flashing offset 0x%04X...\n", pointer);
		if (!sendFirmwareChunk(device, pointer)) {
			err = E_CANT_FLASH_CHUNK;
			return false;
		} else {
			 pointer += 256;
		}
	}
	ALOGD("Firmware flashed %d bytes.\n", pointer);

	if (!device->getFirmwareType()) {
		ALOGD("Comparing CRC...\n");
		if (!compareCRC(device, pointer)) {
			err = E_CRC_COMPARE_FAILURE;
			return false;
		}
		ALOGD("CRC OK.\n");
	}

	ALOGD("Exiting flashing mode...\n");
	if (!exitFlashingMode(device)) {
		err = E_CANT_EXIT_FLASH;
		return false;
	}
	ALOGD("Device has exited flashing mode.\n");
	return true;
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
	while (retry < 3) {
		res = sendFlashCommand(device, tmp, 270);
		if (res)
			return true;
		retry++;
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

bool Uploader::sendFlashCommand(Device* device, uint8_t *data, ssize_t size) {
	ssize_t bytes = 0, written_bytes = 0;
	ssize_t bytesAvailable = 0;
	uint32_t delay = BYTES_IN_BUFFER_DELAY;
	uint8_t tmp[512];
	int fd = device->getFileDescriptor();
	tcflush(fd, TCIOFLUSH);

	do {
		written_bytes  = write(fd, data, size);
		if (written_bytes < 0)
			return false;
		bytes += written_bytes;
	} while (bytes < size);
	// All bytes written, get reply

	do {
		ioctl(fd, FIONREAD, &bytesAvailable);
		delay--;
	} while (bytesAvailable < 12 && delay);

	if (bytesAvailable > 11) {
		read(fd, tmp, 512);
		return (!tmp[11]);
	}
	return false;
}
