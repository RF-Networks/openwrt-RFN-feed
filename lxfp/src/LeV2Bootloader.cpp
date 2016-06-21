#include "LeV2Bootloader.h"


uint8_t LeV2Bootloader::acknowledge [] = {
    0xF1, 0x1C, 0x54, 0x35,
    0x05, 0x00, 0x15, 0x00,
    0x00, 0x00, 0x20, 0x11,
    0x00, 0x02, 0x00, 0x1C,
    0x8C, 0x13, 0x51, 0x50,
    0x6E, 0x2D, 0x92, 0x31,
    0x00, 0x20, 0x00, 0xFF
};
uint8_t LeV2Bootloader::bootCharUsb [] = { 0x41, 0x54 };
uint8_t LeV2Bootloader::bootCharSerial [] = { 0x41, 0x54 };

LeV2Bootloader::LeV2Bootloader(const bool isUsbBootloader) :
    Bootloader(60 * 1000, 1000, isUsbBootloader) {

        initMessages();

        if(isUsbBootloader)
            setMaxRetry(2);
    }

void LeV2Bootloader::initMessages(void) {
    setAcknowledgePositive(acknowledge, sizeof(acknowledge));

    if(isUsbBootloader)
        setBootString(bootCharUsb, sizeof(bootCharUsb));
    else
        setBootString(bootCharSerial, sizeof(bootCharSerial));
}

bool LeV2Bootloader::compare(DataSmallBlock *tbc) {
    int i;

    if (tbc->data[0] == acknowledge[0] &&
        tbc->data[1] == acknowledge[1] &&
        tbc->data[26] == acknowledge[26] &&
        tbc->data[27] == acknowledge[27])
        return true;

    for (i = 0; i < 28; i++)
        ALOGD("xfp compare Boot answer byte %d %x\n", i, tbc->data[i]);

    return false;
}
