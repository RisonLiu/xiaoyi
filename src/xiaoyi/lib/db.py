#-*- coding:gbk -*-
__author__ = 'liu.zhenghua@xiaoyi.com'
import MySQLdb
import sqlite3
# from redis import *

class DB():
    def Close(self):
        self._conn.commit()
        self._session.close()
        self._conn.close()

    def Query(self, sql, type=tuple):
        self._session.execute(sql)
        rows = self._session.fetchall()
        if type == list:
            rows = list(rows)
            for i in range(0, rows.__len__()):
                rows[i] = list(rows[i])
        return rows

    def Commit(self):
        self._conn.commit()

    def Execute(self, sql, isCommit=False):
        rtn = self._session.execute(sql)
        if isCommit == True:
            self._conn.commit()
        return rtn

class mysql(DB):
    def __init__(self, host, user, passwd, database, port=3306):
        self._conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database, port=port)
        self._session = self._conn.cursor()

class sqLite(DB):
    def __init__(self, database=":memory:"):
        self._conn = sqlite3.connect(database)
        self._session = self._conn.cursor()


if __name__ == "__main__":
    print __name__
