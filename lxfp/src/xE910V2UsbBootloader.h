#ifndef _XE910V2_USB_BOOTLOADER_
#define _XE910V2_USB_BOOTLOADER_

#include "Bootloader.h"

class xE910V2UsbBootloader: public Bootloader {
    protected:
        static uint8_t resetChar[1];

        void initMessages(void);

    public:
        xE910V2UsbBootloader(void) :
            Bootloader(120 * 1000, 10, true) { initMessages(); }
        virtual file_descriptor bootModeStrategy(const int fdDevice,
                                                 const char* deviceName);
};
#endif
