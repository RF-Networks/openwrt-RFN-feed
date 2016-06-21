#ifndef LXFP_ERROR_H_
#define LXFP_ERROR_H_

#if defined(ANDROID_CHANGES)
#define LOG_TAG "XFP"
#endif

#define E_SUCCESS               0
#define E_OSCALL                -1
#define E_DEVICE_NOT_OPEN       -2
#define E_FILE_ACCESS           -3
#define E_FLASHER_DEVICE        -4
#define E_FLASHER_TIMEOUT       -5
#define E_FLASHER_NACK          -6
#define E_FLASHER_BOOT          -7
#define E_GENERIC_FAILURE       -99

#endif /* LXFP_ERROR_H_ */
