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

# the port Tor runs on
SOCKS_PORT = 7000
# the connection to the common PostgreSQL database with databasename, user, host and the password used
dbConnectionString = "dbname='honeyconnector' user='honeyconnector' host='127.0.0.1' password='H0f3hL0VUyXCrZpunVUVnhsob'"
# the control port for HoneyConnector control messages
port = 38742

# ----- CRYPTOGRAPHIC STUFF -----
# Crypto stuff - this is for encrypting the connection between the client and the server modules
# This is probably a bad implementation and it should be changed in the future
BLOCK_SIZE = 32
PADDING = '}'
# IMPORTANT: Change this, before deploying in every module
keyHex = "f3be2f062adbdc63f4067431797b797df68c61a32e6a2d83d09ca17b18f44ece"

# Encrypt a message
def encrypt(message):
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
    key = binascii.unhexlify(keyHex)
    cipher = AES.new(key)
    return EncodeAES(cipher, message)

# Decrypt a message
def decrypt(message):
    DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)
    key = binascii.unhexlify(keyHex)
    cipher = AES.new(key)
    return DecodeAES(cipher, message)


# ----- FUNCTIONS SHARED BETWEEN MODULES -----
# This logs a newly creates username to the database for matching purposes
# It saves:the protocol, username, password, timestamp and the hex-id of the node
def saveUsernameToDB(username, password, node, protocol):
    dbConnection = psycopg2.connect(dbConnectionString)
    cur = dbConnection.cursor()
    cur.execute("""INSERT INTO credentials (protocol, username, password, date, node) VALUES (%s, %s, %s, %s, %s);""", (protocol, username, password, datetime.datetime.now(), node))
    dbConnection.commit()

# Checks if an username has ben used before to garantuee the uniqueness of the username
def isUsernameTaken(username):
    dbConnection = psycopg2.connect(dbConnectionString)
    cur = dbConnection.cursor()
    SQLstring = "SELECT COUNT(*) FROM credentials WHERE username = '"+username+"';"
    cur.execute(SQLstring)
    r = cur.fetchone()[0]
    return r == 1

# Sends a control message to another module, at this time this consists of creating and deleting users on the other modules    
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

# Logs a message in the common database
def logMessage(logMsg, msgType):    
    dbConnection = psycopg2.connect(dbConnectionString)
    cur = dbConnection.cursor()
    cur.execute("""INSERT INTO message (type, text, timestamp) VALUES (%s, %s, %s);""", (msgType, logMsg, datetime.datetime.now()))
    dbConnection.commit()

# ----- FTP MODULE FUNCTIONS -----
# Generates a new FTP username according to naming conventions
def generateFTPUsername(nodeName):
    randNr = random.randrange(1,999)
    letters = "abcdefghijklmnopqrstuvwxyz"
    randomLetters = random.choice(letters) + random.choice(letters)
    nameFragments = ["web"+str(randNr), "user"+str(randNr), "ftp"+str(randNr), "usr"+str(randNr), randomLetters+str(randNr).rjust(5, '0')]
    username = random.choice(nameFragments)
    return username
    
# Generates a new FTP password according to generation conventions
def generateFTPPW(nodeName):
    randNr = random.randrange(7,10)
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!$?"
    randomLetters = random.choice(letters)
    while len(randomLetters) < randNr:
        randomLetters = random.choice(letters) + randomLetters
    return randomLetters

# Handles the generation of the whole credentials and garantuees the uniqueness of the username. Returns both username and password
def generateFTPCredentials(nodeName):
    protocol = "ftp"
    password = generateFTPPW(nodeName)
    username = generateFTPUsername(nodeName)
    while isUsernameTaken(username):
        username = generateFTPUsername(nodeName)
    saveUsernameToDB(username, password, nodeName, protocol)
    return [username, password]

# I'm just a callback to print out some stuff on the console - don't look at me that judging, I'm here to help! 
def callbackerDummy(callback):
    print "Recieved file"

# Fishes out the filenames of the directory listing returned by the FTP server, so we can build a proper list    
def getFTPFileName(fileDetailsLine):
    filename = fileDetailsLine.split(" ")[-1]
    print fileDetailsLine
    if "drwxr" in fileDetailsLine:
        return "directory"
    else:
        return filename

# Sorts out files, if they are bait files or not. Bait files won't be requested from the server, so it won't be transferred
# IMPORTANT: Add the names or parts of the names of your bait files which will    
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

# And this removes the bait files from the list of files received by the server, so they won't be requested
def removeBaitFiles(fileList):
    for fileName in fileList:
        if hasBaitFileName(fileName):
            fileList.remove(fileName)
    return fileList

# This in essence simulates the whole FTP session, as similar as possible to the client FileZilla
def simulateFTPSession(username, password, ftpHost):
    try:
        # We use socksipy to wrap the ftplib to Tor, so the connection actually goes through the Tor network
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)
        socks.wrapmodule(ftplib)
        ftp = ftplib.FTP(timeout=60)
        # Connection and login
        ftp.connect(ftpHost, 21)
        ftp.timeout = 30
        ftp.login(username, password)
        # Some fancy commands FileZilla normally sends to servers
        print ftp.sendcmd("SYST")
        print ftp.sendcmd("FEAT")
        print ftp.pwd()
        # Okay, let's get the content of the main directory
        listLines = []
        ftp.dir(listLines.append)
        filenames = []
        for listLine in listLines:
            filenames.append(getFTPFileName(listLine))
        filenames = removeBaitFiles(filenames)
        if len(filenames) > 0:
            # Chose one of the filenames, if the server doesnt consist only of bait files
            filename = random.choice(filenames)
            # Let's wait a little, so the session doesn't look that automated
            waitTime = (random.random() * 20)
            print waitTime
            time.sleep(waitTime)
            # So let's download that file
            print ftp.sendcmd("MDTM " + filename)
            ftp.retrbinary('RETR ' + filename, callbackerDummy)
        # Let's wait a little, so the session doesn't look that automated
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

# Sends the control message to create a new user on the FTP servers
def createFTPUser(username, password, ftpHost):
    message = "FTP " + username + " " + password
    sendMessage(message, ftpHost)    

# Sends the control message to delete a user on the FTP servers    
def resetFTP(username, password, ftpHost):
    message = "FTP stop " + username + " " + password
    sendMessage(message, ftpHost)

# Main function of the FTP client module    
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
    
# ----- FTP MODULE FUNCTIONS -----
# Gets a random line from a file - used for the password files
def getRandomLineFromFile(fileName):
    filecontent = open(fileName).read().splitlines()
    line = random.choice(filecontent)
    return "".join(line.split())

# Gets an IMAP username fron a password file
def generateIMAPUsername(nodeName):
    filename = "facebook-firstnames.txt"
    return getRandomLineFromFile(filename)

# Gets an IMAP password fron a password file
def generateIMAPPW(nodeName):
    filename = "honeynet.txt"
    return getRandomLineFromFile(filename)

# Takes care of the whole generation of the IMAP filename and checks it for uniqueness
def generateIMAPCredentials(nodeName):
    protocol = "imap"
    password = generateIMAPPW(nodeName)
    username = generateIMAPUsername(nodeName)
    while isUsernameTaken(username):
        username = generateIMAPUsername(nodeName)
    saveUsernameToDB(username, password, nodeName, protocol)
    return [username, password]

# Sends the command to create a new user to the IMAP server modules
def createIMAPUser(username, password, imapHost):
    message = "IMAP " + username + " " + password 
    sendMessage(message, imapHost)

# Sends a custom IMAP command via a specified socket - was needed to recreate the behaviour of THunderbird    
def sendIMAPCommand(imapSocket, command):
    imapSocket.send(command)
    data = ''
    buf = imapSocket.recv(1024)
    while len(buf):
        data += buf
        buf = imapSocket.recv(1024)
    return data

# Simulates the whole IMAP session, trying to recreate the session that Thunderbird normally has when checking for new mails, finding none    
def simulateIMAPsession(username, password, imapHost, imapDomainName):
    try:
        # Tunnel through socksipy to Tor, wrapping imaplib through it
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)
        socks.socket.setdefaulttimeout(30)
        socks.wrapmodule(imaplib)
        # So let's log in and let the fun begin
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
        # Bye, IMAP server
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

# Sends a control message to the FTP server module to delete the user
def resetIMAP(username, password, imapHost):
    message = "IMAP stop " + username + " " + password
    sendMessage(message, imapHost)

# The main function of the IMAP module    
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
    
# ----- SSL MODULE FUNCTIONS -----
# Logs an certificate fraud to the database
def logSSLFraud(currentNode, url, torCert):
    dbConnection = psycopg2.connect(dbConnectionString)
    cur = dbConnection.cursor()
    cur.execute("""INSERT INTO "SSLFraud" (fingerprint, url, timestamp, certificate) VALUES (%s, %s, %s, %s);""", (currentNode.fingerprint, url, datetime.datetime.now(), torCert))
    dbConnection.commit()

# Main function of the SSL module, handles the whole comparision of HTTPS certificates of given URLs
def compareSSLCerts(currentNode):
    # The URLs to check HTTPS certificates on
    urls = ["facebook.com", "paypal.com", "mail.google.com", "amazon.com", "checkout.google.com", "accounts.google.com", "coinbase.com", "openid.net", "twitter.com", "steampowered.com", "steamcommunity.com", "clickandbuy.com", "www.paysafecard.com", "sofort.com" , "moneybookers.com"]
    # To avoid spending too much time on this when the exit node is down, we only will continue working on the queue if there were less than four timeouts
    errors = 0
    for url in urls:
        try:
            # So let's compare some certs!
            compareSSLCert(url, currentNode)
            time.sleep(1)
        except (socket.error, socks.Socks5Error, socks.GeneralProxyError, socks.ProxyError), e:
            # Aaaaand a lot can go wrong...
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
                
# Gets the certificate from a specific socket
def get_server_certificate_from_socket(addr, currentSocket):
    currentSocket.connect(addr)
    s = ssl.wrap_socket(currentSocket)
    dercert = s.getpeercert(True)
    s.close()
    return ssl.DER_cert_to_PEM_cert(dercert)

# Here is the most essential function of the SSL stuff: It gets the certificate through a normal socket, then through a tor socket and compares
def compareSSLCert(url, currentNode):
    print "checking ssl cert at", url
    # the normal socket
    normalSocket = socket.socket()
    normalSocket.settimeout(30)
    normalCert = get_server_certificate_from_socket((url, 443), normalSocket)
    normalSocket.close()
    # the Tor socket
    torSocket = socks.socksocket()
    torSocket.settimeout(30)
    torSocket.setproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', SOCKS_PORT)
    torCert = get_server_certificate_from_socket((url, 443), torSocket)
    torSocket.close()
    # Are they identical?
    certOK = normalCert == torCert
    if not certOK:
        logSSLFraud(currentNode, url, torCert)
        print "ALERT: certificate fraud at", url

# ----- MAIN FUNCTION STUFF -----

# Another funny callback function to help, this is from the stem tutorial as far as I remember...
def print_bootstrap_lines(line):
    if "Bootstrapped " in line:
        print term.format(line)

# This behemoth of a function handles one single Tor node
def testTorNode(dbConnection, currentNode):
    print "Starting Tor:"

    try:
        # Okay, let's launch Tor and use the exit node with a specific fingerprint
        tor_process = stem.process.launch_tor_with_config(
          config = {
            'SocksPort': str(SOCKS_PORT),
            'ExitNodes': currentNode.fingerprint,
            'StrictExitNodes': '1',
          },
          init_msg_handler = print_bootstrap_lines,
        )
        # If a certain amount of timeouts is reached, the node will be handled as offline and discarded from the queue to save time
        timeouts = 0
        
        if currentNode.hasHTTPS:
            # test HTTPS/SSL
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
            # test IMAP
            try:
                print "Node supports IMAP, using honey connection"
                testIMAP(currentNode, "192.168.1.2", "hypermailer.net")
                currentNode.madeIMAPLogin = True
            except (socket.error, socks.Socks5Error, socks.GeneralProxyError, socks.ProxyError), e:
                print "problems with allocating IMAP socket", e.message, traceback.format_exc()
                if "TTL expired" in e.message or "timed out" in e.message:
                    timeouts = timeouts + 1
                else:
                    raise
        if currentNode.hasFTP and timeouts < 2:
            # test FTP
            try:
                print "Node supports FTP, using honey connection"
                testFTP(currentNode, "192.168.1.3")
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
        # Close the connection to the Tor network
        TorHandler.saveChangesToDB(dbConnection, currentNode)
        print "terminating tor process (if any)"
        try:
            tor_process.terminate()
            time.sleep(1)
            tor_process.kill()
        except Exception, e:
            print "there is no tor process (or spoon)"
        print "done with", currentNode.fingerprint, currentNode.nickname, "\n"

# Gets the newest Tor node from the queue - if the queue is empty, fill it
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

# And here the obligatory main queue, with a shiny catch-em-all pokemon exception
while True:
    try:
        processQueue()
    except TypeError, e:
        print e.message
