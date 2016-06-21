#include "UploaderFirstAckVariant.h"

#define FIRST_BLOCK_NACK_CHAR 0xFF

uint8_t UploaderFirstAckVariant::acknowledgeFirstBlock[] = {
    0x01, 0x01, 0xA5
};

UploaderFirstAckVariant::UploaderFirstAckVariant(void):
    Uploader() {
        setAcknowledgeFirstBlock(acknowledgeFirstBlock,
                                 sizeof(acknowledgeFirstBlock));
    }

bool UploaderFirstAckVariant::isAckFirstBlock(uint8_t *block) {
    int i;

    for (i = 0; i < 3; i++)
        ALOGD("xfp isAckFirstBlock byte %d %x\n", i, block[i]);

    return ( (block[0] == acknowledgeFirstBlock[0]) &&
             (block[1] == acknowledgeFirstBlock[1]) &&
             (block[2] == acknowledgeFirstBlock[2]));
}

bool UploaderFirstAckVariant::isNackFirstBlock(uint8_t *block) {
    return (block[0] == FIRST_BLOCK_NACK_CHAR);
}
