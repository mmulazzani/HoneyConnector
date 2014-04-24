import os
import datetime
import psycopg2
import shutil

class LogExtractor():
    
    originalLogFile = "/var/log/dovecot-info.log"
    workingCopyLogFile = os.getcwd() + "/dovecot-info.log" 
    domainAt = "@hypermailer.net"
    dbConnectionString = "dbname='torlog' user='logger' host='127.0.0.1' password='H0f3hL0VUyXCrZpunVUVnhsob'"
    lastLog = datetime.datetime(2013, 4, 9, 1, 28, 30)

    def __init__(self):
        pass
    
    def prepareLastLog(self):
        logLines = open(self.workingCopyLogFile).read().splitlines()
        lastLogLine = logLines[-1].rsplit()
        date = lastLogLine[0]
        time = lastLogLine[1]
        self.lastLog = self.getDateTime(date, time)
        shutil.copy(self.originalLogFile, self.workingCopyLogFile)

    
    def getDateTime(self, date, time):
        tempDateTimeString = date + " " + time
        resultingDateTime = datetime.datetime.strptime(tempDateTimeString, "%Y-%m-%d %H:%M:%S")
        return resultingDateTime
    
    def saveToDB(self, dateTime, account, password, IP):
        dbConnection = psycopg2.connect(self.dbConnectionString)
        cur = dbConnection.cursor()
        cur.execute("""INSERT INTO "loginEvents" (protocol, account, password, timestamp, ip, type) VALUES (%s, %s, %s, %s, %s, %s);""", ("imap", account, password, dateTime, IP, "login-attempt"))
        dbConnection.commit()
    
    def isValidLogLine(self, logLine):
        return "pam_authenticate() failed:" in logLine
    
    def parseLogLine(self, logLine):
        splitLine = logLine.strip("()").rsplit()
        date = splitLine[0]
        time = splitLine[1]
        password = splitLine[-1]
        accountIPString = splitLine[4].replace("pam(", "").replace("):", "").replace(self.domainAt, "")
        accountIPList = accountIPString.split(",")
        account = accountIPList[0]
        IP = accountIPList[1]
        dateTime = self.getDateTime(date, time)
        return dateTime, account, password, IP
    
    def crawlLog(self):
        logLines = open(self.originalLogFile).read().splitlines()
        for logLine in logLines:
            if self.isValidLogLine(logLine):
                dateTime, account, password, IP = self.parseLogLine(logLine)
                if dateTime > self.lastLog:
                    self.saveToDB(dateTime, account, password, IP)
    
logExtract = LogExtractor()
logExtract.prepareLastLog()
logExtract.crawlLog()