#-*- coding:gbk -*-
__author__ = 'liu.zhenghua@xiaoyi.com'
import telnetlib
import paramiko
import serial
import socket
from win import *
from abc import ABCMeta, abstractmethod

class remoteConnect(object):
    def __new__(cls, *args, **kwargs):
        cls._session = None
        cls._prompt = None
        return object.__new__(cls, *args, **kwargs)

    def login(self):
        if self._session is None:
            self._session = self._createSession()

        if self._user is not None:
            self._read_until('ogin: ', 5)
            self._session.write(self._user + '\n')
        else:
            self._session.write("\n")
        if self._passwd is not None:
            self._read_until("assword:", 1).strip()
            self._session.write(self._passwd + "\n")
        rtnStr = self._read_until(self._prompt, 2).strip()
        if rtnStr.strip().endswith(">"):
            self.__doAbnormal()
        if not rtnStr.endswith(self._prompt):
            self.close()
            self._waitForPing()
            self.relogin()

    def __doAbnormal(self):
        if "Serial" != self._session.__class__.__name__:
            return
        # `]})"'
        lst = [r'"', r"'", r")", r"}", r"]", r"`"]
        for i in range(0, lst.__len__(), 1):
            self._session.write(lst[i] + "\n")
            rst = self._read_until(timeout=1)
            if rst.strip().endswith(self._prompt):
                return

    def command(self, cmd, finish=None, timeout=3, onlyResult=False):
        if finish is None:
            if self._prompt is None:
                finish = "\r\n"
            else:
                finish = "\r\n" + self._prompt
        try:
            self._session.write(cmd + "\n")
            rtn = self._read_until(finish, timeout).strip()
            if(rtn.strip(self._prompt).strip() == ""):
                temp = self._read_until(finish, timeout)
                if temp.__len__() > rtn.__len__():
                    rtn = temp
            if(onlyResult == True):
                rtn = rtn[cmd.__len__()+1:].strip()
                if(finish ==  "\r\n" + self._prompt):
                    rtn = rtn[:-1*self._prompt.__len__()].strip()
            return rtn
        except:
            self._waitForPing()
            self.relogin()
            # print cmd
            return self.command(cmd, finish, timeout, onlyResult)

    def close(self):
        self._session.close()

    def relogin(self):
        try:
            self.close()
        finally:
            self._session = self._createSession()
        self.login()

    @abstractmethod
    def _createSession(self):pass

    @abstractmethod
    def _read_until(self, finish, timeout):pass

    def _waitForPing(self):
        if "Serial" == self._session.__class__.__name__:
            return
        t0 = time.time()
        while(ping(self._host, 4) == False and time.time()-t0<self._maxWaitSecond):
            print self._host + " connect timeout !"

class telnet(remoteConnect):
    def __init__(self, host, user=None, passwd=None, prompt=None, maxWaitSecond=60):
        self._host = host
        self._user = user
        self._passwd = passwd
        self._prompt = prompt
        self._maxWaitSecond = maxWaitSecond
        self.login()

    def _createSession(self):
        try:
            return telnetlib.Telnet(self._host, 23, 10)
        except:
            self._waitForPing()
            return telnetlib.Telnet(self._host, 23, 10)

    def _read_until(self, finish, timeout):
        return self._session.read_until(finish, timeout)

class ssh(remoteConnect):
    def __init__(self, host, user=None, passwd=None, prompt=None, maxWaitSecond=60):
        self._host = host
        self._user = user
        self._passwd = passwd
        self._prompt = prompt
        self._maxWaitSecond = maxWaitSecond
        self.login()

    def _createSession(self):
        __ssh = paramiko.SSHClient()
        __ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return __ssh

    def login(self):
        if self._session is None:
            self._session = self._createSession()
        self._session.connect(self._host, 22, self._user, self._passwd)

    def command(self, cmd, finish=None, timeout=3, onlyResult=False):
        stdin, stdout, stderr = self._session.exec_command(cmd, timeout=timeout)
        rtnStr = "".join(stdout.readlines())
        if onlyResult == False:
            rtnStr = "%s\n%s" % (cmd, rtnStr)
        return rtnStr

class com(remoteConnect):
    def __init__(self, port, baudrate=115200, user=None, passwd=None, prompt=None, timeout=1):
        self.__port = port
        self.__baudrate = baudrate
        self._user = user
        self._passwd = passwd
        self._timeout = timeout
        self._prompt = prompt
        self.login()

    def _createSession(self):
        return serial.Serial(self.__port, self.__baudrate, timeout=self._timeout)

    def _read_until(self, finish="#", timeout=None):
        t0 = time.time()
        data = ''
        while True:
            data += self._session.read(1)
            if not timeout is None and time.time()-t0 > timeout:
                break
            if data.endswith(finish):
                break
        return data

    def __del__(self):pass

class socketclient():
    def __init__(self, ip, port):
        self.__session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__session.connect((ip, port))
        self.__session.settimeout(1)

    def send(self, msg):
        self.__session.send(msg)

    def recv(self, finish=None, timeout=10):
        t0 = time.time()
        data = ''
        while True:
            try:
                rcvStr = self.__session.recv(512)
            except:
                break
            data += rcvStr
            if rcvStr.__len__() < 512:
                break
            if timeout is not None and time.time()-t0 > timeout:
                break
            if finish is not None and data.find(finish) > 0:
                break
        return data

    def close(self):
        self.__session.close()

'''
import zmq.green as zmq
from .protocol import Message

class BaseSocket(object):

    def send(self, msg):
        self.sender.send(msg.serialize())

    def recv(self):
        data = self.receiver.recv()
        return Message.unserialize(data)


class Server(BaseSocket):
    def __init__(self, host, port):
        context = zmq.Context()
        self.receiver = context.socket(zmq.PULL)
        self.receiver.bind("tcp://%s:%i" % (host, port))

        self.sender = context.socket(zmq.PUSH)
        self.sender.bind("tcp://%s:%i" % (host, port+1))


class Client(BaseSocket):
    def __init__(self, host, port):
        context = zmq.Context()
        self.receiver = context.socket(zmq.PULL)
        self.receiver.connect("tcp://%s:%i" % (host, port+1))

        self.sender = context.socket(zmq.PUSH)
        self.sender.connect("tcp://%s:%i" % (host, port))
'''

if __name__ == "__main__":
    print "__main__"


