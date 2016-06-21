#include <stdio.h>
#include <stdarg.h>

#include "log.h"

#ifdef __cplusplus
extern "C" {
#endif

int log_level = LOG_LEVEL_INFO;

void set_log_level(int level)
{
    log_level = level;
}

void dbg_print(int level, const char *fmt, ...)
{
    FILE *std_log;
    const char *log_tag;

    if (log_level < level)
        return;

    if (LOG_LEVEL_ERROR == level) {
        std_log = stderr;
        log_tag = "ERROR: ";
    } else if (LOG_LEVEL_INFO == level) {
        std_log = stdout;
        log_tag = "";
    } else {
        std_log = stdout;
        log_tag = "DBG: ";
    }

    fprintf(std_log, "%s", log_tag);
    va_list args;
    va_start(args, fmt);
    vfprintf(std_log, fmt, args);
    va_end(args);
}

#ifdef __cplusplus
}
#endif
