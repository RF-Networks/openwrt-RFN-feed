from ecoppia.globals import *
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
import multiprocessing
from multiprocessing import *
import sqlite3

class HardResetPossible:
    def __init__(self, possible, description):
        self.possible = possible
        self.description = description

class ResetFacilitator:

    def __init__(self):
        self.hard_reset_lock = threading.Lock()

        self.main_loop_event = threading.Event()
        self.main_loop_event.clear()
        self.SoftwareEnableReset = True
        dbconn = sqlite3.connect(SQLITE_DB_NAME) 
        cursor = dbconn.cursor() 
              
        num_of_table_instances = cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='"+DB_HARD_RESETS_TABLE_NAME+"'").fetchone()[0]
        
        if num_of_table_instances == 0:	
            cursor.execute("CREATE TABLE "+ DB_HARD_RESETS_TABLE_NAME+"(ID INTEGER PRIMARY KEY, OBSERVATION_TIME DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);")
            dbconn.commit()		 
    def Enable(self):
        self.SoftwareEnableReset = True
        app_log.info("SoftwareEnableReset = True ,TcpListenerEnable = False  !")  


    def Disable(self):
        self.SoftwareEnableReset = False
        app_log.info("SoftwareEnableReset = False  !")       
        

    def HardResetPossible(self):
        if self.SoftwareEnableReset == False :
            return HardResetPossible(False, "Software Disabled") 
        dbconn = sqlite3.connect(SQLITE_DB_NAME) 
        cursor = dbconn.cursor() 

        total_hard_resets = cursor.execute("SELECT COUNT(*) FROM "+DB_HARD_RESETS_TABLE_NAME+" WHERE OBSERVATION_TIME >= DATETIME('now','-"+str(MINIMAL_TIME_INTERVAL_BETWEEN_HARD_RESETS)+" minutes')").fetchone()[0]        
        
        possible = True if total_hard_resets == 0 else False

        msgInfo = str(total_hard_resets)+" hard resets carried out within the last "+str(MINIMAL_TIME_INTERVAL_BETWEEN_HARD_RESETS)+" minutes"
        msgSuffix = ", hard reset is permitted !" if possible else ", hard reset could not be performed !" 
                                       
        return  HardResetPossible(possible, msgInfo + msgSuffix) 
           
    def ClearHardResetDB(self):
        dbconn = sqlite3.connect(SQLITE_DB_NAME) 
        cursor = dbconn.cursor() 
        cursor.execute("DELETE FROM "+DB_HARD_RESETS_TABLE_NAME)
        dbconn.commit()

    def DoHardReset(self, func_before = None, *args):

        with self.hard_reset_lock:

            rslt  = self.HardResetPossible()
            
            if(func_before):
                func_before(rslt, *args)

            app_log.info(rslt.description)

            if rslt.possible:

                app_log.info("Hard Reset Invoked !")  
                     
                dbconn = sqlite3.connect(SQLITE_DB_NAME) 
                cursor = dbconn.cursor() 

                cursor.execute("INSERT INTO "+DB_HARD_RESETS_TABLE_NAME+" DEFAULT VALUES")            
                # Total records in Hard Resets table is limited to DB_HARD_RESETS_TABLE_MAX_SIZE
                cursor.execute("DELETE FROM "+DB_HARD_RESETS_TABLE_NAME+" WHERE ID IN (SELECT ID FROM "+DB_HARD_RESETS_TABLE_NAME+" ORDER BY OBSERVATION_TIME DESC LIMIT "+str(DB_HARD_RESETS_TABLE_MAX_SIZE)+",-1)")

                dbconn.commit()

                __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))        
                try:       
                    #os.system("find /sbin/ -iname 'globals.py' -type f -exec sed -i 's/TcpListenerEnable = True/TcpListenerEnable = False/' {} \\;")
                    os.system("{} {}".format("python", os.path.join(__location__, 'stand_alone_hard_reset.py')))
                except Exception:
                    app_log.error("Running external script stand_alone_hard_reset.py failed !")

    def DoApplicationReset(self):
        app_log.info("Application Reset Invoked !")
        if self.SoftwareEnableReset == False :
            return ""
        self.main_loop_event.set()

    def DoSystemReset(self):
        app_log.info("System Reset Invoked !")  
        if self.SoftwareEnableReset == False :
            return ""
        os.system('reboot')