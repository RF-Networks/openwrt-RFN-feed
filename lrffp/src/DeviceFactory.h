/*
 * DeviceFactory.h
 *
 *  Created on: Mar 3, 2016
 *      Author: ubuntu
 */

#ifndef DEVICEFACTORY_H_
#define DEVICEFACTORY_H_

using namespace std;

#include "Device.h"

class DeviceFactory {
public:
    static Device* getDevice(int deviceId);
    static void destroyDevice(Device *dev);
};


#endif /* DEVICEFACTORY_H_ */
