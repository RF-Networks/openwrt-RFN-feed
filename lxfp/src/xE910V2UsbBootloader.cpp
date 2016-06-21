#include "xE910V2UsbBootloader.h"
#include "lxfpError.h"

#define PORT_OPEN_DELAY (100 * 1000)

uint8_t xE910V2UsbBootloader::resetChar[] = { 0xA1 };

void xE910V2UsbBootloader::initMessages(void) {
    setAcknowledgePositive(resetChar, sizeof(resetChar));
    setBootString(Bootloader::bootChar, sizeof(Bootloader::bootChar));
}

file_descriptor xE910V2UsbBootloader::bootModeStrategy(const int fdDevice,
                                            const char* deviceName){
    int counter = 1000;
    int fdBootLd;

    ALOGW("First boot start\n");

    Bootloader::bootModeStrategy(fdDevice, deviceName);

    if (E_SUCCESS == err) {
        ALOGW("First boot OK. Preparing second boot...\n");

        close(fdDevice);

        setAcknowledgePositive(Bootloader::acknowledge, sizeof(Bootloader::acknowledge));
        setMaxRetry(2);
        delayRestart();

        while ( ((fdBootLd = open(deviceName, O_RDWR | O_NONBLOCK)) < 0) &&
                counter-- ) {
            usleep(PORT_OPEN_DELAY);
        }

        if (counter <= 0) {
            err = E_DEVICE_NOT_OPEN;
            ALOGE("xfp enterBootMode Unable to open device\n");
        } else {
            ALOGI("Second boot start\n");
            Bootloader::bootModeStrategy(fdBootLd, deviceName);
        }
    }

    return fdBootLd;
}
