#-*- coding:gbk -*-
__author__ = 'liu.zhenghua@xiaoyi.com'
import imp
from xiaoyi.lib import *

# Parallel
class MultiThreadRun():
    def __init__(self, client, loopParam, *args, **kwargs):
        self.__LoopParam = loopParam
        self.__args = args
        self.__kwargs = kwargs
        self.__stoped = False
        self.__client = client

    def runOneDevice(self, *args, **kwargs):
        inst = apply(self.__client, list(args), kwargs)
        idx = 1
        while self.stop() == False:
            if self.__maxCount is not None and idx > self.__maxCount:
                break
            inst.testCase()
            idx += 1

    def stop(self):
        return self.__stoped

    def __doMonitor(self, cfg, threadpool=[]):
        try:
            strDepend = cfg.get(self.__client.__name__, "depend")
            lifetime = cfg.get(self.__client.__name__, "timeout")
            if lifetime is None:
                lifetime = 60
            else:
                lifetime = int(lifetime)

            if strDepend is not None:
                isRun = cfg.get(strDepend, "run")
                while(isRun == "0" or isRun is None):
                    print "monitor thread is alive : %s wait %s finished !" % (self.__client.__name__, strDepend)
                    time.sleep(30)
                    isRun = cfg.get(strDepend, "run")
                    if isRun == "1":
                        print "monitor thread is alive : %s wait %s release resource !" % (self.__client.__name__, strDepend)
                        time.sleep(70)  # 等待资源被释放
            # 等待依赖的模块执行完成后，立即start本模块执行线程
            for th in threadpool:
                th.start()
            start_time = time.time()
            idx = 0
            inf = self.__getThreadInfo(threadpool)
            # print "monitor thread is alive : run process %d/100, total thread : %d, alive thread : %d" % (idx, inf[0], inf[1])
            deltT = 0
            heartbeat = 60
            if heartbeat > lifetime/10:
                heartbeat = int(lifetime/10)
            while(time.time() - start_time < lifetime):
                time.sleep(heartbeat)
                deltT += heartbeat
                if int((time.time() - start_time) * 100 / lifetime) > idx:
                    deltT = 0
                    idx = int((time.time() - start_time) * 100 / lifetime)
                    if idx > 100:
                        idx = 100
                    inf = self.__getThreadInfo(threadpool)
                    print "monitor thread is alive : run process %d/100, total thread : %d, alive thread : %d" % (idx, inf[0], inf[1])
                else:
                    print "monitor thread is alive : run process %d/100-%d, total thread : %d, alive thread : %d" % (idx, deltT/heartbeat, inf[0], inf[1])
                # 如果线程中途都异常退出了，则提前结束
                if self.__allThreadFinished(threadpool):
                    break
        finally:
            self.__stoped = True
            # wait for all thread finish
            while(True):
                if self.__allThreadFinished(threadpool):
                    break
                time.sleep(5)
            cfg.set(self.__client.__name__, "run", "1")
            # 为了让其它依赖该模块的测试程序能抓到它已经结束的状态，此处等待60s后再从配置文件中删除
            if cfg._IniConf__canRemove == False:
                time.sleep(60)
            cfg.remove(self.__client.__name__)
            cfg.destroy()

    def __allThreadFinished(self, threadpool=[]):
        bRtn = True
        for th in threadpool:
            if th.isAlive():
                bRtn = False
                break
        return bRtn

    def __getThreadInfo(self, threadpool=[]):
        iTotal = threadpool.__len__()
        iAlive = 0
        for th in threadpool:
            if th.isAlive():
                iAlive += 1
        return (iTotal, iAlive)

    def run(self, **kwargs):
        cfgFile = "conf/main.ini"
        # if kwargs != {}:
        #     cfgFile = "conf/" + self.__client.__name__ + "_" + time.strftime('%Y%m%d%H%M%S') + ".ini"
        cfg = IniConf(cfgFile)
        # if kwargs != {}:
        #     print kwargs
        #     cfg.create(self.__client.__name__, kwargs=kwargs)
        cfg.copy(self.__client.__name__)
        for (key, value) in kwargs.items():
            cfg.set(self.__client.__name__, key, value)
        try:
            if "1" == cfg.get(self.__client.__name__, "run"):
                return
            self.__maxCount = cfg.get(self.__client.__name__, "count")
            if self.__maxCount is not None:
                self.__maxCount = int(self.__maxCount)
            threadpool = []
            for item in self.__LoopParam:
                tmpArgs = self.__args
                if type(item) == list:
                    tmpArgs = tuple(item) + tmpArgs
                else:
                    tmpArgs = (item,) + tmpArgs
                th = threading.Thread(target=self.runOneDevice, args=tmpArgs, kwargs=self.__kwargs)
                threadpool.append(th)
            thMonitor = threading.Thread(target=self.__doMonitor, args=(cfg, threadpool))
            thMonitor.start()
        except:
            self.__stoped = True
            if {} == kwargs:
                time.sleep(120)
            cfg.set(self.__client.__name__, "run", "1")
            time.sleep(20)
            cfg.remove(self.__client.__name__)

