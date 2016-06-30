#-*- coding:gbk -*-
__author__ = 'liu.zhenghua@xiaoyi.com'
from xiaoyi.lib.win import *
import threading

class Report():
    __instance = {}
    def __init__(self, reportfile, initItem=[]):
        if reportfile.find(":") <= 0 or not reportfile.startwith("/"):
            reportfile = "log/" + reportfile
        if os.path.dirname(sys.argv[0]) != "":
            reportfile = os.path.dirname(sys.argv[0]) + "/" + reportfile
        self.__file = reportfile
        if Report.__instance.get(self.__file) is None:
            Report.__instance.setdefault(self.__file, threading.Lock())
        self.__InitItem = []
        self.__KeyList = []
        self.__enableAppendKeyList = True
        for i in range(0, initItem.__len__(), 1):
            self.__InitItem.append(str(initItem[i][0]) + "=" + str(initItem[i][1]))
            self.__KeyList.append(str(initItem[i][0]))
        self.__Item = []

    def appendKeyList(self, keylist):
        self.__KeyList.extend(keylist)
        self.__enableAppendKeyList = False

    def Append(self, item, value):
        if self.__enableAppendKeyList:
            self.__KeyList.append(item)
        self.__Item.append(str(item)+"="+str(value))

    def __writeLog(self, context, append=True):
        # filename = os.path.dirname(sys.argv[0]) + "/log/" + self.__file
        writeFile(self.__file, context, append)

    def Clear(self):
        self.__Item = []

    def Output(self):
        Report.__instance.get(self.__file).acquire()
        outStr = ""
        tmpList = []
        tmpKeyList = []
        tmpKeyList.extend(self.__KeyList)
        tmpList.extend(self.__InitItem)
        tmpList.extend(self.__Item)
        self.__enableAppendKeyList = False
        if not os.path.exists(self.__file):
            outStr = "time"
            for i in range(0, self.__KeyList.__len__(), 1):
                outStr = outStr + "," + self.__KeyList[i]
            self.__writeLog(outStr+"\n")
        outStr = ""
        while tmpKeyList.__len__() > 0:
            tmpKey = tmpKeyList.pop()
            tmp = tmpList.pop()
            if tmp.startswith(tmpKey+"="):
                outStr = tmp[tmpKey.__len__()+1:] + "," + outStr
            else:
                if tmpKeyList.count(tmpKey) == 0:
                    tmpFind = False
                    for i in range(tmpList.__len__()-1, -1, -1):
                        if tmpList[i].startswith(tmpKey+"="):
                            outStr = tmpList[i][tmpKey.__len__()+1:] + "," + outStr
                            del tmpList[i]
                            tmpFind = True
                            break
                    if not tmpFind:
                        outStr = "," + outStr
                else:
                    outStr = "," + outStr
                tmpList.append(tmp)
        outStr = time.strftime('%Y-%m-%d %H:%M:%S') + "," + outStr[:-1]
        self.__writeLog(outStr+"\n")
        self.Clear()
        Report.__instance.get(self.__file).release()
