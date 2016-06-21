#include <unistd.h>

#include "Uploader.h"
#include "Device.h"
#include "lxfpError.h"
#include "lxfp.h"

#define ANSWER_MAX_SIZE 128

char Uploader::progressBar[] = { '|', '/', '-', '\\'};

void Uploader::setAcknowledgeFirstBlock(uint8_t* ackFirstBlock,
                                const uint16_t len) {
    acknowledgeFirstBlock = ackFirstBlock;
    acknowledgeFirstBlockLen = len;
}

bool Uploader::initializeStream(int &stream) {
    int bytesRead = 0;

    err = E_SUCCESS;
    fdStream = stream;
    StreamHeader temp_hdr;

    ALOGD("clearing header struct, size: %d\n", sizeof(header));
    memset(&header, 0, sizeof(header));
    memset(&temp_hdr, 0, sizeof(temp_hdr));

    bytesRead = read(fdStream, ((char *)&temp_hdr), sizeof(temp_hdr));
    if (bytesRead != sizeof(temp_hdr)) {
        err = E_FILE_ACCESS;
        goto end;
    }

    memcpy(&header, &temp_hdr, temp_hdr.header_size);

    ALOGI("xfp bin info header size: %d bytes, " \
          "sw version: %s, " \
          "product name: %s, " \
          "memory type: %d, " \
          "stream version: %d, " \
          "speed offset: %u, " \
          "AckBootOffset: %u\n", header.header_size,
          header.sw_version, header.product_name,
          header.memory_type, header.stream_version,
          header.speed_offset, header.AckBootOffset
         );

    if (lseek(fdStream, header.header_size, SEEK_SET) < 0) {
        err = E_FILE_ACCESS;
    }

end:
    return (err == E_SUCCESS);
}


bool Uploader::uploadStreamStrategy(Device* device) {
    DataBigBlock streamChunk;
    uint8_t answer[ANSWER_MAX_SIZE];
    clock_t clockStart;
    unsigned int count;
    int actualPacketSize;
    int byteWritten;
    uint8_t timeout = 120;
    int progress = 0;
    uint32_t blockCount = 0;
    uint32_t chunkCount = 0;
    uint32_t totalWrittenBytes = 0;
    uint32_t totalReadBytes = 0;
    unsigned int speedByte = 0;
    int readBytes = 0;
    bool speedChange;

    fd_set rfds;
    struct timeval tv;
    int retval;

    err = E_SUCCESS;

    int fd = device->getFileDescriptor();
    tcflush(fd, TCIOFLUSH);

    uint8_t deviceSpeed = device->getDeviceSpeed();

    if (deviceSpeed > 0)
        speedChange = true;

    while ((readBytes = read (fdStream, ((char *)&(streamChunk.len)),
                              CHUNK_HEADER_LEN)) > 0) {
        readBytes = read (fdStream, streamChunk.data, streamChunk.len + 1);
        if (readBytes < 0) {
            err = E_GENERIC_FAILURE;
            goto end;
        }
        totalReadBytes += readBytes;

        ALOGD("xfp uploadStream Block %d length %d readbytes %d\n",
              blockCount, streamChunk.len + 1, readBytes);

#if !defined(ANDROID_CHANGES)
        ALOGI("Flashing... %c\r", progressBar[progress % sizeof(progressBar)]);
        progress++;
#endif

        if ( (totalReadBytes > (header.speed_offset)) && speedChange) {
            speedChange = false;
            speedByte = (header.speed_offset - (totalReadBytes - readBytes) - 2);
        }

        count = streamChunk.len + 1;

        if (speedByte == 0xFF) {
            if (!device->changeBaudRate(deviceSpeed)) {
                err = E_OSCALL;
                goto end;
            }

            speedByte = 0;
        } else if (speedByte > 0) {
            if ( streamChunk.data[speedByte] != 0 ) {
                streamChunk.data[speedByte] = deviceSpeed;
                speedByte = 0xFF;
            }
        }

        while (count) {
            if (count > acceptedPacketSize)
                actualPacketSize = acceptedPacketSize;
            else
                actualPacketSize = count;

            byteWritten = write(fd, &(streamChunk.data[streamChunk.len + 1 - count]), actualPacketSize);
            if (byteWritten != -1) {
                count -= byteWritten;
                totalWrittenBytes += byteWritten;
            }
        }

        if ((device->getType() != DEVICE_LEV2) ||
                (totalWrittenBytes + header.header_size +
                 (chunkCount*CHUNK_HEADER_LEN) >= header.AckBootOffset)) {
            clockStart = clock();
            tv.tv_sec = 120;
            tv.tv_usec = 0;
            FD_ZERO(&rfds);
            FD_SET(fd, &rfds);
            retval = select(fd + 1, &rfds, NULL, NULL, &tv);

            if (retval == -1) {
                err = E_GENERIC_FAILURE;
                goto end;
            } else if (retval) {
                uint8_t bytesAvailable = 0;
                uint32_t delay = BYTES_IN_BUFFER_DELAY;

                do {
                    ioctl(fd, FIONREAD, &bytesAvailable);
                } while ( (bytesAvailable != getBlockAnswerSize(blockCount)) && (--delay) );

                while (read(fd, answer, getBlockAnswerSize(blockCount)) == -1) {
                    if (((clock() - clockStart) / CLOCKS_PER_SEC) > timeout) {
                        err = E_FLASHER_TIMEOUT;
                        goto end;
                    }
                }

                if (checkAck(answer, blockCount)) {
                    blockCount++;
                    // Some modem families need a small delay before sending a new block
                    if (acknowledgeDelay != 0)
                        usleep(acknowledgeDelay);
                    tcflush(fd, TCIOFLUSH);
                    continue;
                } else if (checkNack(answer, blockCount)) {
                    err = E_FLASHER_NACK;
                    goto end;
                } else {
                    err = E_GENERIC_FAILURE;
                    goto end;
                }
            } else {
                err = E_FLASHER_TIMEOUT;
                goto end;
            }
        } else {
            usleep(5000);
            tcflush(fd, TCIOFLUSH);
            ALOGI("Sending chunk %d, not waiting for ack\n", chunkCount);
            chunkCount++;
            usleep(5000);
        }
    }

end:
    if (err != E_SUCCESS) {
        ALOGE("xfp uploadStream Error code %d\n", err);
    }
    return (err == E_SUCCESS);
}

uint16_t Uploader::getBlockAnswerSize(uint32_t blockCount) {
    if (blockCount == 0)
        return acknowledgeFirstBlockLen;
    else
        return 1;
}

bool Uploader::isAckFirstBlock(uint8_t *x) {
    return isAck(x);
}

bool Uploader::isNackFirstBlock(uint8_t *x) {
    return isNack(x);
}

bool Uploader::checkAck(uint8_t *x, uint32_t blockCount) {
    if (blockCount == 0)
        return isAckFirstBlock(x);
    else
        return isAck(x);
}

bool Uploader::checkNack(uint8_t *x, uint32_t blockCount) {
    if (blockCount == 0)
        return isNackFirstBlock(x);
    else
        return isNack(x);
}

Uploader::~Uploader(void) {}
