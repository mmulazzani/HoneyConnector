import os
import datetime
import psycopg2
import shutil

class LogExtractor():
    
    # The location of the file where dovecot logs the login attempts
    originalLogFile = "/var/log/dovecot-info.log"
    # The location of the file where a local copy of the file above will be handled
    workingCopyLogFile = os.getcwd() + "/dovecot-info.log" 
    # The domain your email honeypot uses
    domainAt = "@hypermailer.net"
    # the connection to the common PostgreSQL database with databasename, user, host and the password used
    dbConnectionString = "dbname='torlog' user='logger' host='127.0.0.1' password='H0f3hL0VUyXCrZpunVUVnhsob'"
    # before this point of time, the logger will ignore everything in the logfile before the initial import
    # gets used for the time the last log was parsed
    lastLog = datetime.datetime(2013, 4, 9, 1, 28, 30)

    def __init__(self):
        pass
    
    # gets the time of the last log extraction, then copies the newest logfile over the working copy 
    def prepareLastLog(self):
        logLines = open(self.workingCopyLogFile).read().splitlines()
        lastLogLine = logLines[-1].rsplit()
        date = lastLogLine[0]
        time = lastLogLine[1]
        self.lastLog = self.getDateTime(date, time)
        shutil.copy(self.originalLogFile, self.workingCopyLogFile)

    # reformats the timestamp
    def getDateTime(self, date, time):
        tempDateTimeString = date + " " + time
        resultingDateTime = datetime.datetime.strptime(tempDateTimeString, "%Y-%m-%d %H:%M:%S")
        return resultingDateTime
    
    # saves a log entry to the PostgreSQL database
    def saveToDB(self, dateTime, account, password, IP):
        dbConnection = psycopg2.connect(self.dbConnectionString)
        cur = dbConnection.cursor()
        cur.execute("""INSERT INTO "loginEvents" (protocol, account, password, timestamp, ip, type) VALUES (%s, %s, %s, %s, %s, %s);""", ("imap", account, password, dateTime, IP, "login-attempt"))
        dbConnection.commit()
    
    # checks if the log line has the pattern for the log lines we are looking for
    def isValidLogLine(self, logLine):
        return "pam_authenticate() failed:" in logLine
    
    # parses one log line and extracts the data
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
    
    # goes throgh the log, parses the lines of login attempts and saves them to the PostgreSQL database
    def crawlLog(self):
        logLines = open(self.originalLogFile).read().splitlines()
        for logLine in logLines:
            if self.isValidLogLine(logLine):
                dateTime, account, password, IP = self.parseLogLine(logLine)
                if dateTime > self.lastLog:
                    self.saveToDB(dateTime, account, password, IP)

# so let's go, prepare the log file and parse the new log file
logExtract = LogExtractor()
logExtract.prepareLastLog()
logExtract.crawlLog()