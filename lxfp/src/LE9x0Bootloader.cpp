#include "LE9x0Bootloader.h"
#include "lxfpError.h"

#define BOOT_CHARS_NEEDED 12
#define PORT_OPEN_DELAY (100 * 1000)

uint8_t LE9x0Bootloader::resetChar[] = { 0xA1 };
uint8_t LE9x0Bootloader::nackChar[] = { 0xB6 };

void LE9x0Bootloader::initMessages(void) {
    Bootloader::initMessages();
    setAcknowledgeNegative(nackChar, sizeof(nackChar));
    setResetString(resetChar, sizeof(resetChar));
}

int LE9x0Bootloader::bootModeStrategy(const int fd_device,
                                       const char* deviceName) {
    int writesCount = 0;
    ssize_t bytesRead = 0;
    ssize_t bytesWrite = 0;
    DataSmallBlock acknowledge;
    int counter = 1000;
    int fd_bootld;

    err = E_SUCCESS;
    acknowledge.len = acknowledgePositiveLen;

    while (maxRetry--) {
        bytesWrite = write(fd_device, bootString, bootStringLen);
        writesCount++;

        // if we sent enough boot chars and device is no more writable
        // means it is rebootiing so we wait for new decice
        if ((bytesWrite < 0) && (writesCount >= BOOT_CHARS_NEEDED))
        {
            close(fd_device); // close old device waiting for new
            ALOGI("waiting for device to reboot in ACM device\n");

            while ( ((fd_bootld = open(deviceName, O_RDWR | O_NONBLOCK)) < 0) &&
                    counter-- ) {
                usleep(PORT_OPEN_DELAY);
            }

            if (counter == 0) {
                err = E_DEVICE_NOT_OPEN;
                ALOGE("xfp enterBootMode Unable to open device\n");
                return false;
            }

            bytesWrite = write(fd_bootld, bootString, bootStringLen);
            usleep(bootDelay);
            if (bytesWrite == bootStringLen)
            {
                bytesRead = read(fd_bootld,
                                 acknowledge.data,
                                 acknowledgePositiveLen);
                if (bytesRead == acknowledgePositiveLen)
                {
                    if (compare(&acknowledge))
                    {
                        goto end;
                    }
                }
            }
        }
        usleep(bootDelay);
    }

    if (maxRetry == -1)
        err = E_FLASHER_BOOT;

end:
    if (E_SUCCESS != err) {
        ALOGE("xfp LE9x0 enterBootMode Boot mode FAIL\n");
        close(fd_bootld);
    }

    return fd_bootld;
}
