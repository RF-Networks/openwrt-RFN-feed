#ifndef _HE_BOOTLOADER_H_
#define _HE_BOOTLOADER_H_

#include "Bootloader.h"

class HeBootloader: public Bootloader {
    protected:
        static uint8_t acknowledge[24];
        static uint8_t bootCharSerial[2];
        static uint8_t bootCharUsb[4];

        bool compare(DataSmallBlock *tbc);
        void initMessages(void);

    public:
        HeBootloader(const bool isUsbBootloader);
};
#endif
