#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Implements a new handler for the logging module which uses the pure syslog python module.
@author:  Luis Martin Gil
@year: 2013
'''
import logging
import syslog
import sys
import os.path

class SysLogLibHandler(logging.Handler):
    """A logging handler that emits messages to syslog.syslog."""
    FACILITY = [syslog.LOG_LOCAL0,
                syslog.LOG_LOCAL1,
                syslog.LOG_LOCAL2,
                syslog.LOG_LOCAL3,
                syslog.LOG_LOCAL4,
                syslog.LOG_LOCAL5,
                syslog.LOG_LOCAL6,
                syslog.LOG_LOCAL7]
    def __init__(self, n, logident = None):
        """ Pre. (0 <= n <= 7) """
        if logident is None:
            logident = os.path.basename(sys.argv[0])	# Mimic the behavior introduced in Python 3.2
        else:
            logident = str(logident)

        try:
            syslog.openlog(ident = logident, logoption=syslog.LOG_PID, facility=self.FACILITY[n])
        except Exception as err:
            try:
                syslog.openlog(logident, syslog.LOG_PID, self.FACILITY[n])
            except Exception as err:
                raise
        # We got it
        logging.Handler.__init__(self)

    def emit(self, record):
        syslog.syslog(self.format(record))