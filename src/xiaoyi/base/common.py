#-*- coding:gbk -*-
__author__ = 'liu.zhenghua@xiaoyi.com'
from xiaoyi.lib.win import *
import os
import sys
import time
import urllib
import hmac
import requests
from hashlib import *
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]

def renameLogFile(oldfilename, newfilename):
    oldfilename = __formatFileName(oldfilename)
    newfilename = __formatFileName(newfilename)
    try:
        os.rename(oldfilename, newfilename)
    except:
        os.rename(oldfilename, newfilename)

def writeLog(filename, context, append=True):
    filename = __formatFileName(filename)
    timestr = time.strftime('\n===============log time : %Y-%m-%d %H:%M:%S===============\n')
    writeFile(filename, timestr, append)
    writeFile(filename, context, True)

def __formatFileName(filename):
    if filename.find(":") <= 0 and (False == filename.startswith("/")):
        filename = "log/" + filename
        if os.path.dirname(sys.argv[0]) != "":
            filename = os.path.dirname(sys.argv[0]) + "/" + filename
    return filename

def hmacEncode(strText, strKey, sha=sha1):
    hashed = hmac.new(strKey, strText, sha)
    return hashed.digest().encode("base64").rstrip('\n')

def aesEncrypt(strMsg, strKey, mode=AES.MODE_ECB):
    aes_obj = AES.new(strKey, mode)
    return b2a_hex(aes_obj.encrypt(pad(strMsg))).upper()


def aesDecrypt(strMsg, strKey, mode=AES.MODE_ECB):
    aes_obj = AES.new(strKey, mode)
    return unpad(aes_obj.decrypt(a2b_hex(strMsg))).strip()

def send_request(host, path, raw="", params=None, method="get", **kwargs):
    if params is None:
        params = {}
    raw = raw.strip()
    if method == "post":
        if raw.find("=")>0:
            for param in raw.split("&"):
                p_split = param.split("=")
                params[p_split[0]] = urllib.unquote(p_split[1])
            raw = ""
    if method == "put":
        for (n, v) in params.items():
            if raw.__len__() == 0:
                raw = n + "=" + urllib.quote(v)
            else:
                raw = raw + "&" + n + "=" + urllib.quote(v)
    if raw.__len__() > 0:
        raw = "?" + raw
    try:
        try:
            r = apply(eval("requests." + method), [host + path + raw, params], kwargs)
            r.close()
        except Exception,ec:
            print ec
            time.sleep(0.5)
            r = apply(eval("requests." + method), [host + path + raw, params], kwargs)
            r.close()
        cost = -1
        retDict = {"status": r.status_code, "content": r.text.strip().encode("utf-8"), "cost": -1}
        if r.ok:
            retDict["cost"] = r.elapsed.total_seconds()*1000
            retDict["cookies"] = r.cookies
        return retDict
    except Exception, ec:
        print ec
    return False


if __name__ == "__main__":
    print "__main__"






