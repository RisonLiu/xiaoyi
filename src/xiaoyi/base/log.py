__author__ = 'liu.zhenghua@xiaoyi.com'
import logging
import time
import threading
import traceback
import os
class log():
    __mlock = threading.Lock()
    CRITICAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    def __init__(self, logfilename=None, level=logging.NOTSET, format='[%(asctime)s - %(threadName)s %(message)s'):
        self.__logger = logging.getLogger()
        self.__logger.setLevel(level)
        if logfilename is None:
            self.__filehander = logging.StreamHandler()
        else:
            self.__filehander = logging.FileHandler(logfilename)
        formatter = logging.Formatter(format)
        self.__filehander.setFormatter(formatter)

    def Print(self, level, msg, *args, **kwargs):
        msg = "- " + self.__getTrace() + "] " + msg
        log.__mlock.acquire()
        self.__logger.addHandler(self.__filehander)
        self.__logger.log(level, msg, *args, **kwargs)
        self.__logger.removeHandler(self.__filehander)
        log.__mlock.release()

    def Critical(self, msg, *args, **kwargs):
        msg = "- " + self.__getTrace() + "] " + msg
        log.__mlock.acquire()
        self.__logger.addHandler(self.__filehander)
        self.__logger.critical(msg, *args, **kwargs)
        self.__logger.removeHandler(self.__filehander)
        log.__mlock.release()

    def Error(self, msg, *args, **kwargs):
        msg = "- " + self.__getTrace() + "] " + msg
        log.__mlock.acquire()
        self.__logger.addHandler(self.__filehander)
        self.__logger.error(msg, *args, **kwargs)
        self.__logger.removeHandler(self.__filehander)
        log.__mlock.release()

    def Warning(self, msg, *args, **kwargs):
        msg = "- " + self.__getTrace() + "] " + msg
        log.__mlock.acquire()
        self.__logger.addHandler(self.__filehander)
        self.__logger.warning(msg, *args, **kwargs)
        self.__logger.removeHandler(self.__filehander)
        log.__mlock.release()

    def Info(self, msg, *args, **kwargs):
        msg = "- " + self.__getTrace() + "] " + msg
        log.__mlock.acquire()
        self.__logger.addHandler(self.__filehander)
        self.__logger.info(msg, *args, **kwargs)
        self.__logger.removeHandler(self.__filehander)
        log.__mlock.release()

    def Debug(self, msg, *args, **kwargs):
        msg = "- " + self.__getTrace() + "] " + msg
        log.__mlock.acquire()
        self.__logger.addHandler(self.__filehander)
        self.__logger.debug(msg, *args, **kwargs)
        self.__logger.removeHandler(self.__filehander)
        log.__mlock.release()

    def __getTrace(self):
        inf = traceback.extract_stack()[traceback.extract_stack().__len__()-3]
        return "%s - %s - %s" % (os.path.basename(inf[0]), inf[2], inf[1])
