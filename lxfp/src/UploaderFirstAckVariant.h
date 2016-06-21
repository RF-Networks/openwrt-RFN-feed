#ifndef _FIRST_BLOCK_ACK_UPLOADER_H_
#define _FIRST_BLOCK_ACK_UPLOADER_H_

#include "Uploader.h"

class UploaderFirstAckVariant: public Uploader {
    protected:
        static uint8_t acknowledgeFirstBlock[3];
        virtual bool isAckFirstBlock(uint8_t *x);
        virtual bool isNackFirstBlock(uint8_t *x);

    public:
        UploaderFirstAckVariant(void);
};
#endif
