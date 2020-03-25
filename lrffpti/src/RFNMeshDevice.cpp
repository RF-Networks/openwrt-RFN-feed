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

#include <thread>
#include <chrono>
#include "RFNMeshDevice.h"

RFNMeshDevice::RFNMeshDevice(Uploader* uploader) : Device(uploader) {

}

RFNMeshDevice::~RFNMeshDevice() {

}

bool RFNMeshDevice::enterBootMode() {
	uint8_t reply[16];
	uint8_t enterBootloaderCmd[] = { 0xAB, 0x96, 0x01, 0x0A, 0x12, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0xCB, 0x00, 0x00, 0x00, 0x08, 0x7A, 0xCD };
	memset(reply, 0, sizeof(reply));
	ALOGW("lrffpti enterBootMode Please wait...\n");
	memset(reply, 0, sizeof(reply));
	if (!sendSerialCommand(enterBootloaderCmd, sizeof(enterBootloaderCmd), reply, sizeof(reply))) {
		return false;
	}
	//  AB 96 01 07 13 12 FF FF FF FF 00 00 00 16 7E CD - Reply example
	return (reply[0] == 0xAB && reply[15] == 0xCD && reply[3] == 0x07 && reply[4] == 0x13 && reply[10] == 0x00 && reply[11] == 0x00 && reply[12] == 0x00);
}

