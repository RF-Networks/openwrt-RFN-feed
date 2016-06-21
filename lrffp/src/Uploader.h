/*
 * Uploader.h
 *
 *  Created on: Mar 6, 2016
 *      Author: ubuntu
 */

#ifndef UPLOADER_H_
#define UPLOADER_H_

#include <fstream>
#include <iostream>
#include <string>
#include "log.h"

using namespace std;

class Device;

class Uploader {
	friend class Device;
protected:
	ifstream fdStream;
	int err;
	uint8_t data[0xFFFF];
	unsigned int max_address;
	bool sendFlashCommand(Device* device, uint8_t *data, ssize_t size);
	bool enterFlashingMode(Device* device);
	bool exitFlashingMode(Device* device);
	bool eraseMemory(Device* device);
	bool sendFirmwareChunk(Device* device, ssize_t offset);
	bool compareCRC(Device* device, unsigned int pointer);
public:
	Uploader();
	virtual ~Uploader();
	virtual bool initializeStream(ifstream &stream);
	virtual bool uploadStream(Device* device);
};

#endif /* UPLOADER_H_ */
