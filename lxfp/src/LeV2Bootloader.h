#ifndef _LEV2_BOOTLOADER_H_
#define _LEV2_BOOTLOADER_H_

#include "Bootloader.h"

class LeV2Bootloader: public Bootloader {
    protected:
        static uint8_t acknowledge[28];
        static uint8_t bootCharSerial[2];
        static uint8_t bootCharUsb[2];

        bool compare(DataSmallBlock *tbc);
        void initMessages(void);

    public:
        LeV2Bootloader(const bool isUsbBootloader);
};
#endif
