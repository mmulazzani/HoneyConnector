#!/usr/bin/python

import socket
from FTPtest import FTPtest
from IMAPtest import IMAPtest
from Crypto.Cipher import AES
import base64
import binascii
import traceback
import sys

class ServerMain:

    # Crypto stuff
    
    host = ""
    port = 38742
    
    BLOCK_SIZE = 32
    PADDING = '}'
    keyHex = "f3be2f062adbdc63f4067431797b797df68c61a32e6a2d83d09ca17b18f44ece"
    
    s = socket.socket()
    
    def encrypt(self, message):
        pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        key = binascii.unhexlify(self.keyHex)
        cipher = AES.new(key)
        return EncodeAES(cipher, message)
    
    def decrypt(self, message):
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(self.PADDING)
        key = binascii.unhexlify(self.keyHex)
        cipher = AES.new(key)
        return DecodeAES(cipher, message)
    
    # ... now back to business

    def __init__(self):
        self.s = socket.socket()
        self.s.bind((self.host, self.port))
        
        self.ftpTestServer = FTPtest()
        print "starting ftp server"
        self.ftpTestServer.start()
        print "server started"
    
    def isValidFTPUserCommand(self, inputCMD):
        return inputCMD.count(" ") == 3 and inputCMD.split(" ")[1] == "FTP"
    
    def isValidFTPResetCommand(self, inputCMD):
        return inputCMD.count(" ") == 4 and inputCMD.split(" ")[1] == "FTP" and inputCMD.split(" ")[2] == "stop"
    
    def isValidIMAPUserCommand(self, inputCMD):
        return inputCMD.count(" ") == 3 and inputCMD.split(" ")[1] == "IMAP"
    
    def isValidIMAPResetCommand(self, inputCMD):
        return inputCMD.count(" ") == 4 and inputCMD.split(" ")[1] == "IMAP" and inputCMD.split(" ")[2] == "stop"
    
    def listenForCommand(self):
        self.s.listen(5)
        c, addr = self.s.accept()
        print 'Got connection from', addr
        encMessage = c.recv(4096)
        recvMessage = self.decrypt(encMessage)
    #    s.shutdown(socket.SHUT_RDWR)
        c.close()
        return recvMessage
    
    def removeFTPUser(self, username):
        self.ftpTestServer.delUser(username)
        
    
    def addFTPUsername(self, username, password):
        self.ftpTestServer.addUser(username, password)
        self.ftpTestServer.populateFiles()
        print "Populated stuff"
    
    def resetIMAP(self, username, password):
        imapAdmin = IMAPtest()
        imapAdmin.deleteUser(username)
        print "IMAP user", username, "deleted"
    
    def addIMAPUsername(self, username, password):
        print "IMAP trying to add user with " + username + " " + password
        imapAdmin = IMAPtest()
        imapAdmin.createUser(username, password)
        imapAdmin.populateMailbox(username)
        print "IMAP mailbox populated"

    def mainLoop(self):
        try:
            while True:
                try:
                    command = self.listenForCommand()
                    print command
                    if self.isValidFTPUserCommand(command):
                        username = command.split(" ")[2]
                        password = command.split(" ")[3]
                        self.addFTPUsername(username, password)
                    if self.isValidFTPResetCommand(command):
                        username = command.split(" ")[3]
                        password = command.split(" ")[4]
                        self.removeFTPUser(username)
                    if self.isValidIMAPUserCommand(command):
                        username = command.split(" ")[2]
                        password = command.split(" ")[3]
                        self.addIMAPUsername(username, password)
                    if self.isValidIMAPResetCommand(command):
                        username = command.split(" ")[3]
                        password = command.split(" ")[4]
                        self.resetIMAP(username, password)
                except Exception, e:
                    print e.message, "\n", traceback.format_exc()
        except KeyboardInterrupt:
            raise
        
server = ServerMain()
server.mainLoop()
