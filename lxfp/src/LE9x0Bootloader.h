#ifndef _LE9x0_BOOTLOADER_H_
#define _LE9x0_BOOTLOADER_H_

#include "Bootloader.h"

class LE9x0Bootloader: public Bootloader {
    protected:
        static uint8_t resetChar[1];
        static uint8_t nackChar[1];

        void initMessages(void);
    public:
        LE9x0Bootloader() : Bootloader(120 * 1000) { initMessages(); }
        file_descriptor bootModeStrategy(const int fd_device, const char* deviceName);
};
#endif
