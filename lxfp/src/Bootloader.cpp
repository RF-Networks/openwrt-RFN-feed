#include <unistd.h>
#include <string.h>

#include "Bootloader.h"
#include "lxfpError.h"

uint8_t Bootloader::acknowledge [] = { 0xA0 };
uint8_t Bootloader::bootChar [] = { 0x55 };

void Bootloader::initMessages(void) {
    setAcknowledgePositive(acknowledge, sizeof(acknowledge));
    setBootString(bootChar, sizeof(bootChar));
}

void Bootloader::setAcknowledgePositive(uint8_t* acknowledgePositive, uint16_t len) {
    this->acknowledgePositive = acknowledgePositive;
    this->acknowledgePositiveLen = len;
}

void Bootloader::setAcknowledgeNegative(uint8_t* acknowledgeNegative, uint16_t len) {
    this->acknowledgeNegative = acknowledgeNegative;
    this->acknowledgeNegativeLen = len;
}

void Bootloader::setResetString(uint8_t* resetString, ssize_t len) {
    this->resetString = resetString;
    this->resetStringLen = len;
}

void Bootloader::setBootString(uint8_t* bootString, ssize_t len) {
    this->bootString = bootString;
    this->bootStringLen = len;
}

bool Bootloader::compare(DataSmallBlock *tbc) {
    int i;

    if ( memcmp(tbc->data, acknowledgePositive, acknowledgePositiveLen) == 0 )
        return true;

    for (i = 0; i < acknowledgePositiveLen; i++)
        ALOGD("xfp compare Boot answer byte %d %x\n", i, tbc->data[i]);

    return false;
}

bool Bootloader::validateFirstByte(DataSmallBlock *tbc) {
    if(tbc->data[0] != acknowledgePositive[0])
        ALOGE("First byte validation failed! Received 0x%X while 0x%X was expected.\n",
              tbc->data[0],
              acknowledgePositive[0]);
    return (tbc->data[0] == acknowledgePositive[0]);
}

file_descriptor Bootloader::bootModeStrategy(const int fd_device, const char* deviceName) {
    DataSmallBlock acknowledge;
    uint32_t delay = BYTES_IN_BUFFER_DELAY;
    ssize_t bytesAvailable = 0;
    ssize_t bytesRead = 0;
    ssize_t bytesWrite = 0;
    int origMaxRetries = maxRetry;

    err = E_SUCCESS;
    acknowledge.len = acknowledgePositiveLen;

    while (maxRetry--) {
        ALOGD("Send bootchar attempt: %d\n", origMaxRetries - maxRetry);
        bytesWrite = write(fd_device, bootString, bootStringLen);

        if (bytesWrite == bootStringLen) {
            usleep(bootDelay);

            bytesRead = read(fd_device, acknowledge.data, 1);
            if (bytesRead == 1) {
                if (!validateFirstByte(&acknowledge))
                    continue;
            } else
                continue;

            if (acknowledgePositiveLen == 1) {
                if (compare(&acknowledge)) {
                    goto end;
                } else {
                    continue;
                }
            } else {
wait_answer:
                ioctl(fd_device, FIONREAD, &bytesAvailable);
                if ( (bytesAvailable < (acknowledgePositiveLen - 1)) && delay ) {
                    delay--;
                    goto wait_answer;
                }

                if (read(fd_device, acknowledge.data + 1, acknowledgePositiveLen - 1) != -1) {
                    if (compare(&acknowledge)) {
                        goto end;
                    } else {
                        continue;
                    }
                } else
                    continue;
            }
        } else {
            ALOGE("write returned %d instead of %d\n", bytesWrite, bootStringLen);
        }
    }

    if (maxRetry == -1)
        err = E_FLASHER_BOOT;

end:
    return fd_device;
}

Bootloader::~Bootloader() {}

