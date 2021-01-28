from ecoppia.globals import *
import socket
import thread
import math
import threading
import time
import select
import struct
import binascii
import json
from threading import Thread
import os
import time


class PackageInfo:
    def __init__(self, type, payload, sessionid=0, version=software_version, callbackQueue="", site=""):
        self.type = type
        self.payload = payload
        self.sessionid = sessionid
        self.version = version
        self.callbackQueue = callbackQueue
        self.site = site

    def __str__(self):

        direction1 = 'Master to Station'
        direction2 = 'Station to Master'

        type_name = SmartStPkgType.getName(self.type)

        type_direction = "" if SmartStPkgType.getDirection(self.type) == None else direction1 if SmartStPkgType.getDirection(self.type) == SmartStPkgType.MasterToSmartStation else direction2

        type_description = type_name + " " + "(" + type_direction + ")"  

        return "Pkg session id: {sessionid}, type: {td}, version: {ver}".format(sessionid = self.sessionid, td = type_description, ver = self.version)

class SmartStPkgType:

    SmartStationToMaster = 0
    MasterToSmartStation = 1
    MessageBroker = True
    LowLevelStream = False
    SmartStPkgTypeInfo = {}

    # MasterToSmartStation (LowLevelStream)
    HandShakeAck = 1 
    KeepAlive = 2
    PuttyToSmartSt = 3

    for x in [HandShakeAck, KeepAlive, PuttyToSmartSt]:
        SmartStPkgTypeInfo[x] = (MasterToSmartStation, LowLevelStream)


    # MasterToSmartStation (MessageBroker)
    RFCommand = 4
    NewVersion = 5
    HardReset = 6
    NewRFCommand = 7
    MqttKeepAlive = 8
    StationGetConfig = 9

    for x in [RFCommand, NewVersion, HardReset, NewRFCommand, MqttKeepAlive,StationGetConfig]:
        SmartStPkgTypeInfo[x] = (MasterToSmartStation, MessageBroker)



    # SmartStationToMaster (LowLevelStream)
    HandShake = 128
    KeepAliveAck = 129
    PuttyFromSmartSt = 130

    for x in [HandShake, KeepAliveAck, PuttyFromSmartSt]:
        SmartStPkgTypeInfo[x] = (SmartStationToMaster, LowLevelStream)


    # SmartStationToMaster (MessageBroker)
    RFResponse = 131
    NewVersionAck = 132
    VersionMismatch = 133
    RFCommandAck = 134
    WeatherInfo = 135
    HardResetAck = 136
    MqttKeepAliveAck = 137

    for x in [RFResponse, NewVersionAck, VersionMismatch, RFCommandAck, WeatherInfo, HardResetAck,MqttKeepAliveAck]:
        SmartStPkgTypeInfo[x] = (SmartStationToMaster, MessageBroker)



    @staticmethod
    def getDirection(pkgType):
        return SmartStPkgType.SmartStPkgTypeInfo[pkgType][0] if pkgType in SmartStPkgType.SmartStPkgTypeInfo else None

    @staticmethod
    def getDirectionName(direction):
        if(direction == SmartStPkgType.MasterToSmartStation):
            return "MasterToSmartStation"
        elif(direction == SmartStPkgType.SmartStationToMaster):
            return "SmartStationToMaster"

    @staticmethod
    def getName(pkgType):

        pkgStrType = ""

        if(pkgType == SmartStPkgType.HandShakeAck):
            pkgStrType = "HandShakeAck" 
        elif(pkgType == SmartStPkgType.KeepAlive):
            pkgStrType = "KeepAlive"
        elif(pkgType == SmartStPkgType.PuttyToSmartSt):
            pkgStrType = "PuttyToSmartSt"
        elif(pkgType == SmartStPkgType.RFCommand):
            pkgStrType = "RFCommand"
        elif(pkgType == SmartStPkgType.NewVersion):
            pkgStrType = "NewVersion"
        elif(pkgType == SmartStPkgType.HardReset):
            pkgStrType = "HardReset"
        elif(pkgType == SmartStPkgType.NewRFCommand):
            pkgStrType = "NewRFCommand"
        elif(pkgType == SmartStPkgType.HandShake):
            pkgStrType = "HandShake"
        elif(pkgType == SmartStPkgType.KeepAliveAck):
            pkgStrType = "KeepAliveAck"
        elif(pkgType == SmartStPkgType.PuttyFromSmartSt):
            pkgStrType = "PuttyFromSmartSt"
        elif(pkgType == SmartStPkgType.RFResponse):
            pkgStrType = "RFResponse"
        elif(pkgType == SmartStPkgType.NewVersionAck):
            pkgStrType = "NewVersionAck"
        elif(pkgType == SmartStPkgType.VersionMismatch):
            pkgStrType = "VersionMismatch"
        elif(pkgType == SmartStPkgType.RFCommandAck):
            pkgStrType = "RFCommandAck"
        elif(pkgType == SmartStPkgType.WeatherInfo):
            pkgStrType = "WeatherInfo"
        elif(pkgType == SmartStPkgType.HardResetAck):
            pkgStrType = "HardResetAck"
        elif(pkgType == SmartStPkgType.MqttKeepAlive):
            pkgStrType = "MqttKeepAlive"
        elif(pkgType == SmartStPkgType.MqttKeepAliveAck):
            pkgStrType = "MqttKeepAliveAck"
        elif(pkgType == SmartStPkgType.StationGetConfig):
            pkgStrType = "StationGetConfig"
        else:
            pkgStrType = "Unknown Package Type"

        return pkgStrType

#class SmartStRFGroup:
#    SimpleUnitCommand = 0
#    ConfigUnitCommand = 1
#    HandShakeUnitCommand = 2
#    BroadcastUnitCommand = 3
#    ConfigStationCommand = 4
#    OldUnitCommand = 5

#class RFResponsePayloadType:
#    RFResponseOk = 1
#    RFNoTelitAck = 2
#    RFTimeout = 3
#    RFError = 4


#    @staticmethod
#    def getName(value):

#        name = None
#        if(value == RFResponsePayloadType.RFResponseOk):
#            name = "RFResponseOk"
#        elif(value == RFResponsePayloadType.RFNoTelitAck):
#            name = "RFNoTelitAck"
#        elif(value == RFResponsePayloadType.RFError):
#            name = "RFError"
#        elif(value == RFResponsePayloadType.RFTimeout):
#            name = "RFTimeout"
            
#        return name

def bytearrayToStr(arr):
    if(len(arr) > 0):  
        return "".join("0x%02x , " % i for i in arr)[:-3]
    else:
        return ""

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError, e:
        return False
    return True

def decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = decode_list(item)
        elif isinstance(item, dict):
            item = decode_dict(item)
        rv.append(item)
    return rv

def decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = decode_list(value)
        elif isinstance(value, dict):
            value = decode_dict(value)
        rv[key] = value
    return rv





