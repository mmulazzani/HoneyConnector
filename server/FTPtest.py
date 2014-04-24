#!/usr/bin/env python
import os
import threading
import random
import shutil
import time

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer

class FTPtest(threading.Thread):
    
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
    
        # Instantiate FTP server class and listen on 0.0.0.0:2121
        self.address = ('', 2121)
        self.server = FTPServer(self.address, self.handler)
    
        # set a limit for connections
        self.server.max_cons = 256
        self.server.max_cons_per_ip = 5
        
    def addUser(self, username, password):
        # Define a new user having full r/w permissions and a read-only
        # anonymous user
        directory = os.getcwd()+"/testdata"
        print "adding user " + username + " and pw " + password
        self.authorizer.add_user(username, password, directory, perm="elradfmw")
    
    def delUser(self, username):
        self.authorizer.remove_user(username)
        print "deletd user", username
        
    def getRandomDirs(self):
        htdocDirs = ["htdocs", "www", "www-data", "htdoc", "web"]
        htdocDir = random.choice(htdocDirs)
        dirs = ["isos", "wareZ", "pron", "files", "logs", "conficential", "misc", "funny", "photos", "gf", "share", "saves"]
        dirs.append(htdocDir)
        numOfPossibleDirs = len(dirs)
        numOfDirs = random.randrange(0, numOfPossibleDirs)
        return random.sample(set(dirs), numOfDirs)
    
    def getRandomTimestamp(self):
        endTimestamp = time.time()
        startTimestamp = 1353073006.547738
        return startTimestamp + random.random() * (endTimestamp - startTimestamp)
        
    def populateFiles(self):    
        # populate ftp server
        source = os.getcwd()+"/possibledata/"
        destination = os.getcwd()+"/testdata/"
        currentUser = os.getuid()
        currentGroup = os.getegid()
        
        shutil.rmtree(destination, ignore_errors = True)
        os.mkdir(destination)
        
        filesToCleanUp = os.listdir(destination)
        for fileToRemove in filesToCleanUp:
            os.remove(destination + fileToRemove)
        
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
        
        dirsToCreate = self.getRandomDirs()
        for dirToCreate in dirsToCreate:
            dstPath = destination + dirToCreate
            os.mkdir(dstPath)
            dirTimestamp = self.getRandomTimestamp()
            os.utime(dstPath, (dirTimestamp, dirTimestamp))
                
    def run(self):
        # start ftp server
        self.server.serve_forever()
        
    def stop(self):
        #stop ftp server
        self.server.close_all()
