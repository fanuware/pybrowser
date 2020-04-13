#!/usr/bin/env python3

import sqlite3
import hashlib
import os
import re
import templates
import uuid

class _UserLogger:

    # user permissions
    PERMISSION_NONE = 0
    PERMISSION_READ = 1
    PERMISSION_WRITE = 2
    PERMISSION_ADMIN = 3
    ALLOW_PUBLIC = "[all]"

    # maximum session duration, starts after login [s]
    _MAX_SESSION_DURATION = 60 * 60 * 24 * 365
    
    # maximum login fails
    _MAX_LOGIN_FAILS = 10

    # master password ('admin')
    _PWS_INIT_MASTER = "c7ad44cbad762a5da0a452f9e854fdc1e0e7a52a38015f23f3eab1d80b931dd472634dfac71cd34ebc35d16ab7fb8a90c81f975113d6c7538dc69dd8de9077ec"

    # database
    _LOGGER_DATABASE = 'userlogger.sqlite'

    def __init__(self):
        '''initialize database and and set up current user tables'''

        # identify user
        self.connectionId = hashlib.sha512(os.urandom(16)).hexdigest()
        self.sessionKey = ''
        if 'HTTP_COOKIE' in os.environ:
            cookies = dict()
            cookiesList = os.environ['HTTP_COOKIE'].split('; ')
            for cookie in cookiesList:
                if '=' in cookie:
                    cookie = cookie.split('=')
                    cookies[cookie[0]] = cookie[1]
            self.connectionId = cookies.get('connection_identifier', self.connectionId)
            self.sessionKey = cookies.get('session_key', self.sessionKey)

        # create table and user
        cur = self.__openDb()
        cur.execute('CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY, name VARCHAR(50) NOT NULL UNIQUE, password CHAR(128), permissions TEXT)')
        cur.execute('CREATE TABLE IF NOT EXISTS State (id INTEGER, connectionId VARCHAR(255) PRIMARY KEY, loginHashSeed CHAR(128), sessionId CHAR(128), targetUrl TEXT, copyUrl TEXT, login_time TIMESTAMP, last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(id) REFERENCES users(id))')
        cur.execute('CREATE TABLE IF NOT EXISTS Fails (connectionId VARCHAR(255) PRIMARY KEY, counter INTEGER DEFAULT 0)')

        # create tables for user
        if (not cur.execute('SELECT * FROM State WHERE connectionId=?', (self.connectionId,)).fetchone()):
            cur.execute('INSERT INTO State (connectionId) VALUES (?)', (self.connectionId,))
        self.__closeDb()

    def changeConnectionId(self, connectionId=str(uuid.uuid4())):
        cur = self.__openDb()
        cur.execute('DELETE FROM State WHERE connectionId=?', (self.connectionId,))
        self.connectionId = connectionId
        cur.execute('INSERT INTO State (connectionId) VALUES (?)', (self.connectionId,))
        self.__closeDb()
        return self.connectionId

    def userAdd(self, name, password, path, accessPermission):
        '''add new user'''
        if (self.getPermission(os.sep) == self.PERMISSION_ADMIN):
            cur = self.__openDb()
            try:
                path = path.rstrip(os.sep)
                passwordEncrypted = hashlib.sha512(password.encode()).hexdigest()
                cur.execute('INSERT INTO Users (name, password, permissions) VALUES (?,?,?)',
                    (name, passwordEncrypted, path + '$' + str(accessPermission)))
            except:
                pass
            self.__closeDb();

    def userDelete(self, name):
        '''delete user'''
        if (self.getPermission(os.sep) == self.PERMISSION_ADMIN):
            cur = self.__openDb()
            cur.execute('DELETE FROM State WHERE id=(SELECT id FROM users WHERE name=?)', (name,))
            cur.execute('DELETE FROM Users WHERE name=?', (name,))
            self.__closeDb();

    def login(self, name):
        '''user login'''
        self.resetCopyUrl()
        cur = self.__openDb()

        # track login fails
        cur.execute('SELECT counter FROM Fails WHERE connectionId=?', (self.connectionId,))
        fetchone = cur.fetchone()
        if not fetchone:
            cur.execute('INSERT INTO Fails (connectionId, counter) VALUES (?, 0)', (self.connectionId,))
            counter = 0;
        else:
            cur.execute('SELECT counter FROM Fails WHERE connectionId=?', (self.connectionId,))
            counter = fetchone[0]

        # retrieve seed
        cur.execute('SELECT loginHashSeed FROM State WHERE connectionId=?', (self.connectionId,))
        fetchone = cur.fetchone()
        loginSeed = "" if not fetchone or not fetchone[0] else fetchone[0]
        
        cur.execute('SELECT sessionId FROM State WHERE connectionId=?', (self.connectionId,))
        fetchone = cur.fetchone()
        sessionSeed = "" if not fetchone or not fetchone[0] else fetchone[0]

        # verify name and password
        uid = None
        cur.execute('SELECT id, password FROM Users WHERE name=?', (name,))
        fetchone = cur.fetchone()
        if fetchone and hashlib.sha512(
            hashlib.sha512(fetchone[1].encode() +
                           loginSeed.encode()).hexdigest().encode() +
            sessionSeed.encode()).hexdigest() == self.sessionKey:
            # set user to be authorized
            uid = fetchone[0]

        if uid and counter < self._MAX_LOGIN_FAILS:

            # set user to be authorized
            cur.execute('UPDATE State SET id=?, login_time=CURRENT_TIMESTAMP WHERE connectionId=?', (uid, self.connectionId,))
            cur.execute('UPDATE Fails SET counter=0 WHERE connectionId=?', (self.connectionId,))
        else:

            # create administrator as first user
            if not cur.execute('SELECT * FROM Users').fetchone():
                cur.execute('INSERT INTO Users (name, password, permissions) VALUES (?,?,?)',
                            ('admin', hashlib.sha512(self._PWS_INIT_MASTER.encode()).hexdigest(),
                             os.sep + '$' + str(self.PERMISSION_ADMIN)))
            
            # login rejected
            cur.execute('UPDATE State SET login_time=NULL WHERE connectionId=?', (self.connectionId,))
            cur.execute('UPDATE Fails SET counter=counter+1 WHERE connectionId=?', (self.connectionId,))
        self.__closeDb()

    def logout(self):
        '''logout'''
        cur = self.__openDb()
        cur.execute('UPDATE State SET login_time=NULL WHERE connectionId=?', (self.connectionId,))
        self.__closeDb()

    def isLoggedIn(self):
        '''is user logged in'''
        cur = self.__openDb()
        # validate maximal login time
        cur.execute('SELECT name FROM Users WHERE id = (SELECT id FROM State WHERE connectionId=? and CURRENT_TIMESTAMP BETWEEN login_time AND DATETIME(login_time, ? ))',
                    (self.connectionId, ('+'+str(self._MAX_SESSION_DURATION)+' seconds')))
        fetch = cur.fetchone()
        ret = None if fetch is None else fetch[0]
        self.__closeDb()
        return ret

    def getPermission(self, targetUrl):
        '''get user access permission'''
        cur = self.__openDb()
        permissionPublic = ""
        permissionUser = ""
        accessPermission = self.PERMISSION_NONE

        # validate public permissions
        cur.execute("SELECT permissions FROM Users WHERE name LIKE '%" + self.ALLOW_PUBLIC + "%'")
        for p in cur.fetchall():
            permissionPublic += p[0] + ":"
        
        # validate maximal login time
        cur.execute('SELECT login_time FROM State WHERE connectionId=? and CURRENT_TIMESTAMP BETWEEN login_time AND DATETIME(login_time, ? )',
                    (self.connectionId, ('+'+str(self._MAX_SESSION_DURATION)+' seconds')))
        if cur.fetchone():

            # retrieve seed
            cur.execute('SELECT loginHashSeed FROM State WHERE connectionId=?', (self.connectionId,))
            fetchone = cur.fetchone()
            loginSeed = "" if not fetchone or not fetchone[0] else fetchone[0]

            cur.execute('SELECT sessionId FROM State WHERE connectionId=?', (self.connectionId,))
            fetchone = cur.fetchone()
            sessionSeed = "" if not fetchone or not fetchone[0] else fetchone[0]
            
            # verify name and password
            cur.execute('SELECT id, password FROM Users WHERE id=(SELECT id FROM State WHERE connectionId=?)', (self.connectionId,))
            fetchone = cur.fetchone()
            if fetchone and hashlib.sha512(hashlib.sha512(fetchone[1].encode() + 
                                                          loginSeed.encode()).hexdigest().encode() +
                                           sessionSeed.encode()).hexdigest() == self.sessionKey:
                
                # check user permission
                cur.execute('SELECT permissions FROM Users WHERE id=(SELECT id FROM State WHERE connectionId=?)', (self.connectionId,))

                fetch = cur.fetchone()
                if fetch:
                    permissionUser = fetch[0]
        
        for p in (permissionPublic + permissionUser).strip(":").split(":"):
            permit = p.split("$")
            if (permit[0] == os.sep) or (targetUrl + os.sep).startswith(permit[0] + os.sep):
                if len(permit) == 2:
                    accessPermission = max(accessPermission, int(permit[1]))
        self.__closeDb()
        return accessPermission

    def showLogin(self, message):
        '''show login page'''
        randomHash = hashlib.sha512(os.urandom(16)).hexdigest()
        cur = self.__openDb()
        cur.execute('UPDATE State SET loginHashSeed=? WHERE connectionId=?', (randomHash, self.connectionId,))
        cur.execute('UPDATE State SET sessionId=? WHERE connectionId=?', (randomHash, self.connectionId,))
        self.__closeDb()
        templates.login(msg=message, random=randomHash)
    
    def nextSession(self):
        '''generate next session seed'''
        randomHash = hashlib.sha512(os.urandom(16)).hexdigest()
        cur = self.__openDb()
        cur.execute('UPDATE State SET sessionId=? WHERE connectionId=?', (randomHash, self.connectionId,))
        self.__closeDb()
        return randomHash
    
    def generateSession(self):
        '''generate next session seed'''
        randomHash = hashlib.sha512(os.urandom(16)).hexdigest()
        return randomHash
    
    def saveSession(self, sessionId):
        '''generate next session seed'''
        cur = self.__openDb()
        cur.execute('UPDATE State SET sessionId=? WHERE connectionId=?', (sessionId, self.connectionId,))
        self.__closeDb()

    def setCopyUrl(self, copyUrl):
        '''set copy url, used when user want to copy a file'''
        cur = self.__openDb()
        cur.execute('UPDATE State SET copyUrl=? WHERE connectionId=?', (copyUrl, self.connectionId))
        self.__closeDb()

    def getCopyUrl(self):
        '''get copy url, used when user want to paste a file'''
        cur = self.__openDb()
        cur.execute('SELECT copyUrl FROM State WHERE connectionId=?', (self.connectionId,))
        receivedData = cur.fetchone()
        self.__closeDb()

        # return time
        if receivedData:
            return receivedData[0]

    def resetCopyUrl(self):
        '''reset copy url'''
        cur = self.__openDb()
        cur.execute('UPDATE State SET copyUrl=NULL WHERE connectionId=?', (self.connectionId,))
        self.__closeDb()

    def setTargetUrl(self, targetUrl):
        '''set target url, keeps track of last user action'''
        cur = self.__openDb()
        cur.execute('UPDATE State SET targetUrl=? WHERE connectionId=?', (targetUrl, self.connectionId))
        self.__closeDb()
    
    def getTargetUrl(self):
        '''get target url'''
        cur = self.__openDb()
        cur.execute('SELECT targetUrl FROM State WHERE connectionId=?', (self.connectionId,))
        receivedData = cur.fetchone()
        self.__closeDb()

        # return time
        if receivedData:
            return receivedData[0]
    
    def getUserList(self):
        '''get user list'''
        cur = self.__openDb()
        cur.execute('SELECT name, permissions FROM Users')
        receivedData = cur.fetchall()
        self.__closeDb()
        return receivedData

    def __openDb(self):
        '''open database, returns cursor'''
        try:
            self.cur
        except:
            self.cur = None
        if self.cur is None:
            self.conn = sqlite3.connect(self._LOGGER_DATABASE)
            self.cur = self.conn.cursor()
        return self.cur

    def __closeDb(self):
        '''close database'''
        try:
            self.cur
        except:
            self.cur = None
        if self.cur is not None:
            self.conn.commit()
            self.conn.close()
            self.cur = None

class UserLogger:
    # user permissions
    PERMISSION_NONE = 0
    PERMISSION_READ = 1
    PERMISSION_WRITE = 2
    
    instance = None
    def __init__(self):
        if not UserLogger.instance:
            UserLogger.instance = _UserLogger()
    def __getattr__(self, name):
        return getattr(self.instance, name)
