#include "HeBootloader.h"


uint8_t HeBootloader::acknowledge [] = {
    0xF0, 0x16, 0x51, 0x92, 0x02, 0x00, 0x15, 0x00,
    0x00, 0x00, 0x69, 0xEA, 0x0D, 0x60, 0x11, 0x24,
    0x41, 0xA4, 0x4A, 0x00, 0x00, 0x20, 0xFF, 0xFF
};
uint8_t HeBootloader::bootCharUsb [] = { 0x41, 0x54, 0x41, 0x54 };
uint8_t HeBootloader::bootCharSerial [] = { 0x41, 0x54 };

HeBootloader::HeBootloader(const bool isUsbBootloader) :
    Bootloader(60 * 1000, 1000, isUsbBootloader) {

        initMessages();

        if(isUsbBootloader)
            setMaxRetry(1);
    }

void HeBootloader::initMessages(void) {
    setAcknowledgePositive(acknowledge, sizeof(acknowledge));

    if(isUsbBootloader)
        setBootString(bootCharUsb, sizeof(bootCharUsb));
    else
        setBootString(bootCharSerial, sizeof(bootCharSerial));
}

bool HeBootloader::compare(DataSmallBlock *tbc) {
    int i;

    if (tbc->data[0]  == acknowledge[0]    &&
        tbc->data[1]  == acknowledge[1]    &&
        tbc->data[22] == acknowledge[22]  &&
        tbc->data[23] == acknowledge[23])
        return true;

    for (i = 0; i < 24; i++)
        ALOGD("xfp compare Boot answer byte %d %x\n", i, tbc->data[i]);

    return false;
}
