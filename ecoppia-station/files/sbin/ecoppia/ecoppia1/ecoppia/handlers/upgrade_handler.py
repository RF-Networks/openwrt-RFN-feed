#import logging
from ecoppia.globals import *
import math
import time
import os
import re
import sys
import select
import zipfile
from threading import Thread
from threading import Timer
from ecoppia.lib.package_info import *
from StringIO import StringIO
from shutil import copyfile

class UpgradeHandler:

    def __init__(self):
        self.server_context = None
        self.server_in_types = [SmartStPkgType.NewVersion]

    def setServerContext(self, context):
        self.server_context = context

    def processServerPackage(self, pkgInfo):
        app_log.debug("Process upgrade packet")

        path = self.createNextFolder()
        self.extractZipToFolder(pkgInfo.payload, path)
        self.updateStartFile(path)

        self.server_context.doSendPkg(pkgInfo, PackageInfo(SmartStPkgType.NewVersionAck, '', pkgInfo.sessionid))
        
        app_log.info("Rebooting the device after a successful version upgrade")
        self.server_context.reset_facilitator.DoApplicationReset()

    def createNextFolder(self):
        fileMask = os.path.join(stationFolder, "ecoppia%s")
        i = 1
        while os.path.exists(fileMask % i):
            i += 1
        newFolder = fileMask % i
        os.mkdir(newFolder)
        return newFolder

    def extractZipToFolder(self, compressed, path):
        zip_ref = zipfile.ZipFile(StringIO(compressed))
        zip_ref.extractall(path)
        zip_ref.close()

    def updateStartFile(self, path):
        oldpath = os.path.join(stationFolder, "start.py")
        newpath = os.path.join(stationFolder, "newStart.py")

        lastFolder = os.path.basename(os.path.normpath(path))
        regex = re.compile(r"\'ecoppia\d+\'")

        with open(oldpath, "r") as oldfile, open(newpath, "w") as newfile:
            for line in oldfile:
                newLine = regex.sub("\'" + lastFolder + "\'", line)
                newfile.write(newLine)

        backup = os.path.join(stationFolder, "start.backup")
        #error when working with backup is not critical
        try:
            copyfile(oldpath, backup)
        except OSError:
            pass

        copyfile(newpath, oldpath)

        #error when removing temp file is not critical
        try:
            os.remove(newpath)
        except OSError:
            pass


        

        