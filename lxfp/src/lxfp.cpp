#if defined(ANDROID_CHANGES)
#include <utils/Log.h>
#else
#include <iostream>
#include <fstream>
#include <error.h>
#include "log.h"
#endif
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

#include "lxfpError.h"
#include "lxfp.h"
#include "streamData.h"
#include "DeviceFactory.h"
#include "Device.h"
#include "at.h"


#define MAX_STRING_SIZE 256
#define ONE_SECOND_IN_US 1 * 1000 * 1000
#define SYSDIR "/sys/bus/usb/devices/"
#define MAX_FULL_PATH_LENGTH 100
#define ID_LENGTH 5

using namespace std;

static int verbose_flag = 0;
static int usb_flag = 0;
static uint32_t boot_delay = 0;
static int deviceId = 1;
static int deviceSpeed = 0;
static Device* dev = NULL;
static char* deviceName;
static char read_buffer[MAX_STRING_SIZE];
static char atDevice[MAX_STRING_SIZE] = "";
static int bootloader_check = 0;

static const char* deviceNames[] = {
    "",
    "HE910/863 family",
    "V2 - V3 family",
    "UC family",
    "GE family",
    "DE family",
    "HE910-V2/HE920/UE910-V2",
    "LE family",
    "Altair family (LE866)",
    "LE V2 family"
};

static const char* connection[SUPPORTED_CONNECTIONS] = {
    "serial",
    "USB"
};

static void identify_device(char *selection)
{
    switch (*selection) {
        case DEVICE_HE863_SELECTION:
            deviceId = DEVICE_HE863;
            break;
        case DEVICE_V2_SELECTION:
            deviceId = DEVICE_V2;
            break;
        case DEVICE_UC_SELECTION:
            deviceId = DEVICE_UC;
            break;
        case DEVICE_GE_SELECTION:
            deviceId = DEVICE_GE;
            break;
        case DEVICE_DE_SELECTION:
            deviceId = DEVICE_DE;
            break;
        case DEVICE_xE910V2_SELECTION:
            deviceId = DEVICE_xE910V2;
            break;
        case DEVICE_LE_SELECTION:
            deviceId = DEVICE_LE;
            break;
        case DEVICE_ALTAIR_SELECTION:
            deviceId = DEVICE_ALTAIR;
            break;
        case DEVICE_LEV2_SELECTION:
            deviceId = DEVICE_LEV2;
            break;
        default:
            ALOGE("xfp identify_device Device code not recognized: aborting...\n");
            exit(EXIT_FAILURE);
    }
}

static void identify_speed(char *selection)
{
    switch (*selection) {
        case DEVICE_SPEED_SELECTION_230400:
            deviceSpeed = DEVICE_SPEED_230400;
            break;
        case DEVICE_SPEED_SELECTION_460800:
            deviceSpeed = DEVICE_SPEED_460800;
            break;
        case DEVICE_SPEED_SELECTION_115200:
        default:
            ALOGE("default speed 115200\n");
            deviceSpeed = DEVICE_SPEED_115200;
    }
}

static void check_args(int argc, char *argv[])
{
    static struct option long_options[] = {
        {"device", required_argument, NULL, 'd'},
        {"speed", required_argument, NULL, 's'},
        {"usb", no_argument, &usb_flag, 1},
        {"verbose", no_argument, &verbose_flag, 1},
        {"version", no_argument, NULL, 'v'},
        {"help", no_argument, NULL, 'h'},
        {"restart", required_argument, NULL, 'r'},
        {"timeinterval", required_argument, NULL, 't'},
        {"bootloadercheck", no_argument, &bootloader_check, 'b'},
        {0, 0, 0, 0}
    };
    int option_index = 0;
    int c;

    for (;;) {
        c = getopt_long(argc, argv, "d:s:uvhr:t:b", long_options, &option_index);

        if (c == -1)
            break;

        switch(c) {
            case 'd':
                identify_device(optarg);
                break;
            case 's':
                identify_speed(optarg);
                break;
            case 't':
                if (strtol(optarg, NULL, 10) > 0)
                    boot_delay = strtoul(optarg, NULL, 10);
                else
                    boot_delay = 0;
                break;
            case 'r':
                strncpy(atDevice, optarg, MAX_STRING_SIZE - 1);
                break;
            case 'u':
                usb_flag = 1;
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
        ALOGE("xfp check_args needed filename of the stream and the serial device\n");
        exit(EXIT_FAILURE);
    }
}

static void check_stream_file(int argc, char *argv[], int &fileStream)
{
    fileStream = open(argv[optind++], O_RDONLY | O_NONBLOCK);

    if (fileStream < 0) {
        ALOGE("xfp check_stream_file Error opening the stream\n");
        exit(EXIT_FAILURE);
    }
}

void manage_failure(int &fs, const char *msg) {
    close(fs);
    if (dev != NULL)
        DeviceFactory::destroyDevice(dev);
    ALOGE("%s", msg);
    exit(EXIT_FAILURE);
}

bool get_vid_pid(const char* pDir, char pVid[ID_LENGTH], char pPid[ID_LENGTH]) {
    FILE * file = NULL;
    char vidFile[MAX_FULL_PATH_LENGTH] = {0};
    char pidFile[MAX_FULL_PATH_LENGTH] = {0};

    memset(vidFile, 0, MAX_FULL_PATH_LENGTH);
    snprintf(vidFile, MAX_FULL_PATH_LENGTH, "%s/idVendor", pDir);

    memset(pidFile, 0, MAX_FULL_PATH_LENGTH);
    snprintf(pidFile, MAX_FULL_PATH_LENGTH, "%s/idProduct", pDir);

    if (NULL != (file = fopen(vidFile, "r"))) {
        fgets(pVid, ID_LENGTH, file);
        fclose(file);
    } else {
        return false;
    }


    if (NULL != (file = fopen(pidFile, "r"))) {
        fgets(pPid, ID_LENGTH, file);
        fclose(file);
    } else {
        return false;
    }

    return true;
}

bool is_bootloader_device(const char* pDeviceName, const Device* pDev) {
    DIR *parentDir;
    bool retval = false;
    char bootLoaderDevicePath[50];
    char dirFullPath[MAX_FULL_PATH_LENGTH] = {0};
    char pid[ID_LENGTH] = {0};
    char vid[ID_LENGTH] = {0};
    struct dirent *pCurDir;

    parentDir = opendir(SYSDIR);

    if(NULL == parentDir) {
        ALOGE("Could not open %s\n", SYSDIR);
        return false;
    }

    while(NULL != (pCurDir = readdir(parentDir))) {
        snprintf(dirFullPath, MAX_FULL_PATH_LENGTH, "%s%s", SYSDIR, pCurDir->d_name);

        if (!get_vid_pid(dirFullPath, vid, pid))
            continue;

        if(dev->hasBootLoaderVID(vid) && pDev->hasBootLoaderPID(pid)) {
            snprintf(bootLoaderDevicePath, 50, "%s%s", SYSDIR, pCurDir->d_name);
            break;
        }
    }
    closedir(parentDir);

    if(NULL != pCurDir) {
        DIR* subdir;
        char dirname[120];

        parentDir = opendir(bootLoaderDevicePath);

        if(NULL == parentDir) {
            ALOGE("could not open %s\n", bootLoaderDevicePath);
            return false;
        }

        while(NULL != (pCurDir = readdir(parentDir))) {
            memset(dirname, 0, 120);
            snprintf(dirname, 120, "%s/%s/tty/%s", bootLoaderDevicePath, pCurDir->d_name, pDeviceName);

            if (NULL != (subdir = opendir(dirname))) {
                retval = true;
                break;
            }
        }
        closedir(subdir);
        closedir(parentDir);
    }

    return retval;
}

int main(int argc, char *argv[]) {
    int fdStream;
    check_args(argc, argv);
    int timeForBootloaderDevice = 30;

    ALOGI("xfp Device chosen: %s\n", deviceNames[deviceId]);
    ALOGI("xfp Connection chosen: %s\n", connection[usb_flag]);

    check_stream_file(argc, argv, fdStream);

    deviceName = argv[optind++];

    dev = DeviceFactory::getDevice(deviceId, usb_flag);

    if (dev == NULL)
        manage_failure(fdStream, "xfp Device not supported with this kind of connection\n");

    dev->setType(deviceId);

    if(bootloader_check)
    {
        ALOGI("Waiting up to %d seconds for the expected Bootloader device (%s:%s) to connect\n",
              timeForBootloaderDevice,
              dev->getBootLoaderVID(),
              dev->getBootLoaderPID());

        while(!is_bootloader_device(basename(deviceName), dev) &&
              0 < timeForBootloaderDevice) {
            --timeForBootloaderDevice;
            usleep(ONE_SECOND_IN_US);
        }

        if (0 >= timeForBootloaderDevice)
            manage_failure(fdStream, "Could not find expected bootloader device\n");
    }

    if (verbose_flag)
        set_log_level(LOG_LEVEL_VERBOSE);

    if (!dev->initialize(fdStream))
        manage_failure(fdStream, "xfp Error checking stream\n");

    if (boot_delay > 0) {
        dev->setBootDelay(boot_delay);
        ALOGI("Forced boot delay %d ms\n", boot_delay);
    }

    if ( (deviceSpeed > 0) && !usb_flag) {
        dev->setDeviceSpeed(deviceSpeed);
        ALOGI("Setting device speed %d\n", deviceSpeed);
    }

    if (strlen(atDevice) > 0) {
        int fdDevice;
        char *restartCmd;

        restartCmd = dev->getRestartCmd();
        if (NULL == restartCmd)
            manage_failure(fdStream, "xfp Device does not support shutdown\n");

        ALOGI("xfp Restart device: %s\n", atDevice);

        fdDevice = open_device(atDevice);
        if (-1 == fdDevice)
            manage_failure(fdStream, "xfp unable to open the device for restart\n");

        if (send_verify(fdDevice,
                        restartCmd,
                        "OK",
                        read_buffer,
                        MAX_STRING_SIZE) <= 0)
            manage_failure(fdStream, "xfp error response to AT command\n");

        close(fdDevice);
    }

    if (!dev->enterBootMode(deviceName))
        manage_failure(fdStream, "xfp Error entering boot mode\n");

    if (!dev->uploadStream())
        manage_failure(fdStream, "xfp Error uploading stream\n");

    ALOGI("xfp Stream uploaded successfully\n");
    DeviceFactory::destroyDevice(dev);
    exit(EXIT_SUCCESS);
}
