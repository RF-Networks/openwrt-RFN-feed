#ifndef _BOOTLOADER_H_
#define _BOOTLOADER_H_

#include <sys/ioctl.h>
#include <unistd.h>

#include "streamData.h"
#if defined(ANDROID_CHANGES)
#include <utils/Log.h>
#else
#include "log.h"
#endif
#define BYTES_IN_BUFFER_DELAY 1000000

typedef uint32_t msec;
typedef int file_descriptor;

class Bootloader {
    friend class Device;

    protected:
    static uint8_t acknowledge[1];
    static uint8_t bootChar[1];

    int err;
    msec bootDelay;
    msec bootStartDelay;
    int maxRetry;
    msec restartDelay;
    ssize_t bootStringLen;
    ssize_t resetStringLen;
    uint16_t acknowledgeNegativeLen;
    uint16_t acknowledgePositiveLen;
    uint8_t* acknowledgeNegative;
    uint8_t* acknowledgePositive;
    uint8_t* bootString;
    uint8_t* resetString;
    bool isUsbBootloader;

    virtual bool compare(DataSmallBlock *tbc);
    virtual bool validateFirstByte(DataSmallBlock *tbc);
    virtual void initMessages(void);

    public:
    Bootloader(const msec bootDelay = 60 * 1000,
               const int maxRetry = 1000,
               const bool isUsbBootloader = false,
               const msec bootStartDelay = 0) :
        bootDelay(bootDelay),
        bootStartDelay(bootStartDelay),
        maxRetry(maxRetry),
        isUsbBootloader(isUsbBootloader) { initMessages(); }

    void setAcknowledgeNegative(uint8_t* acknowledgenegative, uint16_t len);
    void setAcknowledgePositive(uint8_t* acknowledgePositive, uint16_t len);
    void setBootDelay(const msec delay)     { bootDelay = delay; }
    void setBootStartDelay(const msec delay) { bootStartDelay = delay; }
    void setBootString(uint8_t* bootString, ssize_t len);
    void setMaxRetry(const int maxRetry)    { this->maxRetry = maxRetry; }
    void setResetString(uint8_t* resetString, ssize_t len);
    void setRestartDelay(const msec delay)  { restartDelay = delay; }
    void delayBootStart(void) {
        if (bootStartDelay)
            usleep(bootStartDelay);
    }
    void delayRestart(void) {
        if(restartDelay)
            usleep(restartDelay);
    }
    int getError(void) {return err; }

    virtual file_descriptor bootModeStrategy(const int fd_device, const char* deviceName);
    virtual ~Bootloader();

    int getMaxRetry(void) const;
    size_t getBootStringLen(void) const;
    uint16_t getAcknowledgePositiveLen(void) const;
    uint32_t getBootDelay(void) const;
    void getAcknowledgePositive(uint8_t* data) const;
    void getBootString(uint8_t* data) const;

};
# endif // _BOOTLOADER_H_
