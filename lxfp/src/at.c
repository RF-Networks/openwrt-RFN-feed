#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

#include "log.h"

static int _send_command(int fd,
        char *cmd,
        char *resp,
        size_t resp_size_max,
        struct timeval *tv)
{
    int ret = -1;
    int bytes_total = 0;
    int bytes_written;
    int bytes_read;
    int len;
    int retry = 100;
    fd_set rfds;

    len = strlen(cmd);

    while (len) {
        bytes_written = write(fd,
                cmd + bytes_total,
                strlen(cmd + bytes_total));
        if (-1 != bytes_written) {
            len -= bytes_written;
            bytes_total += bytes_written;
        } else {
            dbg_print(LOG_LEVEL_ERROR, "Device write\n");
        }
    }

    bytes_total = 0;
    memset(resp, '\0', resp_size_max);

    do {
        FD_ZERO(&rfds);
        FD_SET(fd, &rfds);

        ret = select(fd + 1, &rfds, NULL, NULL, tv);
        if (-1 == ret) {
            dbg_print(LOG_LEVEL_ERROR, "Select failed on device\n");
            goto error;
        } else if (0 == ret) {
            dbg_print(LOG_LEVEL_VERBOSE, "Select read timeout\n");
            break;
        } else {
            bytes_read = read(fd,
                    resp + bytes_total,
                    resp_size_max - bytes_total - 1);
            if (-1 == bytes_read) {
                dbg_print(LOG_LEVEL_ERROR, "Read failed on device\n");
                continue;
            }

            bytes_total += bytes_read;
        }
        retry--;
    } while (retry);

    ret = bytes_total;
    dbg_print(LOG_LEVEL_VERBOSE,
            "Response: %s\n, Bytes total: %d\n",
            resp,
            bytes_total);

error:
    return ret;
}

int send_verify(int fd,
        char *cmd,
        char *resp_expected,
        char *resp,
        size_t resp_size_max)
{
    int ret;
    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 0;

    ret = _send_command(fd, cmd, resp, resp_size_max, &tv);
    if (-1 != ret) {
        if (strstr(resp, resp_expected) == NULL) {
            ret = 0;
            dbg_print(LOG_LEVEL_ERROR, "Expected response not found\n");
        }
    }

    return ret;
}

int send_verify_timeout(int fd,
        char *cmd,
        char *resp_expected,
        char *resp,
        size_t resp_size_max,
        struct timeval *tv)
{
    int ret;

    ret = _send_command(fd, cmd, resp, resp_size_max, tv);
    if (-1 != ret) {
        if (strstr(resp, resp_expected) == NULL) {
            ret = 0;
            dbg_print(LOG_LEVEL_ERROR, "Expected response not found\n");
        }
    }

    return ret;
}

int send_timeout(int fd,
        char *cmd,
        char *resp,
        size_t resp_size_max,
        struct timeval *tv)
{
    return _send_command(fd, cmd, resp, resp_size_max, tv);
}

int send(int fd, char *cmd, char *resp, size_t resp_size_max)
{
    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 0;

    return _send_command(fd, cmd, resp, resp_size_max, &tv);
}

int open_device(char *dev_name)
{
    return open(dev_name, O_RDWR|O_NOCTTY);
}

