import sqlite3
from ecoppia.globals import *

#fields is a list like ['ID INTEGER PRIMARY KEY', 'NAME TEXT NOT NULL']

class Dal():
    def __init__(self):
        self.create_sqlite_tbl(DB_CONFIGURATIONS_TABLE_NAME, ['ID INTEGER PRIMARY KEY', 'CONFIG_TYPE TEXT NOT NULL', 'CONFIG_NAME TEXT NOT NULL'])

    def get_sqlite_connection(self):
        dbconn = sqlite3.connect(SQLITE_DB_NAME) 
        return dbconn 

    def create_sqlite_tbl(self, tbl_name, fields):
        dbconn = self.get_sqlite_connection()
        cursor = dbconn.cursor()
        num_of_table_instances = cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='"+tbl_name+"'").fetchone()[0]
        if num_of_table_instances == 0:	
            tbl_name_and_fields = tbl_name + '('
            for f in fields:
                tbl_name_and_fields = tbl_name_and_fields + f + ','
            tbl_name_and_fields = tbl_name_and_fields[:-1] + ')'
            cursor.execute("CREATE TABLE " + tbl_name_and_fields)
            dbconn.commit()	

    def get_configuration(self, config_type):
        dbconn = self.get_sqlite_connection()
        cursor = dbconn.cursor()
        clist = cursor.execute("SELECT CONFIG_NAME FROM " + DB_CONFIGURATIONS_TABLE_NAME + " WHERE CONFIG_TYPE = ?", (config_type,)).fetchall()
        config_name = clist[0][0] if len(clist) > 0 else ''
        return config_name

    def update_configuration(self, config_type, config_value):
        dbconn = self.get_sqlite_connection()
        cursor = dbconn.cursor()
        cl = cursor.execute("SELECT CONFIG_NAME FROM " + DB_CONFIGURATIONS_TABLE_NAME + " WHERE CONFIG_TYPE = ? ", (config_type,)).fetchall()
        if len(cl) == 0:
            cursor.execute("INSERT INTO " + DB_CONFIGURATIONS_TABLE_NAME + "(CONFIG_NAME, CONFIG_TYPE) VALUES(?,?)", (config_value, config_type))
        else:
            cursor.execute("UPDATE " + DB_CONFIGURATIONS_TABLE_NAME + " SET CONFIG_NAME = ? WHERE CONFIG_TYPE = ? ", (config_value, config_type))
        dbconn.commit() #Commit the change
