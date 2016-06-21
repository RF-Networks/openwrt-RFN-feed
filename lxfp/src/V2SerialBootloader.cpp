#include "V2SerialBootloader.h"

uint8_t V2SerialBootloader::acknowledge[] = { 0x92, 0x00, 0x00 };

void V2SerialBootloader::initMessages(void) {
    setAcknowledgePositive(acknowledge, sizeof(acknowledge));
    setBootString(Bootloader::bootChar, sizeof(Bootloader::bootChar));
}
