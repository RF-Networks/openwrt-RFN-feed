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

#include <fstream>
#include <cstring>
#include <thread>
#include <chrono>
#include <stdlib.h>
#include <getopt.h>
#include "lrffp.h"
#include "log.h"

#include "DeviceFactory.h"
#include "Device.h"

using namespace std;

static int verbose_flag = 0;
static int deviceId = 0;
static int telit_firmware = 0;
static Device* dev = NULL;
static char* deviceName;
static LibSerial::BaudRate deviceSpeed = LibSerial::BaudRate::BAUD_19200;
static int bootloader_check = 0;
static int rs485dirgpio = -1;

static const char *deviceNames[] = { "All", "RFN-TagReceiver", "Telit-Mesh", "Telit-Star", "RFN-Mesh" };

static void identify_device(char *selection) {
	switch (*selection) {
	case DEVICE_ALL_SELECTION:
		deviceId = DEVICE_ALL;
		break;
	case DEVICE_RFN_TAG_RECEIVER_SELECTION:
		deviceId = DEVICE_RFN_TAG_RECEIVER;
		break;
	case DEVICE_TELIT_MESH_SELECTION:
		deviceId = DEVICE_TELIT_MESH;
		break;
	case DEVICE_TELIT_STAR_SELECTION:
		deviceId = DEVICE_TELIT_STAR;
		break;
	case DEVICE_RFN_MESH_SELECTION:
		deviceId = DEVICE_RFN_MESH;
		break;
	default:
		ALOGE("lrffp identify_device Device code not recognized: aborting...\n");
		exit(EXIT_FAILURE);
	}
}

static void identify_speed(char *selection) {
	switch (*selection) {
	case DEVICE_SPEED_SELECTION_115200:
		deviceSpeed = LibSerial::BaudRate::BAUD_115200;
		break;
	case DEVICE_SPEED_SELECTION_19200:
		deviceSpeed = LibSerial::BaudRate::BAUD_19200;
		break;
	case DEVICE_SPEED_SELECTION_57600:
		deviceSpeed = LibSerial::BaudRate::BAUD_57600;
		break;
	default:
		ALOGE("default speed 19200\n");
		deviceSpeed = LibSerial::BaudRate::BAUD_19200;
	}
}

static void identify_gpio(char *selection) {
	char *end;
	long int values[] = { 0, 1, 2, 3, 4, 5, 6, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 37, 43, 44, 45, 46 };
	long int val = strtol(selection, &end, 10);
	rs485dirgpio = -1;
	for (size_t i = 0; i < sizeof(values); i++)
	{
		if (val == values[i])
		{
			rs485dirgpio = (int)val;
			break;
		}
	}
}

static void check_args(int argc, char *argv[]) {
	static struct option long_options[] = {
		{"device", required_argument, NULL, 'd'},
		{"speed", required_argument, NULL, 's'},
		{"verbose", no_argument, &verbose_flag, 1},
		{"version", no_argument, NULL, 'v'},
		{"help", no_argument, NULL, 'h'},
		{"enterbootloader", no_argument, &bootloader_check, 'b'},
		{"gpio", optional_argument, &rs485dirgpio, 'g'},
		{0, 0, 0, 0}
	};

	int option_index = 0;
	int c;

	for (;;) {
		c = getopt_long(argc, argv, "d:s:vhbg:", long_options, &option_index);

		if (c == -1)
			break;

		switch(c) {
		case 'd':
			identify_device(optarg);
			break;
		case 's':
			identify_speed(optarg);
			break;
		case 'v':
			ALOGI("%s\n", VERSION_MSG);
			exit(EXIT_SUCCESS);
			break;
		case 'h':
			ALOGI("%s\n", HELP_MSG);
			exit(EXIT_SUCCESS);
			break;
		case 'b':
			bootloader_check = 1;
			break;
		case 'g':
			identify_gpio(optarg);
			break;
		}
	}

	if ((argc - optind) != 2) {
		ALOGE("lrffp check_args needed filename of the stream and the serial device\n");
		exit(EXIT_FAILURE);
	}
}

static const char *get_filename_ext(const char *filename) {
    const char *dot = strrchr(filename, '.');
    if(!dot || dot == filename) return "";
    return dot + 1;
}

static void check_stream_file(int argc, char *argv[], ifstream &fileStream)
{
	string fn = string(get_filename_ext(argv[optind]));
	telit_firmware = !fn.compare("tlt");
    fileStream.open(argv[optind++], ios::in);

    if (!fileStream.is_open()) {
        ALOGE("lrffp check_stream_file Error opening the stream\n");
        exit(EXIT_FAILURE);
    }
}

void manage_failure(ifstream &fs, const char *msg) {
    fs.close();
    if (dev != nullptr)
        DeviceFactory::destroyDevice(dev);
    ALOGE("%s", msg);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
	ifstream fdStream;
	bool isInBootloader;

	check_args(argc, argv);

	if (verbose_flag)
		set_log_level(LOG_LEVEL_VERBOSE);

	system("mt7688_pinmux set spi_s gpio");
	system("mt7688_pinmux set pwm1 gpio");

	ALOGI("lrffp Device chosen: %s%s\n", deviceNames[deviceId], ((rs485dirgpio > -1)? " RS485": ""));

	check_stream_file(argc, argv, fdStream);

	deviceName = argv[optind++];

	dev = DeviceFactory::getDevice((deviceId == DEVICE_ALL)? DEVICE_RFN_TAG_RECEIVER : deviceId);
	if (dev == NULL)
		manage_failure(fdStream, "lrffp Device not supported\n");

	dev->setSpeed(deviceSpeed);
	dev->setFirmwareType(telit_firmware);
	if (!dev->initialize(fdStream, deviceName))
		manage_failure(fdStream, "lrffp Error checking stream\n");

	isInBootloader = dev->isInBootloader();
	if (!bootloader_check && !isInBootloader)
		manage_failure(fdStream, "lrffp Device is not in bootloader, must be in bootloader in order to flash firmware\n");

	if (!isInBootloader && bootloader_check) {
		// Not in bootloader, should enter bootloader
		if (deviceId == DEVICE_ALL) {
			deviceId = DEVICE_RFN_TAG_RECEIVER;
			while (deviceId <= DEVICE_RFN_MESH)
			{
				// Go to next device
				ALOGI("lrffp Switching %s to bootloader %s\n", deviceName, deviceNames[deviceId]);
				if (dev->enterBootMode())
					break;

				ALOGE("lrffp Can't switch to bootloader\n");
				DeviceFactory::destroyDevice(dev);
				// Go to next device
				deviceId++;
				dev = DeviceFactory::getDevice(deviceId);
				if (dev == NULL)
					manage_failure(fdStream, "lrffp Device not supported\n");
				dev->setSpeed(deviceSpeed);
				dev->setFirmwareType(telit_firmware);
				if (!dev->initialize(fdStream, deviceName))
					manage_failure(fdStream, "lrffp Error checking stream\n");
			}
		} else {
			// Switch to bootloader
			ALOGI("lrffp Switching %s to bootloader %s\n", deviceName, deviceNames[deviceId]);
			if (!dev->enterBootMode())
				manage_failure(fdStream, "lrffp Can't switch to bootloader\n");
		}
		if (deviceId > DEVICE_RFN_MESH)
			manage_failure(fdStream, "lrffp Can't switch to bootloader\n");

		// Flash
		if (!dev->uploadStream())
			manage_failure(fdStream, "lrffp Error uploading stream\n");
	} else if (isInBootloader) {
		// Just flash firmware
		if (!dev->uploadStream())
			manage_failure(fdStream, "lrffp Error uploading stream\n");
	}

	ALOGI("lrffp Stream uploaded successfully\n");
	DeviceFactory::destroyDevice(dev);

	exit(EXIT_SUCCESS);
}

