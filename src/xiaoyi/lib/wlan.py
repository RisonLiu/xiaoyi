#-*- coding:gbk -*-
__author__ = 'liu.zhenghua@xiaoyi.com'
import os
import threading
import time
import sys
from win import *

class Wlan():
    __mlock = threading.Lock()

    # ������wifi���ӱ�Ϊ�ֶ�ģʽ
    def __init__(self):
        lstWifi = self.getProfileList()
        self.__alreadyAddProfileList = []
        for wifi in lstWifi:
            os.popen("netsh wlan set profileparameter name=" + wifi + " connectionmode=manual")
            # executeDosCmd("netsh wlan delete profile name=" + wifi)

    # def __del__(self):
        # lstWifi = self.getProfileList()
        # for wifi in lstWifi:
        #     os.popen("netsh wlan set profileparameter name=" + wifi + " connectionmode=auto")

    def getProfileList(self):  # ��ȡ��ǰ�������п���wifi
        lstWifi = []
        fh = os.popen("netsh wlan show profiles")
        lines = fh.readlines()
        iCnt = lines.__len__()
        for i in range(iCnt-1, 0, -1):
            if lines[i].strip() == "":
                del lines[i]
                continue
            if lines[i].find("-------") >= 0:
                break
            tmp = lines[i].split(":")
            if tmp[0].find("�����û������ļ�")>=0:
                lstWifi.append(tmp[1].strip())
        return lstWifi

    def getCurProfile(self):
        dictInfo = self.getWifiInfo()
        if (dictInfo.has_key("״̬") and dictInfo["״̬"] == "������") or (dictInfo.has_key("State") and dictInfo["State"] == "connected"):
            return dictInfo["SSID"]
        return False

    def connect(self, profilename, timeout=60):
        Wlan.__mlock.acquire()
        curProfile = self.getCurProfile()
        if curProfile != profilename:
            self.disconnect()
            os.popen("netsh wlan connect name=" + profilename)
            bRtn = False
            t_start = time.time()
            while time.time() - t_start < timeout:
                curProfile = self.getCurProfile()
                if curProfile == profilename:
                    bRtn = True
                    break
                time.sleep(2)
        else:
            bRtn = True
        if bRtn == True:
            bRtn = False
            netgate = self.getNetGate()
            t_start = time.time()
            while time.time() - t_start < timeout:
                if True == ping(netgate):
                    bRtn = True
                    break
                time.sleep(1)
        Wlan.__mlock.release()
        return bRtn

    def disconnect(self):
        os.popen("netsh wlan disconnect")
        time.sleep(2)
        dictInfo = self.getWifiInfo()
        t0 = time.time()
        bRtn = True
        while (dictInfo.has_key("״̬") and dictInfo["״̬"] != "�ѶϿ�����") or (dictInfo.has_key("State") and dictInfo["State"] != "disconnected"):
            if time.time() - t0 > 60:
                bRtn = False
                break
            time.sleep(2)
            dictInfo = self.getWifiInfo()
        return bRtn

    def addwifi(self, ssid, passwd):
        if self.__alreadyAddProfileList.count(ssid) > 0:
            return
        os.popen('netsh wlan delete profile name="' + ssid + '"')
        filename = "conf/wifi_" + ssid + ".xml"
        strContent = '<?xml version="1.0"?>\n'
        strContent = strContent + '<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">\n'
        strContent = strContent + '<name>' + ssid + '</name>\n'
        strContent = strContent + '<SSIDConfig>\n'
        strContent = strContent + '<SSID>\n'
        strContent = strContent + '<name>' + ssid + '</name>\n'
        strContent = strContent + '</SSID>\n'
        strContent = strContent + '</SSIDConfig>\n'
        strContent = strContent + '<connectionType>ESS</connectionType>\n'
        strContent = strContent + '<connectionMode>manual</connectionMode>\n'
        strContent = strContent + '<MSM>\n'
        strContent = strContent + '<security>\n'
        strContent = strContent + '<authEncryption>\n'
        strContent = strContent + '<authentication>WPA2PSK</authentication>\n'
        strContent = strContent + '<encryption>AES</encryption>\n'
        strContent = strContent + '<useOneX>false</useOneX>\n'
        strContent = strContent + '</authEncryption>\n'
        strContent = strContent + '<sharedKey>\n'
        strContent = strContent + '<keyType>passPhrase</keyType>\n'
        strContent = strContent + '<protected>false</protected>\n'
        strContent = strContent + '<keyMaterial>' + passwd + '</keyMaterial>\n'
        strContent = strContent + '</sharedKey>\n'
        strContent = strContent + '</security>\n'
        strContent = strContent + '</MSM>\n'
        strContent = strContent + '</WLANProfile>\n'
        writeFile(filename, strContent, False)
        os.popen('netsh wlan add profile filename="' + filename + '"')
        self.__alreadyAddProfileList.append(ssid)
        os.remove(filename)

    def getNetGate(self):
        dictInfo = self.getWifiInfo()
        if dictInfo.has_key("�����ַ"):
            macAddress = dictInfo["�����ַ"].replace(":","-").upper()
        strRst = executeDosCmd("ipconfig -all")
        strRst = strRst[strRst.find(macAddress):]
        strRst = strRst[strRst.find("Ĭ������"):]
        strRst = strRst[strRst.find(":")+1:strRst.find("\n")]
        return strRst.strip()

    def getWifiInfo(self):
        strRst = executeDosCmd("netsh wlan show interfaces")
        strRst = strRst[strRst.find("����"):strRst.find("��������״̬")]
        lstRst = strRst.split("\n")
        dictRtn = {}
        for item in lstRst:
            if item.strip().__len__()>0:
                dictRtn.setdefault(item[0:item.find(":")].strip(), item[item.find(":")+1:].strip())
        return dictRtn



if __name__ == "__main__":
    print "__main__"

