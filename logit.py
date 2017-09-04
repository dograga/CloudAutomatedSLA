#!/usr/bin/python
import logging
from logging.handlers import RotatingFileHandler
class logit():
    def __init__(self,filepath):
        self.logger = logging.getLogger('uptime_check')
        hdlr = logging.handlers.TimedRotatingFileHandler(filepath,when='W0',interval=1,backupCount=5)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def logadd(self,msg,mtype):
        print msg
        if mtype=='info':
            self.logger.info(msg)
        else:
            self.logger.error(msg)
