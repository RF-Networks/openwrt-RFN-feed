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
#include "lrffpti.h"
#include "log.h"

#include "DeviceFactory.h"
#include "Device.h"

using namespace std;

static int verbose_flag = 0;
static int deviceId = 0;
static int is_hex = 0;
static Device* dev = NULL;
static char* deviceName;
static LibSerial::BaudRate deviceSpeed = LibSerial::BaudRate::BAUD_19200;
static int bootloader_check = 0;

static const char *deviceNames[] = { "All", "RFN-Mesh", "RFN-Star" };

static void identify_device(char *selection) {
	switch (*selection) {
	case DEVICE_ALL_SELECTION:
		deviceId = DEVICE_ALL;
		break;
	case DEVICE_RFN_MESH_SELECTION:
		deviceId = DEVICE_RFN_MESH;
		break;
	case DEVICE_RFN_STAR_SELECTION:
		deviceId = DEVICE_RFN_STAR;
		break;
	default:
		ALOGE(
				"lrffpti identify_device Device code not recognized: aborting...\n");
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

static void check_args(int argc, char *argv[]) {
	static struct option long_options[] = {
		{"device", required_argument, NULL, 'd'},
		{"speed", required_argument, NULL, 's'},
		{"verbose", no_argument, &verbose_flag, 1},
		{"version", no_argument, NULL, 'v'},
		{"help", no_argument, NULL, 'h'},
		{"enterbootloader", no_argument, &bootloader_check, 'b'},
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
		}
	}

	if ((argc - optind) != 2) {
		ALOGE("lrffpti check_args needed filename of the stream and the serial device\n");
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
	is_hex = !fn.compare("hex");
    fileStream.open(argv[optind++], ios::in);

    if (!fileStream.is_open()) {
        ALOGE("lrffpti check_stream_file Error opening the stream\n");
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

	if (!bootloader_check && deviceId == DEVICE_ALL)
		deviceId = DEVICE_RFN_MESH;

	system("mt7688_pinmux set spi_s gpio");
	system("mt7688_pinmux set pwm1 gpio");

	ALOGI("lrffpti Device chosen: %s\n", deviceNames[deviceId]);

	check_stream_file(argc, argv, fdStream);

	deviceName = argv[optind++];

	// Check if is already in bootloader
	dev = DeviceFactory::getDevice(DEVICE_RFN_STAR);
	if (dev == NULL)
		manage_failure(fdStream, "lrffpti Device not supported\n");
	dev->setIsHex(is_hex);
	dev->setSpeed(deviceSpeed);
	if (!dev->initialize(fdStream, deviceName))
		manage_failure(fdStream, "lrffpti Error checking stream\n");
	isInBootloader = dev->isInBootloader();
	if ((!isInBootloader) && (!bootloader_check)) {
		manage_failure(fdStream, "lrffpti Not in bootloader\n");
	}

	if (isInBootloader) {
		ALOGI("lrffpti Device is already in bootloader\n");
	} else {
		DeviceFactory::destroyDevice(dev);
		if (deviceId == DEVICE_ALL && bootloader_check) {
			// Try to switch to bootloader
			do {
				switch (deviceId)
				{
					case DEVICE_ALL:
						deviceId = DEVICE_RFN_MESH;
						break;
					case DEVICE_RFN_MESH:
						deviceId = DEVICE_RFN_STAR;
						break;
				}
				dev = DeviceFactory::getDevice(deviceId);
				if (dev == NULL)
					manage_failure(fdStream, "lrffpti Device not supported\n");

				dev->setType(deviceId);
				dev->setIsHex(is_hex);
				dev->setSpeed(deviceSpeed);

				fdStream.seekg(0, fdStream.beg);
				if (!dev->initialize(fdStream, deviceName))
					manage_failure(fdStream, "lrffpti Error checking stream\n");
				std::this_thread::sleep_for(std::chrono::seconds(1));

				ALOGI("lrffpti Switching %s to bootloader %s\n", deviceName, deviceNames[deviceId]);
				isInBootloader = dev->enterBootMode();
				if (isInBootloader)
					break; // Bootloader entered no need to destroy device
				DeviceFactory::destroyDevice(dev);
				dev = nullptr;
			} while (deviceId != DEVICE_RFN_STAR);
			std::this_thread::sleep_for(std::chrono::seconds(1));
			if (dev == nullptr)
				manage_failure(fdStream, "lrffpti Error switching to bootloader\n");
		} else {
			dev = DeviceFactory::getDevice(deviceId);

			if (dev == NULL)
				manage_failure(fdStream, "lrffpti Device not supported\n");

			dev->setType(deviceId);
			dev->setSpeed(deviceSpeed);
			dev->setIsHex(is_hex);

			fdStream.seekg(0, fdStream.beg);
			if (!dev->initialize(fdStream, deviceName))
				manage_failure(fdStream, "lrffpti Error checking stream\n");
			std::this_thread::sleep_for(std::chrono::seconds(1));

			ALOGI("lrffpti Switching %s to bootloader %s\n", deviceName, deviceNames[deviceId]);
			isInBootloader = dev->enterBootMode();
			if (!isInBootloader) {
				manage_failure(fdStream, "lrffpti Error switching to bootloader\n");
			}
			std::this_thread::sleep_for(std::chrono::seconds(1));
		}
	}

	ALOGI("lrffpti Bootloader entered. Flashing...\n");

	std::this_thread::sleep_for(std::chrono::seconds(1));
	if (!dev->uploadStream())
		manage_failure(fdStream, "lrffpti Error uploading stream\n");

	ALOGI("lrffpti Stream uploaded successfully\n");

	system("mt7688_pinmux set spi_s gpio");
	system("mt7688_pinmux set pwm1 gpio");
	exit(EXIT_SUCCESS);
}


