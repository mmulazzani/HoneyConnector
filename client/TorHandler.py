import socket
import datetime
import sys
import stem.process

from stem.util import term
from stem.control import Controller
from stem.descriptor.remote import DescriptorDownloader

# the port Tor runs on
SOCKS_PORT = 7000

# the IP of your FTP server
FTP_SERVER_IP = "88.198.161.146"

# the IP of your IMAP server
IMAP_SERVER_IP = "37.187.52.237"

# this class is used to save the information about the Tor node to be processed or while being processed
class TorNode:
    madeFTPLogin = False
    madeIMAPLogin = False
    madeSSLCheck = False
    
    def __init__(self, nodeid, nickname, fingerprint, address, published, uptime, contact, queueTimestamp, hasHTTPS, hasIMAP, hasFTP, exitPolicies, platformVersion):
        self.nodeid = nodeid
        self.nickname = nickname
        self.fingerprint = fingerprint
        self.address = address
        self.published = published
        self.uptime = uptime
        self.contact = contact
        self.queueTimestamp = queueTimestamp
        self.hasHTTPS = hasHTTPS
        self.hasIMAP = hasIMAP
        self.hasFTP = hasFTP
        self.exitPolicies = exitPolicies
        self.platformVersion = platformVersion
        
    

# Perform DNS resolution through the socket - i think this was from a tutorial
def getaddrinfo(*args):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

socket.getaddrinfo = getaddrinfo

# Another funny callback function to help, this is from the stem tutorial as far as I remember...
def print_bootstrap_lines(line):
    if "Bootstrapped " in line:
        print term.format(line)

# Adds an Tor node to the queue in the database
def addItemToQueue(dbConnection, desc, now, i):
    nickname = desc.nickname
    fingerprint = desc.fingerprint
    address = desc.address
    published = desc.published
    uptime = desc.uptime
    contact = str(desc.contact)
    queueTimestamp = now
    hasHTTPS = desc.exit_policy.can_exit_to(address = FTP_SERVER_IP, port = 443)
    hasIMAP = desc.exit_policy.can_exit_to(address = IMAP_SERVER_IP, port = 143)
    hasFTP = desc.exit_policy.can_exit_to(address = FTP_SERVER_IP, port = 21)
    exitPolicies = ""
    exitPoliciesList = desc.exit_policy 
    for exitPolicy in exitPoliciesList:
        exitPolicies = exitPolicies + str(exitPolicy) + "\r\n"
    platformVersion = str(desc.tor_version) + " " + desc.operating_system
    if (hasHTTPS or hasIMAP or hasFTP):
        print i, "adding", nickname, fingerprint, address, published, uptime, contact, queueTimestamp, hasHTTPS, hasIMAP, hasFTP
        cur = dbConnection.cursor()
        cur.execute("""INSERT INTO queue ("nickname", "fingerprint", "address", "published", "uptime", "contact", "queueTimestamp", "hasHTTPS", "hasIMAP", "hasFTP", "exitPolicies", "platformVersion") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", (nickname, fingerprint, address, published, uptime, contact, queueTimestamp, hasHTTPS, hasIMAP, hasFTP, exitPolicies, platformVersion))
        dbConnection.commit()
    else:
        print i, "skipping", nickname, fingerprint, address, published, uptime, contact, queueTimestamp, hasHTTPS, hasIMAP, hasFTP

# Fills the queue.
# IMPORTANT: Set your own control password here
def fillQueue(dbConnection):
    print term.format("Starting Tor:\n")

    # Launch Tor
    tor_process = stem.process.launch_tor_with_config(
      config = {
        'SocksPort': str(SOCKS_PORT),
        'ControlPort': '9051',
        'HashedControlPassword': '16:268106D01BA5D72060EF5302A17BF60B10D980F0FEA121D1B1D343AEBA',
      },
      init_msg_handler = print_bootstrap_lines,
      take_ownership = True,
    )
    now = datetime.datetime.now()
    downloadSuccessful = False
    errorCount = 0
    while not downloadSuccessful:
        try:
            controller = Controller.from_port(port = 9051)
            # IMPORTANT: Change the password to the fitting "HashedControlPassword" set in the Torrc by stem, a few lines above here 
            controller.authenticate("schnitzel")
            downloader = DescriptorDownloader()
            # Now tefth those servers and add them to the queue
            serverDescriptors =downloader.get_server_descriptors().run()
            i = 1
            for desc in serverDescriptors:
                if desc.exit_policy.is_exiting_allowed():
                    addItemToQueue(dbConnection, desc, now, i)
                    i = i+1
            downloadSuccessful = True
        except:
            e = sys.exc_info()[0]
            print e
            errorCount = errorCount + 1
            if (errorCount >= 5):
                print "HUGE CLUSTERFUCK, stopping execution"
                tor_process.kill()  # stops tor
                raise
    tor_process.kill()  # stops tor

# Fetches a node from the queue and returns a Tor node object
def getNextNodeFromQueue(dbConnection):
    cur = dbConnection.cursor()
    SQLstring = """SELECT * FROM "queue" ORDER BY "queueTimestamp", "uptime" LIMIT 1;"""
    cur.execute(SQLstring)
    result = cur.fetchone()
    nodeid = result[0]
    nickname = result[1]
    fingerprint = result[2]
    address = result[3]
    published = result[4]
    uptime = result[5]
    contact = result[6]
    queueTimestamp = result[7]
    hasHTTPS = result[8]
    hasIMAP = result[9]
    hasFTP = result[10]
    exitPolicies = result[11]
    platformVersion = result[12]
    currentNode = TorNode(nodeid, nickname, fingerprint, address, published, uptime, contact, queueTimestamp, hasHTTPS, hasIMAP, hasFTP, exitPolicies, platformVersion)
    return currentNode
    
# Checks if a node with a certain fingerprint is already in the database of nodes
def isNodeInDB(dbConnection, currentNode):
    cur = dbConnection.cursor()
    cur.execute("""SELECT COUNT(*) FROM "knownNodes" WHERE "fingerprint" = %s;""", (currentNode.fingerprint,))
    r = cur.fetchone()[0]
    return r == 1

# Checks if a node's IP is already in the database
def isNodeIPInDB(dbConnection, currentNode):
    cur = dbConnection.cursor()
    cur.execute("""SELECT COUNT(*) FROM "knownNodeIPs" WHERE "fingerprint" = %s AND "address" = %s;""", (currentNode.fingerprint, currentNode.address))
    r = cur.fetchone()[0]
    return r == 1

# Updates the node in the database after it was processed in the queue
def updateNodeInDB(dbConnection, currentNode):
    FTPLogin = 0
    IMAPLogin = 0
    SSLCheck = 0
    if currentNode.madeFTPLogin:
        FTPLogin = 1
    if currentNode.madeIMAPLogin:
        IMAPLogin = 1
    if currentNode.madeSSLCheck:
        SSLCheck = 1
    cur = dbConnection.cursor()    
     
    cur.execute("""UPDATE "knownNodes" SET "lastSeen" = %s, "countIMAPLogins" = "countIMAPLogins" + %s, "countFTPLogins" = "countFTPLogins" + %s, "countSSLChecks" = "countSSLChecks" + %s, "exitPolicies" = %s, "platformVersion" = %s  WHERE "fingerprint" = '"""+currentNode.fingerprint+"""';""", (currentNode.queueTimestamp, IMAPLogin, FTPLogin, SSLCheck, currentNode.exitPolicies, currentNode.platformVersion))
    dbConnection.commit()

# Adds a new node to the database of nodes
def addNodeToDB(dbConnection, currentNode):
    FTPLogin = 0
    IMAPLogin = 0
    SSLCheck = 0
    if currentNode.madeFTPLogin:
        FTPLogin = 1
    if currentNode.madeIMAPLogin:
        IMAPLogin = 1
    if currentNode.madeSSLCheck:
        SSLCheck = 1
    cur = dbConnection.cursor()
    cur.execute("""INSERT INTO "knownNodes" ("nickname", "fingerprint", "published", "contact", "firstSeen", "lastSeen", "countIMAPLogins", "countFTPLogins", "countSSLChecks", "exitPolicies", "platformVersion") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", (currentNode.nickname, currentNode.fingerprint, currentNode.published, currentNode.contact, currentNode.queueTimestamp, currentNode.queueTimestamp, IMAPLogin, FTPLogin, SSLCheck, currentNode.exitPolicies, currentNode.platformVersion))
    dbConnection.commit()
    pass

# Adds a new node IP to the database of note IPs
def addNodeIPToDB(dbConnection, currentNode):
    cur = dbConnection.cursor()
    cur.execute("""INSERT INTO "knownNodeIPs" ("fingerprint", "address") VALUES (%s, %s);""", (currentNode.fingerprint, currentNode.address))
    dbConnection.commit()
    pass

# Remove a specific node from the database, after it has been processed
def removeNodeFromQueue(dbConnection, currentNode):
    cur = dbConnection.cursor()
    cur.execute("""DELETE FROM "queue" WHERE "id" = %s;""", (currentNode.nodeid,))
    dbConnection.commit()

# Checks if a node is already in the DB - if yes, it gets updated, if not, a new node is created. Same with the IPs. After that, the node is discarded from tue queue
def saveChangesToDB(dbConnection, currentNode):
    if isNodeInDB(dbConnection, currentNode):
        updateNodeInDB(dbConnection, currentNode)
        if not isNodeIPInDB(dbConnection, currentNode):
            addNodeIPToDB(dbConnection, currentNode)
    else:
        addNodeToDB(dbConnection, currentNode)
        addNodeIPToDB(dbConnection, currentNode)
    removeNodeFromQueue(dbConnection, currentNode)

# Checks if the queue of Tor nodes to process is empty
def isQueueEmpty(dbConnection):
    cur = dbConnection.cursor()
    cur.execute("""SELECT COUNT(*) FROM "queue";""")
    r = cur.fetchone()[0]
    return r == 0