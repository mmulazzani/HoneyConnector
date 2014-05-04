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

    # listen on every ip address for incoming control messages
    host = ""
    # the control port for HoneyConnector control messages
    port = 38742
    
    s = socket.socket()
    
    # ----- CRYPTOGRAPHIC STUFF -----
    # Crypto stuff - this is for encrypting the connection between the client and the server modules
    # This is probably a bad implementation and it should be changed in the future
    BLOCK_SIZE = 32
    PADDING = '}'
    # IMPORTANT: Change this, before deploying in every module
    keyHex = "f3be2f062adbdc63f4067431797b797df68c61a32e6a2d83d09ca17b18f44ece"
    

    # Encrypt a message
    def encrypt(self, message):
        pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING
        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
        key = binascii.unhexlify(self.keyHex)
        cipher = AES.new(key)
        return EncodeAES(cipher, message)
    
    # Decrypt a message
    def decrypt(self, message):
        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(self.PADDING)
        key = binascii.unhexlify(self.keyHex)
        cipher = AES.new(key)
        return DecodeAES(cipher, message)
    
    # ... now back to normal business
    # Start listening on the control port and start the FTP server without any users
    def __init__(self):
        self.s = socket.socket()
        self.s.bind((self.host, self.port))
        
        self.ftpTestServer = FTPtest()
        print "starting ftp server"
        self.ftpTestServer.start()
        print "server started"
    
    # Checks if the command is a valid command to create a new FTP user
    def isValidFTPUserCommand(self, inputCMD):
        return inputCMD.count(" ") == 3 and inputCMD.split(" ")[1] == "FTP"

    # Checks if the command is a valid command to delete the FTP users    
    def isValidFTPResetCommand(self, inputCMD):
        return inputCMD.count(" ") == 4 and inputCMD.split(" ")[1] == "FTP" and inputCMD.split(" ")[2] == "stop"
    
        # Checks if the command is a valid command to create a new IMAP user
    def isValidIMAPUserCommand(self, inputCMD):
        return inputCMD.count(" ") == 3 and inputCMD.split(" ")[1] == "IMAP"
    
        # Checks if the command is a valid command to delete an IMAP user
    def isValidIMAPResetCommand(self, inputCMD):
        return inputCMD.count(" ") == 4 and inputCMD.split(" ")[1] == "IMAP" and inputCMD.split(" ")[2] == "stop"
    
    # Listens for any incomming connection on the control port, decrypts it and returns the message
    def listenForCommand(self):
        self.s.listen(5)
        c, addr = self.s.accept()
        print 'Got connection from', addr
        encMessage = c.recv(4096)
        recvMessage = self.decrypt(encMessage)
    #    s.shutdown(socket.SHUT_RDWR)
        c.close()
        return recvMessage
    
    # Removes a user from the FTP server
    def removeFTPUser(self, username):
        self.ftpTestServer.delUser(username)
        
    # Adds a user to the FTP server
    def addFTPUsername(self, username, password):
        self.ftpTestServer.addUser(username, password)
        self.ftpTestServer.populateFiles()
        print "Populated stuff"
    
    # Removes a user from the IMAP server
    def resetIMAP(self, username, password):
        imapAdmin = IMAPtest()
        imapAdmin.deleteUser(username)
        print "IMAP user", username, "deleted"
    
    # Adds a user to the IMAP server
    def addIMAPUsername(self, username, password):
        print "IMAP trying to add user with " + username + " " + password
        imapAdmin = IMAPtest()
        imapAdmin.createUser(username, password)
        imapAdmin.populateMailbox(username)
        print "IMAP mailbox populated"

    # And now the main function: Loop through listening for commands, match them if they are understood and do stuff if it fits
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
