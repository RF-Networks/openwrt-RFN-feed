#include "lxfpError.h"
#include "Device.h"
#include "log.h"

#include <errno.h>

using namespace std;

bool Device::changeBaudRate(uint8_t br) {
    struct termios serCfg;
    speed_t speed;
    err = E_SUCCESS;

    memset(&serCfg, 0, sizeof(serCfg));

    switch(br) {
      case 2:
        speed = B230400;
        break;
      case 3:
        speed = B460800;
        break;
      case 1:
      default:
        speed = B115200;
    }

    if (tcgetattr(fd_device, &serCfg) != 0) {
        err = E_OSCALL;
        goto end;
    }

    cfmakeraw(&serCfg);
    if (cfsetispeed(&serCfg, speed) == -1) {
        err = E_OSCALL;
        goto end;
    }

    if (cfsetospeed(&serCfg, speed) == -1) {
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

bool Device::initialize(int &stream) {
    return uploader->initializeStream(stream);
}

bool Device::enterBootMode(const char* deviceName) {
    bool retval = false;
    ALOGW("xfp enterBootMode Power on the device to start flashing...\n");

    if (!openDevice(deviceName))
        return false;

    if (!changeBaudRate(1)) {
        ALOGE("xfp enterBootMode Unable to set baudrate\n");
        err = E_OSCALL;
    } else {
        fd_device = bootloader->bootModeStrategy(fd_device, deviceName);
    }

    if (E_SUCCESS == err && E_SUCCESS == bootloader->getError())
    {
        ALOGI("xfp enterBootMode Boot mode OK\n");
        retval = true;
    }
    else
    {
        ALOGE("xfp enterBootMode Boot mode FAIL\n");
        close(fd_device);
    }


    return retval;
}

bool Device::uploadStream() {
    return uploader->uploadStreamStrategy(this);
}

int Device::getError() {
    return err;
}

char *Device::getRestartCmd() {
    return NULL;
}

Device::~Device() {
    if (NULL != bootloader) {
        delete bootloader;
        bootloader = NULL;
    }

    if (NULL != uploader) {
        delete uploader;
        uploader = NULL;
    }

    close(fd_device);
}

uint16_t Device::getAcceptedPacketSize(void) const {
    return uploader->acceptedPacketSize;
}

uint16_t Device::getAcknowledgeDelay(void) const {
    return uploader->acknowledgeDelay;
}

void Device::getAcknowledgeFirstBlock(uint8_t* data) const {
    memcpy(data,
           uploader->acknowledgeFirstBlock,
           uploader->acknowledgeFirstBlockLen);
}

uint16_t Device::getAcknowledgeFirstBlockLen(void) const {
    return uploader->acknowledgeFirstBlockLen;
}

void Device::getAcknowledgePositive(uint8_t* data) const {
    memcpy(data,
           bootloader->acknowledgePositive,
           bootloader->acknowledgePositiveLen);
}

uint16_t Device::getAcknowledgePositiveLen(void) const {
    return bootloader->acknowledgePositiveLen;
}

uint32_t Device::getBootDelay(void) const {
    return bootloader->bootDelay;
}

void Device::getBootString(uint8_t* data) const {
    memcpy(data,
           bootloader->bootString,
           bootloader->bootStringLen);
}

size_t Device::getBootStringLen(void) const {
    return bootloader->bootStringLen;
}

int Device::getCounter(void) const {
    return counter;
}

int Device::getMaxRetry(void) const {
    return bootloader->maxRetry;
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
        ALOGE("xfp enterBootMode Unable to open device\n");
        retval = false;
    }
    return retval;
}


