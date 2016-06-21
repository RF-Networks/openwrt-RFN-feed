#ifndef _HE_FAMILY_H_
#define _HE_FAMILY_H_

#if !defined(ANDROID_CHANGES)
#include <iostream>
#include <fstream>
#endif
#include <cstdlib>
#include <cstring>

#include "Device.h"

using namespace std;

class HeFamily: public Device {
protected:
    char *getRestartCmd() {
        static char cmd[] = "AT#SHDN=5\r";
        return cmd;
    }
public:
    HeFamily(Bootloader* bootloader, Uploader* uploader):
        Device(bootloader, uploader){}
};

#endif /* _HE_FAMILY_H_ */
