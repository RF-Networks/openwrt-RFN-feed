#import logging
from ecoppia.globals import *
import math
import time
import os
import glob
import re
import sys
import select
import zipfile
from threading import Thread
from threading import Timer
from ecoppia.lib.package_info import *
from StringIO import StringIO
from shutil import copyfile

startstring = """import os
import os.path
import sys

workingdir = os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), '{}')
sys.path.insert(0, workingdir)

import ecoppia.ecoppia_station

#import test_telit_commands
#import test_unit_simulator"""

class UpgradeHandler:

    def __init__(self):
        self.server_context = None
        self.server_in_types = [SmartStPkgType.NewVersion]

    def setServerContext(self, context):
        self.server_context = context

    def processServerPackage(self, pkgInfo):
        try:
            app_log.debug("Process upgrade packet")
            station_upgrade.info("Process upgrade packet %s", str(pkgInfo))
            #station_upgrade.info("delete_rotated_logs") 
            #self.delete_rotated_logs() Not Working
            station_upgrade.info("createNextFolder")
            path = self.createNextFolder(pkgInfo.version)
            station_upgrade.info("extractZipToFolder %s", path)
            self.extractZipToFolder(pkgInfo.payload, path)
            station_upgrade.info("updateStartFile %s", path)
            self.updateStartFile(path,pkgInfo.version)

            station_upgrade.info("doSendPkg Success %s %s",SmartStPkgType.NewVersionAck, pkgInfo.sessionid)
            self.server_context.doSendPkg(pkgInfo, PackageInfo(SmartStPkgType.NewVersionAck, 'Success', pkgInfo.sessionid))
        except Exception as ex:
            station_upgrade.info("doSendPkg Error %s %s",SmartStPkgType.NewVersionAck, pkgInfo.sessionid)
            self.server_context.doSendPkg(pkgInfo, PackageInfo(SmartStPkgType.NewVersionAck, 'Error: %s %s' % (ex, pkgInfo), pkgInfo.sessionid))

        station_upgrade.info("Rebooting the device after a successful version upgrade")
        app_log.info("Rebooting the device after a successful version upgrade")
        self.server_context.reset_facilitator.DoApplicationReset()

    def createNextFolder(self,version):
        fileMask = os.path.join(stationFolder, version)
        #i = 1
        #while os.path.exists(fileMask % i):
        #    i += 1
        #newFolder = fileMask % i
        if not os.path.exists(fileMask):
            os.mkdir(fileMask)
        return fileMask

    def delete_rotated_logs(self):
        for filename in glob.glob(logsFolder + "/" + "*.log.*"):
            station_upgrade.info("deleting rotated logfile %s", filename)
            app_log.info("deleting rotated logfile %s", filename)
            try:
                os.remove(filename)
            except OSError as ex:
                station_upgrade.info("deleting %s failed: %s", filename, ex)
                app_log.info("deleting %s failed: %s", filename, ex)
                pass

    def extractZipToFolder(self, compressed, path):
        zip_ref = zipfile.ZipFile(StringIO(compressed))
        zip_ref.extractall(path)
        zip_ref.close()

    def updateStartFile(self, path, version):
        oldpath = os.path.join(stationFolder, "start.py")
        newpath = os.path.join(stationFolder, "newStart.py")

        lastFolder = os.path.basename(os.path.normpath(path))
        with open(newpath, "a") as newfile:
            newfile.write(startstring.format(version))
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


        

        