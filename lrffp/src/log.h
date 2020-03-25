/*
 * Copyright (c) 2019, RF Networks Ltd.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code are not permitted.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of RF Networks Ltd. nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef SRC_LOG_H_
#define SRC_LOG_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <string>

#define LOG_LEVEL_ERROR     0
#define LOG_LEVEL_INFO      1
#define LOG_LEVEL_VERBOSE   2

void set_log_level(int level);
int get_log_level();
void dbg_print(int level, const char *fmt, ...);
std::string array_as_hex_string(unsigned char *data, size_t data_length);

#if !defined(ANDROID_CHANGES)
#define ALOGI(format, ...) dbg_print(LOG_LEVEL_INFO, format, ## __VA_ARGS__)
#define ALOGE(format, ...) dbg_print(LOG_LEVEL_ERROR, format, ## __VA_ARGS__)
#define ALOGD(format, ...) dbg_print(LOG_LEVEL_VERBOSE, format, ## __VA_ARGS__)
#define ALOGW(format, ...) dbg_print(LOG_LEVEL_INFO, format, ## __VA_ARGS__)
#endif

#ifdef __cplusplus
} /* C */
#endif

#endif /* SRC_LOG_H_ */
