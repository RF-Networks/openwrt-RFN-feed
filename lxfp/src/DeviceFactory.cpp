#include "lxfp.h"

#include "AltairFamily.h"
#include "DeviceFactory.h"
#include "GeBootloader.h"
#include "HeBootloader.h"
#include "HeFamily.h"
#include "LE9x0Bootloader.h"
#include "UploaderFirstAckVariant.h"
#include "V2SerialBootloader.h"
#include "xE910V2UsbBootloader.h"
#include "LeV2Bootloader.h"

Device* DeviceFactory::getDevice(int deviceId, int usbFlag) {
    switch (deviceId) {
        case DEVICE_HE863:
            {
                Bootloader* bl = new HeBootloader(usbFlag);
                Uploader* up = new UploaderFirstAckVariant();
                return new HeFamily(bl, up);
            }
            break;
        case DEVICE_V2:
            if (usbFlag) {
                return NULL;
            } else {
                Bootloader* bl = new V2SerialBootloader();
                Uploader* up = new Uploader();
                return new Device(bl, up);
            }
            break;
        case DEVICE_UC:
            {
                Bootloader* bl = new Bootloader(65 * 1000);
                Uploader* up = new Uploader();
                return new Device(bl, up);
            }
            break;
        case DEVICE_GE:
            {
                Bootloader* bl = new GeBootloader(usbFlag);
                Uploader* up = new UploaderFirstAckVariant();

                if(!usbFlag)
                    up->setAcknowledgeDelay(1000);

                return new Device(bl, up);
            }
            break;
        case DEVICE_DE:
            {
                Bootloader* bl = new Bootloader();
                bl->setBootStartDelay(1 * 1000 * 1000);

                uint16_t packetSize = 256;
                Uploader* up = new Uploader(packetSize);

                return new Device(bl, up);
            }
            break;
        case DEVICE_xE910V2:
            {
                Bootloader* bl = NULL;
                Uploader* up = new Uploader();

                if (usbFlag) {
                    bl = new xE910V2UsbBootloader();
                    bl->setRestartDelay(2000 * 1000);
                    up->setAcknowledgeDelay(1000);
                    up->setAcceptedPacketSize(256);

                } else {
                    bl = new Bootloader(120 * 1000);
                }

                return new Device(bl, up);
            }
            break;
        case DEVICE_LE:
            {
                Bootloader* bl = new LE9x0Bootloader();
                Uploader* up = new Uploader();
                up->setAcceptedPacketSize(512);
                return new Device(bl, up);
            }
            break;
        case DEVICE_ALTAIR:
            if (usbFlag) {
                msec bootDelay = 120 * 1000;
                int maxRetry = 1000;

                Bootloader* bl = new Bootloader(bootDelay, maxRetry, usbFlag);
                Uploader* up = new Uploader();

                return new AltairFamily(bl, up);
            }
            else {
                return NULL;
            }
            break;
        case DEVICE_LEV2:
            {
                if (usbFlag) {
                    Bootloader* bl = new LeV2Bootloader(usbFlag);
                    Uploader* up = new UploaderFirstAckVariant();
                    return new HeFamily(bl, up);
                }
                else {
                    return NULL;
                }
            }
            break;
        default:
            return NULL;
    }
}

void DeviceFactory::destroyDevice(Device *dev) {
    if (NULL != dev) {
        delete dev;
        dev = NULL;
    }
}
