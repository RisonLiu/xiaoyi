#-*- coding:gbk -*-
__author__ = 'liu.zhenghua@xiaoyi.com'
import platform
import time
import subprocess
import os
import httplib
import sys

def ping(ip, count=1, output=[]):
    try:
        t1 = time.time()
        if platform.system() == "Windows":
            p = subprocess.Popen(["ping", ip, "-n", "%d" % count], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        else:
            p = subprocess.Popen(["ping", ip, "-c", "%d" % count], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out = p.stdout.read()
        if p.stdin:
            p.stdin.close()
        if p.stdout:
            p.stdout.close()
        if p.stderr:
            p.stderr.close()
        try:
            p.kill()
        except OSError:
            pass
        t2 = time.time()
        bRtn = False
        if out.find(r"(0%") > 0 and out.find("无法访问目标主机") <= 0:
            if t2-t1 < 1:
                time.sleep(1)
            bRtn = True
        output.append(out)
    except Exception, ec:
        print ec
    return bRtn

def executeDosCmd(cmd):
    # os.popen("chcp 65001")
    fh = os.popen(cmd)
    lines = fh.readlines()
    iCnt = lines.__len__()
    for i in range(iCnt-1, -1, -1):
        if lines[i].strip() == "":
            del lines[i]
            continue
        # lines[i] = lines[i].decode("gbk")
    iCnt = lines.__len__()
    rtnStr = ""
    for i in range(0, iCnt, 1):
        rtnStr = rtnStr + "\r\n" + lines[i]
    return rtnStr.strip()

def __ignore_executeDosCmd(cmd, timeout=60):
    start = time.time()
    process = subprocess.Popen(cmd, bufsize=10000, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    while process.poll() is None:
        time.sleep(0.1)
        now = time.time()
        if now - start> timeout:
            try:
                process.terminate()
            except Exception,e:
                print e
                return None
            return None
    try:
        out = process.communicate(timeout=timeout-now+start)[0]
    except:
        return None
    if process.stdin:
        process.stdin.close()
    if process.stdout:
        process.stdout.close()
    if process.stderr:
        process.stderr.close()
    try:
        process.kill()
    except OSError:
        pass
    return out.strip()

def waitRebootCompleted(ip, block=10, maxCount=600, output=[]):
    iCnt = 0
    t0 = time.time()
    bRtn = False
    for i in range(1, maxCount, 1):
        t = time.time()-t0
        if not ping(ip, output=output):
            iCnt += 1
        elif (iCnt > 4 and t > block):
            bRtn = True
            break
        else:
            iCnt = 0
            t0 = time.time()
    return bRtn

def syncTime():
    try:
        conn = httplib.HTTPConnection("www.baidu.com")
        conn.request("GET", "/")
        r = conn.getresponse()
        ts = r.getheader('date')
        ltime = time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
        ttime = time.localtime(time.mktime(ltime)+8*60*60)
        dat = "date %u-%02u-%02u" % (ttime.tm_year, ttime.tm_mon, ttime.tm_mday)
        tm = "time %02u:%02u:%02u" % (ttime.tm_hour, ttime.tm_min, ttime.tm_sec)
        os.system(dat)
        os.system(tm)
        return True
    except:
        return False

def screenshoot(filename=None):
    from PIL import ImageGrab
    if filename is None:
        filename = time.strftime('%Y%m%d%H%M%S')
    if filename.find(":") <= 0:
        filename = os.path.dirname(sys.argv[0]) + "/log/" + filename
    filename = filename + ".png"
    dirStr = filename[:filename.rfind("/")]
    if not os.path.exists(dirStr):
        os.makedirs(dirStr)
    im = ImageGrab.grab()
    im.save(filename, 'png')
    return filename

def speak(txt, rate=0):
    import win32com.client
    spk = win32com.client.Dispatch("SAPI.SpVoice")
    spk.Rate = rate
    spk.Volume = 100
    spk.Speak(txt)

def writeFile(filename, context, append=True):
    if filename.rfind("/") > 0:
        dirStr = filename[:filename.rfind("/")]
    elif filename.rfind("\\") > 0:
        dirStr = filename[:filename.rfind('\\')]
    else:
        dirStr = "./"
    if not os.path.exists(dirStr):
        os.makedirs(dirStr)
    if append:
        fh = open(filename, "a")
    else:
        fh = open(filename, "w")
    try:
        if type(context) == list:
            for i in range(0, context.__len__()):
                try:
                    fh.write(str(context[i]))
                except:
                    fh.write(context[i].encode("gbk"))
        else:
            try:
                fh.write(str(context))
            except:
                fh.write(context.encode("gbk"))
    except:
        print sys.exc_info()
    finally:
        fh.close()

def readFile(filename):
    fh = open(filename, 'r')
    strContent = fh.read()
    fh.close()
    return strContent

if __name__ == "__main__":
    print __name__

