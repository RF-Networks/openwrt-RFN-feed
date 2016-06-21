#ifndef LOG_H_
#define LOG_H_

#ifdef __cplusplus
extern "C" {
#endif

#define LOG_LEVEL_ERROR     0
#define LOG_LEVEL_INFO      1
#define LOG_LEVEL_VERBOSE   2

void set_log_level(int level);
void dbg_print(int level, const char *fmt, ...);

#if !defined(ANDROID_CHANGES)
#define ALOGI(format, ...) dbg_print(LOG_LEVEL_INFO, format, ## __VA_ARGS__)
#define ALOGE(format, ...) dbg_print(LOG_LEVEL_ERROR, format, ## __VA_ARGS__)
#define ALOGD(format, ...) dbg_print(LOG_LEVEL_VERBOSE, format, ## __VA_ARGS__)
#define ALOGW(format, ...) dbg_print(LOG_LEVEL_INFO, format, ## __VA_ARGS__)
#endif

#ifdef __cplusplus
} /* C */
#endif

#endif /* LOG_H_ */
