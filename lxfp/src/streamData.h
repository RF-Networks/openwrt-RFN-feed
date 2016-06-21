#ifndef STREAM_DATA_H_
#define STREAM_DATA_H_

#include <stdint.h>
#include <termios.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#define DATA_SMALL_BLOCK_MAX_SIZE       256
#define DATA_BIG_BLOCK_MAX_SIZE	        65536

#define CHUNK_HEADER_LEN                2

#define NACK_CHAR                       0xB5
#define ACK_CHAR_MIN                    0xA0
#define	ACK_CHAR_MAX                    0xA9
#define ACK_CHAR_SINGLE                 0x01
#define BOGUS_CHAR                      0x01

typedef struct stream_header {
    int16_t header_size;
    char sw_version[32];
    char product_name[32];
    int16_t memory_type;
    int16_t stream_version;
    uint32_t speed_offset;
    char dummy[116];
    uint32_t AckBootOffset;
} __attribute__((__packed__)) StreamHeader;

typedef struct data_small_block {
    uint16_t len;
    uint8_t data[DATA_SMALL_BLOCK_MAX_SIZE];
} DataSmallBlock;

typedef struct data_big_block {
    uint16_t len;
    char data[DATA_BIG_BLOCK_MAX_SIZE];
} DataBigBlock;

#endif /* STREAM_DATA_H_ */
