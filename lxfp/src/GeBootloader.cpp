#include "GeBootloader.h"


uint8_t GeBootloader::acknowledge [] = {
    0xF0, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0xFF
};
uint8_t GeBootloader::bootCharUsb [] = { 0x41, 0x54, 0x41, 0x54 };
uint8_t GeBootloader::bootCharSerial [] = { 0x41, 0x54 };

GeBootloader::GeBootloader(const bool isUsbBootloader) :
    Bootloader(60 * 1000, 1000, isUsbBootloader) {

        initMessages();

        if(isUsbBootloader)
            setMaxRetry(1);
    }

void GeBootloader::initMessages(void) {
    setAcknowledgePositive(acknowledge, sizeof(acknowledge));

    if(isUsbBootloader)
        setBootString(bootCharUsb, sizeof(bootCharUsb));
    else
        setBootString(bootCharSerial, sizeof(bootCharSerial));
}

bool GeBootloader::compare(DataSmallBlock *tbc) {
    int i;

    if (tbc->data[0]  == acknowledge[0]    &&
        tbc->data[1]  == acknowledge[1]    &&
        tbc->data[11] == acknowledge[11])
        return true;

    for (i = 0; i < 12; i++)
        ALOGD("xfp compare Boot answer byte %d %x\n", i, tbc->data[i]);

    return false;
}
