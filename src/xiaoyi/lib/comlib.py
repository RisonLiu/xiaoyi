#-*- coding:gbk -*-
__author__ = 'liu.zhenghua@xiaoyi.com'

import serial
import time
import traceback
import sys
import threading

# 继电器控制程序
class Relay(object):
    __mlock = threading.Lock()
    __instance = {}
    WAIT_SECONDS = 0.04
    def __new__(cls, port, baudrate=9600, timeout=0.02):
        if cls.__mlock.acquire():
            if cls.__instance.get(port) is None:
                cls.__instance.setdefault(port, [super(Relay, cls).__new__(cls, port, baudrate, timeout), serial.Serial(port, baudrate, timeout=timeout)])
            cls.__mlock.release()
        return cls.__instance.get(port)[0]

    def __init__(self, port, baudrate=9600, timeout=0.1):
        self.__info = []
        self.__initInfo(self.__info)
        self.__ser = Relay.__instance.get(port)[1]

    def __initInfo(self, lstInfo=[]):
        lstInfo.append([[0x98, 0x35], [0xD9, 0xC5]])   #1
        lstInfo.append([[0xC9, 0xF5], [0x88, 0x05]])   #2
        lstInfo.append([[0x39, 0xF5], [0x78, 0x05]])   #3
        lstInfo.append([[0x68, 0x35], [0x29, 0xC5]])   #4
        lstInfo.append([[0xD9, 0xF4], [0x98, 0x04]])   #5
        lstInfo.append([[0x88, 0x34], [0xC9, 0xC4]])   #6
        lstInfo.append([[0x78, 0x34], [0x39, 0xC4]])   #7
        lstInfo.append([[0x29, 0xF4], [0x68, 0x04]])   #8
        lstInfo.append([[0x19, 0xF7], [0x58, 0x07]])   #9
        lstInfo.append([[0x48, 0x37], [0x09, 0xC7]])   #10
        lstInfo.append([[0xB8, 0x37], [0xF9, 0xC7]])   #11
        lstInfo.append([[0xE9, 0xF7], [0xA8, 0x07]])   #12
        lstInfo.append([[0x58, 0x36], [0x19, 0xC6]])   #13
        lstInfo.append([[0x09, 0xF6], [0x48, 0x06]])   #14
        lstInfo.append([[0xF9, 0xF6], [0xB8, 0x06]])   #15
        lstInfo.append([[0xA8, 0x36], [0xE9, 0xC6]])   #16

    def __OpenOne(self, sequence):
        try:
            if Relay.__mlock.acquire():
                sequence = sequence - 1
                self.__ser.write(chr(0xFE))
                self.__ser.write(chr(0x05))
                self.__ser.write(chr(0x00))
                self.__ser.write(chr(sequence))
                self.__ser.write(chr(0xFF))
                self.__ser.write(chr(0x00))
                self.__ser.write(chr(self.__info[sequence][0][0]))
                self.__ser.write(chr(self.__info[sequence][0][1]))
                time.sleep(self.WAIT_SECONDS)
                Relay.__mlock.release()
            return True
        except Exception:
            print traceback.print_exc()
            sys.exc_clear()
            Relay.__mlock.release()
        return False

    def __CloseOne(self, sequence):
        try:
            if Relay.__mlock.acquire():
                sequence = sequence - 1
                self.__ser.write(chr(0xFE))
                self.__ser.write(chr(0x05))
                self.__ser.write(chr(0x00))
                self.__ser.write(chr(sequence))
                self.__ser.write(chr(0x00))
                self.__ser.write(chr(0x00))
                self.__ser.write(chr(self.__info[sequence][1][0]))
                self.__ser.write(chr(self.__info[sequence][1][1]))
                time.sleep(self.WAIT_SECONDS)
                Relay.__mlock.release()
            return True
        except Exception:
            print traceback.print_exc()
            sys.exc_clear()
            Relay.__mlock.release()
        return False

    def Open(self, sequence=None):
        for k in range(0, 10):  #继电器操作，如果不成功，重试几次
            if sequence is not None:
                if not self.__OpenOne(sequence):
                    self.__OpenOne(sequence)
                bRtn = self.Query(sequence)
                if bRtn is None:
                    bRtn = self.Query(sequence)
            else:
                for i in range(1, 17, 1):
                    if not self.__OpenOne(i):
                        self.__OpenOne(i)
                bRtn = self.Query()
                if bRtn is None:
                    bRtn = self.Query()
                if bRtn == "1111111111111111":
                    bRtn = True
            if True == bRtn:
                break
            if bRtn is None:
                bRtn = False
        return bRtn

    def ReOpen(self, sequence=None, minInterval=0.35):
        t0 = time.time()
        bRtn = self.Close(sequence)
        cost = time.time() - t0
        if cost < minInterval:
            time.sleep(minInterval - cost)
        bRtn = bRtn and self.Open(sequence)
        return bRtn

    def Close(self, sequence=None):
        for k in range(0, 10):  #继电器操作，如果不成功，重试几次
            if not sequence is None:
                if not self.__CloseOne(sequence):
                    self.__CloseOne(sequence)
                bRtn = self.Query(sequence)
                if bRtn is None:
                    bRtn = not self.Query(sequence)
                else:
                    bRtn = not bRtn
            else:
                for i in range(1, 17, 1):
                    if not self.__CloseOne(i):
                        self.__CloseOne(i)
                bRtn = self.Query()
                if bRtn is None:
                    bRtn = self.Query()
                if bRtn == "0000000000000000":
                    bRtn = True
            if (bRtn is not None) and (bRtn == True):
                return bRtn
        return False

    def Query(self, sequence=None):
        try:
            if Relay.__mlock.acquire():
                self.__ser.write('\n')
                self.__ser.readlines()
                self.__ser.write(chr(0xFE))
                self.__ser.write(chr(0x01))
                self.__ser.write(chr(0x00))
                self.__ser.write(chr(0x00))
                self.__ser.write(chr(0x00))
                self.__ser.write(chr(0x10)) #01
                self.__ser.write(chr(0x29)) #E9
                self.__ser.write(chr(0xC9)) #C5
                time.sleep(self.WAIT_SECONDS)
                self.__ser.write('\n')
                rtnStatus = map(ord, self.__ser.readline())
                # print rtnStatus
                if rtnStatus.__len__() < 5:
                    print "TEST"
                    self.__ser.write(chr(0xFE))
                    self.__ser.write(chr(0x01))
                    self.__ser.write(chr(0x00))
                    self.__ser.write(chr(0x00))
                    self.__ser.write(chr(0x00))
                    self.__ser.write(chr(0x10)) #01
                    self.__ser.write(chr(0x29)) #E9
                    self.__ser.write(chr(0xC9)) #C5
                    time.sleep(self.WAIT_SECONDS)
                    self.__ser.write('\n')
                    rtnStatus = map(ord, self.__ser.readline())
                    print rtnStatus
                strStatus = self.__Dec2bin(rtnStatus[3]) + self.__Dec2bin(rtnStatus[4])
                Relay.__mlock.release()
            if(sequence is None):
                return strStatus
            return True if strStatus[sequence-1:sequence] == '1' else False
        except Exception:
            print traceback.print_exc()
            sys.exc_clear()
            Relay.__mlock.release()
        return

    def __Dec2bin(self, decStr):
        binStr = bin(decStr)
        if binStr.startswith("0b"):
            binStr = binStr[2:]
            while(binStr.__len__() < 8):
                binStr = "0" + binStr
            return binStr[::-1]

# 步进电机控制程序
class Motor(object):
    def __init__(self, port, driverPara=12800, baudrate=115200, timeout=0.1):
        self.__ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self.__driverPara23 = driverPara

    def __Dec2Hex(self, val, nbits=32):
        return "%08x" % int(hex((val + (1 << nbits)) % (1 << nbits))[2:-1], 16)

    def Step(self, angle=45, bWaitForStop=True, timeout=20):
        if angle >= 0:
            angle = angle % 360
        else:
            angle = -1 * (abs(angle) % 360)
        iPulse = angle * self.__driverPara23 / 30
        strHex = self.__Dec2Hex(iPulse)
        self.__ser.write('\n')
        self.__ser.write(chr(0x55))
        self.__ser.write(chr(0xaa))
        self.__ser.write(chr(0x08))
        self.__ser.write(chr(0x10))
        self.__ser.write(chr(0x27))
        self.__ser.write(chr(int(strHex[6:8], 16)))  # STETP
        self.__ser.write(chr(int(strHex[4:6], 16)))  # STETP
        self.__ser.write(chr(int(strHex[2:4], 16)))  # STETP
        self.__ser.write(chr(int(strHex[0:2], 16)))  # STETP
        self.__ser.write(chr(0xc3))
        self.__ser.write('\n')
        t0 = time.time()
        while bWaitForStop:
            st = self.Query()
            if st[0] == 32:
                break
            if st[1] == -1 and time.time()-t0 > timeout:
                break
            time.sleep(0.2)

    def Pause(self):
        self.__ser.write('\n')
        self.__ser.write(chr(0x55))
        self.__ser.write(chr(0xaa))
        self.__ser.write(chr(0x02))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0xc3))
        self.__ser.write('\n')

    def Query(self):
        self.__ser.write('\n')
        self.__ser.write(chr(0x55))
        self.__ser.write(chr(0xaa))
        self.__ser.write(chr(0x0c))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0x00))
        self.__ser.write(chr(0xc3))
        self.__ser.write('\n')
        lstRead = map(ord, self.__ser.readline())
        coordinate = -1
        status = 1
        if lstRead.__len__() == 8:
            coordinate = int("%02x%02x%02x%02x" % (lstRead[0], lstRead[1], lstRead[2], lstRead[3]), 16)
            status = lstRead[7]
        # print (status, coordinate)
        return (status, coordinate)


if __name__ == "__main__":
    print "__main__"
