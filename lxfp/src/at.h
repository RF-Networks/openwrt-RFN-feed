#ifndef AT_H_
#define AT_H_

#ifdef __cplusplus
extern "C" {
#endif

int send_verify(int fd,
        const char *cmd,
        const char *resp_expected,
        char *resp,
        size_t resp_size_max);

int send_verify_timeout(int fd,
        const char *cmd,
        const char *resp_expected,
        char *resp,
        size_t resp_size_max,
        struct timeval *tv);

int send_timeout(int fd,
        const char *cmd,
        char *resp,
        size_t resp_size_max,
        struct timeval *tv);

int send(int fd, char *cmd, char *resp, size_t resp_size_max);

int open_device(char *dev_name);

#ifdef __cplusplus
} /* C */
#endif

#endif /* AT_H_ */

