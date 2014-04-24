#!/usr/bin/python

import socket
import time
import random
import psycopg2
import datetime
import ftplib
import imaplib
import ssl
import TorHandler
import socks 
import stem.process
import traceback
from Crypto.Cipher import AES
import base64
import binascii

from stem.util import term

SOCKS_PORT = 7000
dbConnectionString = "dbname='torlog' user='logger' host='127.0.0.1' password='H0f3hL0VUyXCrZpunVUVnhsob'"

port = 38742

# Crypto stuff

BLOCK_SIZE = 32
PADDING = '}'
keyHex = "f3be2f062adbdc63f4067431797b797df68c61a32e6a2d83d09ca17b18f44ece"

def encrypt(message):
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    key = binascii.unhexlify(keyHex)
    cipher = AES.new(key)
    return EncodeAES(cipher, message)

def decrypt(message):
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
    key = binascii.unhexlify(keyHex)
    cipher = AES.new(key)
    return DecodeAES(cipher, message)

# SHARED STUFF =====

def saveUsernameToDB(username, password, node, protocol):
    dbConnection = psycopg2.connect(dbConnectionString)
    cur = dbConnection.cursor()
    cur.execute("""INSERT INTO credentials (protocol, username, password, date, node) VALUES (%s, %s, %s, %s, %s);""", (protocol, username, password, datetime.datetime.now(), node))
    dbConnection.commit()

def isUsernameTaken(username):
    dbConnection = psycopg2.connect(dbConnectionString)
    cur = dbConnection.cursor()
    SQLstring = "SELECT COUNT(*) FROM credentials WHERE username = '"+username+"';"
    cur.execute(SQLstring)
    r = cur.fetchone()[0]
    return r == 1
    
def sendMessage(message, host):
    socket.socket = socks._orgsocket
    commandSocket = socket.socket()
    commandSocket.connect((host, port))
    replayAttackProof = str(random.randrange(1,9999))
    replayAttackProofedMessage = replayAttackProof + " " + message
    messageEnc = encrypt(replayAttackProofedMessage) 
    commandSocket.send(messageEnc)
    commandSocket.shutdown(socket.SHUT_RDWR)
    commandSocket.close       

def logMessage(logMsg, msgType):    
    dbConnection = psycopg2.connect(dbConnectionString)
    cur = dbConnection.cursor()
    cur.execute("""INSERT INTO message (type, text, timestamp) VALUES (%s, %s, %s);""", (msgType, logMsg, datetime.datetime.now()))
    dbConnection.commit()

# FTP STUFF ======

def generateFTPUsername(nodeName):
    randNr = random.randrange(1,999)
    letters = "abcdefghijklmnopqrstuvwxyz"
    randomLetters = random.choice(letters) + random.choice(letters)
    nameFragments = ["web"+str(randNr), "user"+str(randNr), "ftp"+str(randNr), "usr"+str(randNr), randomLetters+str(randNr).rjust(5, '0')]
    username = random.choice(nameFragments)
    return username
    
def generateFTPPW(nodeName):
    randNr = random.randrange(7,10)
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!$?"
    randomLetters = random.choice(letters)
    while len(randomLetters) < randNr:
        randomLetters = random.choice(letters) + randomLetters
    return randomLetters

def generateFTPCredentials(nodeName):
    protocol = "ftp"
    password = generateFTPPW(nodeName)
    username = generateFTPUsername(nodeName)
    while isUsernameTaken(username):
        username = generateFTPUsername(nodeName)
    saveUsernameToDB(username, password, nodeName, protocol)
    return [username, password]


def callbackerDummy(callback):
    print "Recieved file"
    
def getFTPFileName(fileDetailsLine):
    filename = fileDetailsLine.split(" ")[-1]
    print fileDetailsLine
    if "drwxr" in fileDetailsLine:
        return "directory"
    else:
        return filename
    
def hasBaitFileName(fileName):
    if "visa" in fileName:
        return True
    elif "master" in fileName:
        return True
    elif "directory" in fileName:
        return True
    elif "auth" in fileName:
        return True
    elif "login" in fileName:
        return True
    elif "download" in fileName:
        return True
    elif "xls" in fileName:
        return True
    elif "key" in fileName:
        return True
    elif "account" in fileName:
        return True
    elif "paypal" in fileName:
        return True
    elif "vpn" in fileName:
        return True
    elif "steam-acs" in fileName:
        return True
    else:
        return False
    
def removeBaitFiles(fileList):
    for fileName in fileList:
        if hasBaitFileName(fileName):
            fileList.remove(fileName)
    return fileList

def simulateFTPSession(username, password, ftpHost):
    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)
        socks.wrapmodule(ftplib)
        ftp = ftplib.FTP(timeout=60)
        ftp.connect(ftpHost, 21)
        ftp.timeout = 30
        ftp.login(username, password)
        print ftp.sendcmd("SYST")
        print ftp.sendcmd("FEAT")
        print ftp.pwd()
        listLines = []
        ftp.dir(listLines.append)
        filenames = []
        for listLine in listLines:
            filenames.append(getFTPFileName(listLine))
        filenames = removeBaitFiles(filenames)
        if len(filenames) > 0:
            filename = random.choice(filenames)
            waitTime = (random.random() * 20)
            print waitTime
            time.sleep(waitTime)
            print ftp.sendcmd("MDTM " + filename)
            ftp.retrbinary('RETR ' + filename, callbackerDummy)
        waitTime = (random.random() * 30)
        print waitTime
        time.sleep(waitTime)
        print ftp.quit()
    except Exception:
        raise
    finally:
        try:
            ftp.close()
        except Exception:
            pass

def createFTPUser(username, password, ftpHost):
    message = "FTP " + username + " " + password
    sendMessage(message, ftpHost)    
    
def resetFTP(username, password, ftpHost):
    message = "FTP stop " + username + " " + password
    sendMessage(message, ftpHost)
    
def testFTP(currentNode, ftpHost):
    try:
        time.sleep(10)
        FTPcredentials = generateFTPCredentials(currentNode.fingerprint)
        FTPusername = FTPcredentials[0]
        FTPpassword = FTPcredentials[1]
        print "Creating FTP user with password: ", FTPusername, FTPpassword
        createFTPUser(FTPusername, FTPpassword, ftpHost)
        time.sleep(45)
        simulateFTPSession(FTPusername, FTPpassword, ftpHost)
        time.sleep(5)
    except Exception:
        raise
    finally:
        resetFTP(FTPusername, FTPpassword, ftpHost)
    
# IMAP STUFF ======

def getRandomLineFromFile(fileName):
    filecontent = open(fileName).read().splitlines()
    line = random.choice(filecontent)
    return "".join(line.split())

def generateIMAPUsername(nodeName):
    filename = "facebook-firstnames.txt"
    return getRandomLineFromFile(filename)

def generateIMAPPW(nodeName):
    filename = "honeynet.txt"
    return getRandomLineFromFile(filename)

def generateIMAPCredentials(nodeName):
    protocol = "imap"
    password = generateIMAPPW(nodeName)
    username = generateIMAPUsername(nodeName)
    while isUsernameTaken(username):
        username = generateIMAPUsername(nodeName)
    saveUsernameToDB(username, password, nodeName, protocol)
    return [username, password]

def createIMAPUser(username, password, imapHost):
    message = "IMAP " + username + " " + password 
    sendMessage(message, imapHost)
    
def sendIMAPCommand(imapSocket, command):
    imapSocket.send(command)
    data = ''
    buf = imapSocket.recv(1024)
    while len(buf):
        data += buf
        buf = imapSocket.recv(1024)
    return data
    
def simulateIMAPsession(username, password, imapHost, imapDomainName):
    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)
        socks.socket.setdefaulttimeout(30)
        socks.wrapmodule(imaplib)
        mail = imaplib.IMAP4(imapHost, 143)
        mail.login(username+'@'+imapDomainName, password)
        print "namespace", mail.namespace()
        print "lsub", mail.lsub()
        print "list inbopx", mail.list("", "INBOX")
        selectanswer = mail.select("INBOX")
        print "select inbox",selectanswer
        responsecode, data = selectanswer
        lastmail = data[0]
        fetchflag = lastmail + ":*"
        print "fetch uid" , mail.fetch(fetchflag,"(FLAGS)")
        mail.logout()
        socket.socket = socks._orgsocket
    except Exception:
        raise
    finally:
        try:
            mail.logout()
            mail.shutdown()
        except Exception:
            pass
        finally:
            socket.socket = socks._orgsocket


def resetIMAP(username, password, imapHost):
    message = "IMAP stop " + username + " " + password
    sendMessage(message, imapHost)
    
def testIMAP(currentNode, imapHost, imapDomainName):
    try:
        IMAPcredentials = generateIMAPCredentials(currentNode.fingerprint)
        IMAPusername = IMAPcredentials[0]
        IMAPpassword = IMAPcredentials[1]
        print "Creating IMAP user with password:", IMAPusername, IMAPpassword
        createIMAPUser(IMAPusername, IMAPpassword, imapHost)
        # wait till mailbox is populated
        time.sleep(30)
        simulateIMAPsession(IMAPusername, IMAPpassword, imapHost, imapDomainName)
        time.sleep(5)
    except Exception:
        raise
    finally:
        resetIMAP(IMAPusername, IMAPpassword, imapHost)
    
## SSL CERT

def logSSLFraud(currentNode, url, torCert):
    dbConnection = psycopg2.connect(dbConnectionString)
    cur = dbConnection.cursor()
    cur.execute("""INSERT INTO "SSLFraud" (fingerprint, url, timestamp, certificate) VALUES (%s, %s, %s, %s);""", (currentNode.fingerprint, url, datetime.datetime.now(), torCert))
    dbConnection.commit()

def compareSSLCerts(currentNode):
    urls = ["facebook.com", "paypal.com", "mail.google.com", "amazon.com", "checkout.google.com", "accounts.google.com", "coinbase.com", "openid.net", "twitter.com", "steampowered.com", "steamcommunity.com", "clickandbuy.com", "www.paysafecard.com", "sofort.com" , "moneybookers.com"]
    errors = 0
    for url in urls:
        try:
            compareSSLCert(url, currentNode)
            time.sleep(1)
        except (socket.error, socks.Socks5Error, socks.GeneralProxyError, socks.ProxyError), e:
            if "TTL expired" in e.message or "time" in e.message:
                print "Certificate timeout"
                errors = errors + 1
                if errors >= 3:
                    urls = []
                    raise
            elif "Host unreachable" in e.message:
                print "Host unreachable"
            else:
                raise
                

def get_server_certificate_from_socket(addr, currentSocket):
    currentSocket.connect(addr)
    s = ssl.wrap_socket(currentSocket)
    dercert = s.getpeercert(True)
    s.close()
    return ssl.DER_cert_to_PEM_cert(dercert)

def compareSSLCert(url, currentNode):
    print "checking ssl cert at", url
    normalSocket = socket.socket()
    normalSocket.settimeout(30)
    normalCert = get_server_certificate_from_socket((url, 443), normalSocket)
    normalSocket.close()
    torSocket = socks.socksocket()
    torSocket.settimeout(30)
    torSocket.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)
    torCert = get_server_certificate_from_socket((url, 443), torSocket)
    torSocket.close()
    certOK = normalCert == torCert
    if not certOK:
        logSSLFraud(currentNode, url, torCert)
        print "ALERT: certificate fraud at", url

## main function, tests one tor node

def print_bootstrap_lines(line):
    if "Bootstrapped " in line:
        print term.format(line)

def testTorNode(dbConnection, currentNode):
    print "Starting Tor:"

    try:
        tor_process = stem.process.launch_tor_with_config(
          config = {
            'SocksPort': str(SOCKS_PORT),
            'ExitNodes': currentNode.fingerprint,
            'StrictExitNodes': '1',
          },
          init_msg_handler = print_bootstrap_lines,
        )
        timeouts = 0
        
        if currentNode.hasHTTPS:
            try:
                print "Node supports HTTPS, testing certificates"
                compareSSLCerts(currentNode)
                currentNode.madeSSLCheck = True
            except (socket.error, socks.Socks5Error, socks.GeneralProxyError, socks.ProxyError), e:
                print "problems with allocating HTTPS socket", e.message, traceback.format_exc()
                if "TTL expired" in e.message or "timed out" in e.message:
                    timeouts = timeouts + 1
                else:
                    raise
        if currentNode.hasIMAP:
            try:
                print "Node supports IMAP, using honey connection"
                testIMAP(currentNode, "37.187.52.237", "hypermailer.net")
                currentNode.madeIMAPLogin = True
            except (socket.error, socks.Socks5Error, socks.GeneralProxyError, socks.ProxyError), e:
                print "problems with allocating IMAP socket", e.message, traceback.format_exc()
                if "TTL expired" in e.message or "timed out" in e.message:
                    timeouts = timeouts + 1
                else:
                    raise
        if currentNode.hasFTP and timeouts < 2:
            try:
                print "Node supports FTP, using honey connection"
                testFTP(currentNode, "88.198.161.146")
                currentNode.madeFTPLogin = True
            except (socket.error, socks.Socks5Error, socks.GeneralProxyError, socks.ProxyError), e:
                print "problems with allocating FTP socket", e.message, traceback.format_exc()
                if "TTL expired" in e.message or "timed out" in e.message:
                    timeouts = timeouts + 1
                else:
                    raise        
    except (socket.error, socks.Socks5Error, socks.GeneralProxyError, socks.ProxyError), e:
        if "TTL expired" in e.message or "timed out" in e.message:
            print "node seems offline or broken, removing from queue..."
            TorHandler.removeNodeFromQueue(dbConnection, currentNode)
    except Exception, e:
        logMsg = "unknown exception:\nfingerprint: " + currentNode.fingerprint + "\nexception: " + e.message + "\nstacktrace:\n" + traceback.format_exc()
        logMessage(logMsg, "exception")
    finally:
        TorHandler.saveChangesToDB(dbConnection, currentNode)
        print "terminating tor process (if any)"
        try:
            tor_process.terminate()
            time.sleep(1)
            tor_process.kill()
        except Exception, e:
            print "there is no tor process (or spoon)"
        print "done with", currentNode.fingerprint, currentNode.nickname, "\n"

def processQueue():
    socket.setdefaulttimeout(35)
    socks.socket.setdefaulttimeout(35)
    dbConnection = psycopg2.connect(dbConnectionString)
    if not TorHandler.isQueueEmpty(dbConnection):
        currentNode = TorHandler.getNextNodeFromQueue(dbConnection)
        print "New node from queue:", currentNode.fingerprint, currentNode.nickname, currentNode.address
        testTorNode(dbConnection, currentNode)
        time.sleep(5)
    else:
        msg = "Queue empty, filling queue"
        logMessage(msg, "queue-fill")
        print msg
        socket.socket = socks._orgsocket
        TorHandler.fillQueue(dbConnection)
        logMessage("Queue filled", "queue-fill-success")

while True:
    try:
        processQueue()
    except TypeError, e:
        print e.message
