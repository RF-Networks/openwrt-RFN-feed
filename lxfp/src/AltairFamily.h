#ifndef _ALTAIR_FAMILY_H_
#define _ALTAIR_FAMILY_H_

#include "Device.h"

class AltairFamily: public Device {
    public:
        AltairFamily(Bootloader* bootloader, Uploader* uploader):
            Device(bootloader, uploader) {
                bootLoaderVID = const_cast<char*>("216f");
                bootLoaderPID = const_cast<char*>("0051");
            }
};

#endif /* _ALTAIR_FAMILY_H_ */
