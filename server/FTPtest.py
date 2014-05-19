#!/usr/bin/env python
import os
import threading
import random
import shutil
import time

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer

# This is the HoneyConnector FTP server module
# Much of this is based upon a tutorial how to use pyFTPd
class FTPtest(threading.Thread):
    
    # Start the FTP server in a thread with a dummy authorizer, where we can later on feed users to
    def __init__(self):
        threading.Thread.__init__(self)
        # Instantiate a dummy authorizer for managing 'virtual' users
        self.authorizer = DummyAuthorizer()
    
        # Instantiate FTP handler class
        self.handler = FTPHandler
        self.handler.authorizer = self.authorizer
   
        # Specify a masquerade address and the range of ports to use for
        # passive connections.  Decomment in case you're behind a NAT.
        #handler.masquerade_address = '151.25.42.11'
        #handler.passive_ports = range(60000, 65535)
    
        # Instantiate FTP server class and listen on every IP address of the machine on port 2121
        # If you use this port, please use the iptables command provided in the installation documentation
        # If you configured your system so users can listen on ports below 1024, you can set this to 21 and fotget the command
        self.address = ('', 2121)
        self.server = FTPServer(self.address, self.handler)
    
        # set a limit for connections
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5
        
    # Define a new user having full r/w permissions and a read-only
    def addUser(self, username, password):
        directory = os.getcwd()+"/testdata"
        print "adding user " + username + " and pw " + password
        self.authorizer.add_user(username, password, directory, perm="elradfmw")
    
    # Removes an user from the server
    def delUser(self, username):
        self.authorizer.remove_user(username)
        print "deletd user", username
        
    # Get some random directories to create within the server
    def getRandomDirs(self):
        htdocDirs = ["htdocs", "www", "www-data", "htdoc", "web"]
        htdocDir = random.choice(htdocDirs)
        dirs = ["isos", "wareZ", "pron", "files", "logs", "conficential", "misc", "funny", "photos", "gf", "share", "saves"]
        dirs.append(htdocDir)
        numOfPossibleDirs = len(dirs)
        numOfDirs = random.randrange(0, numOfPossibleDirs)
        return random.sample(set(dirs), numOfDirs)
    
    # Get some random timestamps between the set start timestamp and now, so the timestamps on the server aren't weird
    def getRandomTimestamp(self):
        endTimestamp = time.time()
        startTimestamp = 1353073006.547738
        return startTimestamp + random.random() * (endTimestamp - startTimestamp)
        
    # Copy a random subset of data from the possibledata directory to the FTP server directory - then create some random directorys
    def populateFiles(self):    
        # The path to the bait and safe data
        source = os.getcwd()+"/possibledata/"
        # The path to the FTP server directory
        destination = os.getcwd()+"/testdata/"
        # The uid and gid of the current user
        currentUser = os.getuid()
        currentGroup = os.getegid()
        
        # Whipe the whole directory the server had before and create a new one
        shutil.rmtree(destination, ignore_errors = True)
        os.mkdir(destination)
        
        filesToCleanUp = os.listdir(destination)
        for fileToRemove in filesToCleanUp:
            os.remove(destination + fileToRemove)
        
        # Get the random subset of files from the bait and safe data and copy them into the FTP directory
        allPossibleFiles = os.listdir(source)
        print allPossibleFiles
        numOfPossibleFiles = len(allPossibleFiles)
        numOfFilesToCopy = random.randrange(1, numOfPossibleFiles)
        
        filesToCopy = random.sample(set(allPossibleFiles), numOfFilesToCopy)
        
        for fileToCopy in filesToCopy:
            dstFile = destination + fileToCopy
            shutil.copy2(source + fileToCopy, dstFile)
            os.chown(dstFile, currentUser, currentGroup)
            fileTimestamp = self.getRandomTimestamp()
            os.utime(dstFile, (fileTimestamp, fileTimestamp))
        
        # Create the random directories
        dirsToCreate = self.getRandomDirs()
        for dirToCreate in dirsToCreate:
            dstPath = destination + dirToCreate
            os.mkdir(dstPath)
            dirTimestamp = self.getRandomTimestamp()
            os.utime(dstPath, (dirTimestamp, dirTimestamp))
                
    # start the FTP server
    def run(self):
        self.server.serve_forever()

    # stop the FTP server     
    def stop(self):
        self.server.close_all()
