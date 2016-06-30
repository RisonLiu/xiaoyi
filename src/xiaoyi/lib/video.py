#-*- coding:gbk -*-
__author__ = 'liu.zhenghua@xiaoyi.com'
import os
import win32api
import win32con
import time

class Video():
    def __init__(self,mediaPlayerPath=r"D:\Program Files (x86)\Baofeng\StormPlayer\StormPlayer.exe"):
        self.__mplayer = mediaPlayerPath
        self.__play = True

    def start(self,videofile="D:\\video\\VID_20151016_183107.mp4"):
        cmd = r'start ""  "' + self.__mplayer + r'"  "'+videofile+ r'"'
        os.system(cmd)

    def stop(self):
        prcessName = self.__mplayer[self.__mplayer.rfind("\\")+1:]
        #print prcessName
        os.system(r'taskkill /im "' + prcessName + r'" /f /t')

    def pause(self):
        if not self.__play:
            return
        self.__pressSpaceBar()
        self.__play = False


    def replay(self):
        if self.__play:
            return
        self.__pressSpaceBar()
        self.__play = True

    def __pressSpaceBar(self):
        win32api.keybd_event(32,0,0,0)
        win32api.keybd_event(32,0,win32con.KEYEVENTF_KEYUP,0)

if __name__ == "__main__":
    print __name__
    # v = Video()
    # v.start("D:\\video\\VID_20151016_183107.mp4")
    # time.sleep(5)
    # v.stop()

