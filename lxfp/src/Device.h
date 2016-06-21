#ifndef DEVICE_H_
#define DEVICE_H_

#if defined(ANDROID_CHANGES)
#include <stdio.h>
#include <time.h>
#include <utils/Log.h>
#else
#include <iostream>
#include <fstream>
#endif
#include <cstdlib>
#include <cstring>

#include <sys/ioctl.h>
#include <sys/types.h>
#include <termios.h>

#include "Bootloader.h"
#include "Uploader.h"
#include "log.h"

using namespace std;

#define ANSWER_MAX_SIZE 128
#define PORT_OPEN_DELAY (100 * 1000)
#define BYTES_IN_BUFFER_DELAY 1000000

class Device {
protected:
    Bootloader* bootloader;
    Uploader* uploader;
    int fd_device;
    int err;
    int counter;
    int type;

    uint8_t deviceSpeed;
    char* bootLoaderVID;
    char* bootLoaderPID;

public:
    Device(Bootloader* bootloader, Uploader* uploader):
        bootloader(bootloader),
        uploader(uploader),
        counter(1000),
        bootLoaderVID(const_cast<char*>("")),
        bootLoaderPID(const_cast<char*>("")) {}

    bool changeBaudRate(uint8_t br);

    bool hasBootLoaderVID(const char* pVid) const {
        return (0 == strncmp(bootLoaderVID, pVid, 5));
    }
    bool hasBootLoaderPID(const char* pPid) const {
        return (0 == strncmp(bootLoaderPID, pPid, 5));
    }
    const char* getBootLoaderVID(void) const {
        if(bootLoaderVID)
            return bootLoaderVID;
        else
            return "";
    }
    const char* getBootLoaderPID(void) const {
        if(bootLoaderPID)
            return bootLoaderPID;
        else
            return "";
    }

    void setBootDelay(uint32_t delay) {
        bootloader->setBootDelay(delay * 1000);
    }

    void setDeviceSpeed(uint8_t devSpeed) {
        deviceSpeed = devSpeed;
    }

    void setType(int t) {
        type = t;
    }

    virtual bool initialize(int &stream);
    virtual bool enterBootMode(const char* deviceName);
    virtual bool uploadStream();
    virtual int getError();
    virtual char *getRestartCmd();
    virtual ~Device();

    bool openDevice(const char* deviceName);
    int getCounter(void) const;
    int getMaxRetry(void) const;
    size_t getBootStringLen(void) const;
    uint16_t getAcceptedPacketSize(void) const;
    uint16_t getAcknowledgeDelay(void) const;
    uint16_t getAcknowledgeFirstBlockLen(void) const;
    uint16_t getAcknowledgePositiveLen(void) const;
    uint32_t getBootDelay(void) const;
    void getAcknowledgeFirstBlock(uint8_t* data) const;
    void getAcknowledgePositive(uint8_t* data) const;
    void getBootLoaderPID(char* data) const;
    void getBootLoaderVID(char* data) const;
    void getBootString(uint8_t* data) const;
    int getFileDescriptor(void) const { return fd_device; }
    uint8_t getDeviceSpeed(void) const { return deviceSpeed; }
    uint8_t getType(void) const { return type; }
};

#endif /* DEVICE_H_ */
