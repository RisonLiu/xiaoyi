__author__ = 'liu.zhenghua@xiaoyi.com'
import functools
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import const
import time
import gevent
import gevent.monkey
gevent.monkey.patch_all()

def debug(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if const.Debug:
                print "[%s] begin function : %s%s%s" % (time.strftime('%Y-%m-%d %H:%M:%S'), func.__name__, str(args[1:]), str(kwargs))
        except:pass
        rtn = func(*args, **kwargs)
        try:
            if const.Debug:
                print "[%s] end function : %s = %s" % (time.strftime('%Y-%m-%d %H:%M:%S'), func.__name__, str(rtn))
        except:pass
        return rtn
    return wrapper

class Paralleled(object):
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls, *args, **kwargs)

    def run(self, tag="task_"):
        tasks = []
        lstDir = dir(self)
        for method in lstDir:
            if method.startswith(tag):
                m = getattr(self, method)
                tasks.append(gevent.spawn(m))
        gevent.joinall(tasks)

class Email():
    toUser = None
    Subject = ""
    Context = ""
    Attach = None
    def __init__(self, smtpServer, username, passwd):
        self.__msg = MIMEMultipart()
        self.__server = smtplib.SMTP()
        self.__server.connect(smtpServer)
        self.__server.login(username, passwd)
        self.__fromuser = username + "@" + smtpServer[smtpServer.find(".")+1:]

    def __del__(self):
        if self.__server is not None:
            self.__server.close()

    def __doContext(self):
        txt = MIMEText(self.Context.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>"), _subtype='html', _charset='gb2312')
        self.__msg.attach(txt)

    def __doAttach(self):
        if self.Attach is None:
            return
        self.Attach = self.Attach.replace(";", ",")
        attList = self.Attach.split(",")
        for att in attList:
            temp = MIMEText(open(att, 'rb').read(), 'base64', 'gb2312')
            temp["Content-Type"] = 'application/octet-stream'
            filename = os.path.basename(att).decode("gbk").encode("utf-8")
            temp["Content-Disposition"] = 'attachment; filename="%s"' % filename
            self.__msg.attach(temp)

    def __doInit(self):
        self.__msg['to'] = self.toUser
        self.__msg['from'] = self.__fromuser
        self.__msg['subject'] = self.Subject.decode("gbk").encode("utf-8")

    def send(self):
        self.__doInit()
        self.__doContext()
        self.__doAttach()
        self.__server.sendmail(self.__fromuser, self.toUser, self.__msg.as_string())
        self.__server.quit()

    def close(self):
        self.__server.close()
        self.__server = None

if __name__ == "__main__":
    print __name__