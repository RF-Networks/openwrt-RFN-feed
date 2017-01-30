#include <iostream>
#include <fstream>
#include <error.h>
#include "log.h"
#include <cstdlib>
#include <cstring>
#include <string.h>

#include <getopt.h>
#include <stdint.h>
#include <termios.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <dirent.h>
#include <stdlib.h>
#include <unistd.h>
#include <libgen.h>

#include "lrffp.h"
#include "DeviceFactory.h"
#include "Device.h"

using namespace std;

static int verbose_flag = 0;
static int deviceId = 0;
static int telit_firmware = 0;
static Device* dev = NULL;
static char* deviceName;
static int deviceSpeed = 1;
static int bootloader_check = 0;

static const char* deviceNames[] = {
    "All",
	"RFN",
	"Mesh",
	"Star"
};

static void identify_device(char *selection) {
	switch (*selection) {
		case DEVICE_ALL_SELECTION:
			deviceId = DEVICE_ALL;
			break;
		case DEVICE_TAG_READER_ROUTER_SELECTION:
			deviceId = DEVICE_TAG_READER_ROUTER;
			break;
		case DEVICE_COORDINATOR_SELECTION:
			deviceId = DEVICE_COORDINATOR;
			break;
		case DEVICE_STAR_SELECTION:
			deviceId = DEVICE_STAR;
			break;
		default:
			ALOGE("lrffp identify_device Device code not recognized: aborting...\n");
			exit(EXIT_FAILURE);
	}
}

static void identify_speed(char *selection) {
	switch (*selection) {
		case DEVICE_SPEED_SELECTION_115200:
			deviceSpeed = DEVICE_SPEED_115200;
			break;
		case DEVICE_SPEED_SELECTION_19200:
			deviceSpeed = DEVICE_SPEED_19200;
			break;
		default:
			ALOGE("default speed 19200\n");
			deviceSpeed = DEVICE_SPEED_19200;
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
		c = getopt_long(argc, argv, "d:s:vhb", long_options, &option_index);

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

    if (fileStream < 0) {
        ALOGE("lrffp check_stream_file Error opening the stream\n");
        exit(EXIT_FAILURE);
    }
}

void manage_failure(ifstream &fs, const char *msg) {
    fs.close();
    if (dev != NULL)
        DeviceFactory::destroyDevice(dev);
    ALOGE("%s", msg);
    exit(EXIT_FAILURE);
}

int main(int argc, char *argv[]) {
	bool enterflashMode = true;
	ifstream fdStream;
	check_args(argc, argv);

	if (!bootloader_check && deviceId == DEVICE_ALL)
		deviceId = DEVICE_TAG_READER_ROUTER;

	ALOGI("lrffp Device chosen: %s\n", deviceNames[deviceId]);

	check_stream_file(argc, argv, fdStream);

	deviceName = argv[optind++];

	if (deviceId == DEVICE_ALL && bootloader_check)
	{
		// Try to switch to bootloader
		do {
			switch (deviceId)
			{
				case DEVICE_ALL:
					deviceId = DEVICE_TAG_READER_ROUTER;
					break;
				case DEVICE_TAG_READER_ROUTER:
					deviceId = DEVICE_COORDINATOR;
					break;
				case DEVICE_COORDINATOR:
					deviceId = DEVICE_STAR;
					break;
			}
			dev = DeviceFactory::getDevice(deviceId);
			if (dev == NULL)
				manage_failure(fdStream, "lrffp Device not supported\n");

			dev->setType(deviceId);
			dev->setSpeed(deviceSpeed);
			dev->setFirmwareType(telit_firmware);

			if (verbose_flag)
				set_log_level(LOG_LEVEL_VERBOSE);

			fdStream.seekg(0, fdStream.beg);
			if (!dev->initialize(fdStream, deviceName))
				manage_failure(fdStream, "lrffp Error checking stream\n");
			sleep(1);

			if (bootloader_check) {
				ALOGI("lrffp Switching %s to bootloader %s\n", deviceName, deviceNames[deviceId]);
				if (!dev->enterBootMode()) {
					//manage_failure(fdStream, "lrffp Error switching to bootloader\n");
				}
				else {
					enterflashMode = false;
					break;
				}
			}

			DeviceFactory::destroyDevice(dev);
		} while (deviceId != DEVICE_STAR);
		sleep(1);
		if (dev == NULL)
			manage_failure(fdStream, "lrffp Error switching to bootloader\n");
	}
	else
	{
		dev = DeviceFactory::getDevice(deviceId);

		if (dev == NULL)
			manage_failure(fdStream, "lrffp Device not supported\n");

		dev->setType(deviceId);
		dev->setSpeed(deviceSpeed);
		dev->setFirmwareType(telit_firmware);

		if (verbose_flag)
			set_log_level(LOG_LEVEL_VERBOSE);

		if (!dev->initialize(fdStream, deviceName))
			manage_failure(fdStream, "lrffp Error checking stream\n");
		sleep(1);

		if (bootloader_check) {
			ALOGI("lrffp Switching %s to bootloader\n", deviceName);
			if (!dev->enterBootMode()) {
				manage_failure(fdStream, "lrffp Error switching to bootloader\n");
			}
			sleep(1);
		}
	}

	if (!dev->uploadStream(enterflashMode))
		manage_failure(fdStream, "lrffp Error uploading stream\n");

	ALOGI("lrffp Stream uploaded successfully\n");
	DeviceFactory::destroyDevice(dev);
	exit(EXIT_SUCCESS);
}

