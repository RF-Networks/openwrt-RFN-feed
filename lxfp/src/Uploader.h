#ifndef _UPLOADER_H_
#define _UPLOADER_H_

#include "streamData.h"
#if defined(ANDROID_CHANGES)
#include <utils/Log.h>
#else
#include "log.h"
#endif

class Device;

class Uploader {
    friend class Device;

    protected:
        int fdStream;
        int err;
        static char progressBar[];
        StreamHeader header;
        uint8_t *acknowledgeFirstBlock;
        uint16_t acknowledgeFirstBlockLen;
        uint16_t acknowledgeDelay;
        uint16_t acceptedPacketSize;

        bool checkAck(uint8_t *x, uint32_t blockCount);
        bool checkNack(uint8_t *x, uint32_t blockCount);
        uint16_t getBlockAnswerSize(uint32_t blockCount);
        virtual bool isAckFirstBlock(uint8_t *x);
        virtual bool isNackFirstBlock(uint8_t *x);
        virtual inline bool isNack(uint8_t* x) {
            ALOGD("xfp nack %x\n", x[0]);
            return (*x == NACK_CHAR);
        }
        virtual inline bool isAck(uint8_t* x) {
            ALOGD("xfp ack %x\n", x[0]);
            return ( ((ACK_CHAR_MIN <= *x) && (*x <= ACK_CHAR_MAX)) || (*x == ACK_CHAR_SINGLE) );
        }
    public:
        Uploader(const uint16_t acceptedPktSize = 1024,
                 const uint16_t ackDelay = 0,
                 const uint16_t ackFirstBlkLen = 1):
            acknowledgeFirstBlockLen(ackFirstBlkLen),
            acknowledgeDelay(ackDelay),
            acceptedPacketSize(acceptedPktSize) {}

        int getError(void) { return err; }
        void setAcknowledgeFirstBlock(uint8_t* ackFirstBlock, const uint16_t len);
        void setAcknowledgeDelay(const uint16_t delay) { acknowledgeDelay = delay; }
        void setAcceptedPacketSize(const uint16_t size) { acceptedPacketSize = size; }
        virtual bool initializeStream(int &stream);
        virtual bool uploadStreamStrategy(Device*);

        virtual ~Uploader(void);
};
#endif
