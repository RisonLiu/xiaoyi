#-*- coding:gbk -*-
__author__ = 'liu.zhenghua@xiaoyi.com'
import ConfigParser
import os

class IniConf():
    def __init__(self, iniFile):
        self.__iniFile = iniFile
        self.__hidFile = iniFile[:-1*os.path.basename(iniFile).__len__()] + "." + os.path.basename(iniFile)
        self.__canRemove = False

    def create(self, section, kwargs):
        cfg = ConfigParser.ConfigParser()
        cfg.read(self.__iniFile)
        if not cfg.has_section(section):
            cfg.add_section(section)
        for key in kwargs:
            cfg.set(section, key, kwargs[key])
        cfg.write(open(self.__iniFile, "w"))
        self.__canRemove = True

    def destroy(self):
        if self.__canRemove:
            os.remove(self.__iniFile)

    def get(self, section, key):
        strRtn = None
        cfg = ConfigParser.ConfigParser()
        if os.path.exists(self.__hidFile):
            cfg.read(self.__hidFile)
            if not cfg.has_section(section):
                cfg.read(self.__iniFile)
            if cfg.has_section(section) and cfg.has_option(section, key):
                strRtn = cfg.get(section, key)
        elif os.path.exists(self.__iniFile):
            cfg.read(self.__iniFile)
            if cfg.has_section(section) and cfg.has_option(section, key):
                strRtn = cfg.get(section, key)
        return strRtn

    def set(self, section, key, value, chgsource=False):
        cfg = ConfigParser.ConfigParser()
        if os.path.exists(self.__hidFile):
            cfg.read(self.__hidFile)
            if not cfg.has_section(section):
                self.copy(section)
        else:
            self.copy(section)
        cfg = ConfigParser.ConfigParser()
        cfg.read(self.__hidFile)
        if not cfg.has_section(section):
            cfg.add_section(section)
        cfg.set(section, key, value)
        cfg.write(open(self.__hidFile, "w"))

    def remove(self, section, key=None):
        if os.path.exists(self.__hidFile):
            cfg = ConfigParser.ConfigParser()
            cfg.read(self.__hidFile)
            if cfg.has_section(section):
                if key is None:
                    cfg.remove_section(section)
                    cfg.write(open(self.__hidFile, "w"))
                elif cfg.has_option(section, key):
                    cfg.remove_option(section, key)
                    cfg.write(open(self.__hidFile, "w"))
            if cfg.sections().__len__() == 0:
                os.remove(self.__hidFile)

    def copy(self, section):
        print "********* copy :" + section
        if os.path.exists(self.__iniFile):
            cfg = ConfigParser.ConfigParser()
            cfg.read(self.__iniFile)
            if cfg.has_section(section):
                tmp = ConfigParser.ConfigParser()
                tmp.read(self.__hidFile)
                if tmp.has_section(section):
                    tmp.remove_section(section)
                tmp.add_section(section)
                for opt in cfg.options(section):
                    tmp.set(section, opt, cfg.get(section, opt))
                tmp.write(open(self.__hidFile, "w"))
