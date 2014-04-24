import MySQLdb
import hashlib
import random
import os
import shutil
from mailbox import Maildir
from mailbox import MaildirMessage

class IMAPtest():
    
    domain = "hypermailer.net"

    def createUser(self, username, password):
        database = MySQLdb.connect(host="localhost",user="mailuser",db="mailserver",passwd="GsWkLfvlyhgh7KRosdcffHcIS")
        passwordMD5 = hashlib.md5(password).hexdigest()
        usernameDOM = username + "@" + self.domain
        cursor = database.cursor()
        cursor.execute("INSERT INTO virtual_users (domain_id, password, email) VALUES (%s, %s, %s)", (1, passwordMD5, usernameDOM))
        database.commit()
        database.close()
        
    def deleteUser(self, username):
        database = MySQLdb.connect(host="localhost",user="mailuser",db="mailserver",passwd="GsWkLfvlyhgh7KRosdcffHcIS")
        usernameDOM = username + "@" + self.domain
        cursor = database.cursor()
        cursor.execute("DELETE FROM virtual_users WHERE email = %s", usernameDOM)
        database.commit()
        database.close()
        shutil.rmtree("/var/vmail/" + self.domain + "/" + username, ignore_errors = True)
        
    def chmodMailbox(self, path):
        os.chmod(path, 0o777)
        for root, dirs, files in os.walk(path):  
            for d in dirs:  
                os.chmod(os.path.join(root, d), 0o777)
            for f in files:
                os.chmod(os.path.join(root, f), 0o777)
        
    def populateMailbox(self, username):
        pathShort = "/var/vmail/" + self.domain + "/" + username
        pathLong = pathShort + "/Maildir"
        os.mkdir(pathShort)
        mailbox = Maildir(pathLong)
        numOfMails = random.randint(1, 6666)
        percentageRead = random.randint(0, 100)
        for i in xrange(1, numOfMails):
            message = MaildirMessage(message=str(i))
            message.set_subdir("cur")
            readSeed = random.randint(0, 100)
            if percentageRead <= readSeed:
                message.set_flags("S")
            mailbox.add(message)
        self.chmodMailbox(pathShort)
        
        