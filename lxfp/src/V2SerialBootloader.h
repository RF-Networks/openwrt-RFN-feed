#ifndef _V2_SERIAL_BOOTLOADER_H_
#define _V2_SERIAL_BOOTLOADER_H_

#include "Bootloader.h"

class V2SerialBootloader: public Bootloader {
    protected:
        static uint8_t acknowledge[3];

        void initMessages(void);

    public:
        V2SerialBootloader(void) :
            Bootloader(120 * 1000, 1000, false) { initMessages(); }
};
#endif
