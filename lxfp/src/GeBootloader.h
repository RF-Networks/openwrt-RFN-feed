#ifndef _GE_BOOTLOADER_H_
#define _GE_BOOTLOADER_H_

#include "Bootloader.h"

class GeBootloader: public Bootloader {
    protected:
        static uint8_t acknowledge[12];
        static uint8_t bootCharSerial[2];
        static uint8_t bootCharUsb[4];

        bool compare(DataSmallBlock *tbc);
        void initMessages(void);

    public:
        GeBootloader(const bool isUsbBootloader);
};
#endif
