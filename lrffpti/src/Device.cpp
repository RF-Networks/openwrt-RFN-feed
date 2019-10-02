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

#include "Device.h"
#include "log.h"

#include <errno.h>


using namespace std;

Device::~Device() {
	if (fd_device > -1)
		close(fd_device);
}

bool Device::initialize(ifstream &stream, const char* deviceName) {
	if (!openDevice(deviceName))
		return false;
    return uploader->initializeStream(stream, is_hex);
}

bool Device::enterBootMode() {
	bool retval = false;
	int origMaxRetries = maxRetry;
	//ssize_t bytesAvailable = 0;
	//uint32_t delay = BYTES_IN_BUFFER_DELAY;
	//uint8_t bootstring1 [] = { 0xAB, 0x65, 0x00, 0x00, 0x08, 0xAA, 0xAA, 0x05, 0x00, 0x00, 0x0B, 0x00, 0x64, 0xCD };
	//uint8_t bootstring2 [] = { 0xAB, 0x6D, 0xFF, 0xFF, 0x41, 0x54, 0x42, 0x4C, 0x0D, 0xCD };
	//uint8_t bootstring3 [] = { 0x6D, 0xFF, 0xFF, 0x41, 0x54, 0x42, 0x4C, 0x0D };
	uint8_t bootstring1 [] = { 0xAB, 0x96, 0x01, 0x0A, 0x12, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x07, 0xA1, 0xCD };
	uint8_t bootstring4 [] = { 0x2B, 0x2B, 0x2B };
	uint8_t bootstring5 [] = { 0x41, 0x54, 0x4F, 0x0D };
	//uint8_t bootstring6 [] = { 0x41, 0x54, 0x42, 0x4C, 0x0D };
	ssize_t bytesWrite = 0, bootStringLen = 0;

	ALOGW("lrffpti enterBootMode Please wait...\n");

	if (!changeBaudRate(speed)) {
		ALOGE("lrffpti enterBootMode Unable to set baudrate\n");
		err = E_OSCALL;
		return retval;
	}
	usleep(500);

	// Send enter boot command
	while (maxRetry--) {
		ALOGD("Send enter bootloader attempt: %d\n", origMaxRetries - maxRetry);
		uploader->setRTS(GPIO_LOW);
		if (type == 1) {
			// RFN-Mesh
			bootStringLen = sizeof(bootstring1);
			bytesWrite = write(fd_device, bootstring1, bootStringLen);
			sleep(2);
		} else if (type == 2) {
			// RFN-Star
			bootStringLen = sizeof(bootstring4);
			bytesWrite = write(fd_device, bootstring4, bootStringLen);
			sleep(1);
			bootStringLen = sizeof(bootstring5);
			bytesWrite = write(fd_device, bootstring5, bootStringLen);
			sleep(2);
//			bytesWrite = write(fd_device, bootstring5, bootStringLen);
//			sleep(2);
		}
		uploader->setRTS(GPIO_HIGH);
//		if (type == 2) {
//			bootStringLen = sizeof(bootstring2);
//			bytesWrite = write(fd_device, bootstring2, bootStringLen);
//			sleep(1);
//			bootStringLen = sizeof(bootstring3);
//			bytesWrite = write(fd_device, bootstring3, bootStringLen);
//		} else if (type == 3) {
//			bootStringLen = sizeof(bootstring4);
//			bytesWrite = write(fd_device, bootstring4, bootStringLen);
//			sleep(1);
//			bootStringLen = sizeof(bootstring5);
//			bytesWrite = write(fd_device, bootstring5, bootStringLen);
//			sleep(2);
//			bytesWrite = write(fd_device, bootstring5, bootStringLen);
//		} else {
//			bootStringLen = sizeof(bootstring1);
//			bytesWrite = write(fd_device, bootstring1, bootStringLen);
//		}
		if ((bytesWrite == bootStringLen) && (bytesWrite > 0)) {
			// Check bootloader mode
			sleep(1);
			if (!changeBaudRate(3)) {
				ALOGE("lrffpti enterBootMode Unable to set baudrate\n");
				err = E_OSCALL;
				return false;
			}
			sleep(1);
			if (!uploader->establishCommunication(this))
			{
				ALOGW("Failed entering bootloader mode...\n");
				if (speed != 2)
					changeBaudRate(speed);
			}
			else {
				sleep(1);
				ALOGW("Entered bootloader mode\n");
				retval = true;
				break;
			}
//			do {
//				ioctl(fd_device, FIONREAD, &bytesAvailable);
//				delay--;
//			} while (bytesAvailable < 12 && delay);
//			break;
		} else {
            ALOGE("write returned %d instead of %d\n", bytesWrite, bootStringLen);
        }
	}
	if (maxRetry == -1)
		err = E_FLASHER_BOOT;
//	else
//		retval = true;

	sleep(1);

	return retval;
}

bool Device::openDevice(const char* deviceName) {
	bool retval = true;
	errno = 0;
	while ( ((fd_device = open(deviceName, O_RDWR | O_NONBLOCK)) < 0) && counter ) {
		ALOGD("Open error %d: %s\n", errno, strerror(errno));
		usleep(PORT_OPEN_DELAY);
		counter--;
	}

	if (counter == 0) {
		err = E_DEVICE_NOT_OPEN;
		ALOGE("lrffpti enterBootMode Unable to open device\n");
		retval = false;
	}
	return retval;
}

bool Device::changeBaudRate(uint8_t br) {
    struct termios serCfg;
    speed_t s_speed;
    err = E_SUCCESS;

    memset(&serCfg, 0, sizeof(serCfg));

    switch(br) {
      case 2:
    	  s_speed = B57600;
        break;
      case 3:
		  s_speed = B115200;
		  break;
      default:
    	  s_speed = B19200;
    }

    if (tcgetattr(fd_device, &serCfg) != 0) {
        err = E_OSCALL;
        goto end;
    }

    cfmakeraw(&serCfg);
    if (cfsetispeed(&serCfg, s_speed) == -1) {
        err = E_OSCALL;
        goto end;
    }

    if (cfsetospeed(&serCfg, s_speed) == -1) {
        err = E_OSCALL;
        goto end;
    }

    serCfg.c_cflag &= ~CRTSCTS;
    if (tcsetattr(fd_device, TCSANOW, &serCfg) != 0) {
        err = E_OSCALL;
        goto end;
    }

end:
    return (err == E_SUCCESS);
}

bool Device::uploadStream(bool enterflashMode) {
	if (!changeBaudRate(3)) {
		ALOGE("lrffpti enterBootMode Unable to set baudrate\n");
		err = E_OSCALL;
		return false;
	}
	sleep(1);
    return uploader->uploadStream(this, enterflashMode);
}

