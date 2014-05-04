import MySQLdb
import hashlib
import random
import os
import shutil
from mailbox import Maildir
from mailbox import MaildirMessage

# class of the IMAP server module for HoneyConnector
class IMAPtest():
    
    # The domain your IMAP server uses
    domain = "hypermailer.net"

    # Creates a new user in the MySQL database of Dovecot
    # You will have to change the database connection data
    def createUser(self, username, password):
        database = MySQLdb.connect(host="localhost",user="mailuser",db="mailserver",passwd="GsWkLfvlyhgh7KRosdcffHcIS")
        passwordMD5 = hashlib.md5(password).hexdigest()
        usernameDOM = username + "@" + self.domain
        cursor = database.cursor()
        cursor.execute("INSERT INTO virtual_users (domain_id, password, email) VALUES (%s, %s, %s)", (1, passwordMD5, usernameDOM))
        database.commit()
        database.close()

    # Deletes a specific user from the MySQL database of Dovecot
    # You will have to change the database connection data        
    def deleteUser(self, username):
        database = MySQLdb.connect(host="localhost",user="mailuser",db="mailserver",passwd="GsWkLfvlyhgh7KRosdcffHcIS")
        usernameDOM = username + "@" + self.domain
        cursor = database.cursor()
        cursor.execute("DELETE FROM virtual_users WHERE email = %s", usernameDOM)
        database.commit()
        database.close()
        shutil.rmtree("/var/vmail/" + self.domain + "/" + username, ignore_errors = True)
    
    # Chmods the Mailbox, so dovecot can access the e-mails    
    def chmodMailbox(self, path):
        os.chmod(path, 0o777)
        for root, dirs, files in os.walk(path):  
            for d in dirs:  
                os.chmod(os.path.join(root, d), 0o777)
            for f in files:
                os.chmod(os.path.join(root, f), 0o777)
    
    # Populates the mailbox with 1 to 6666 e-mails, containing in essential nothing. All e-mails are marked as known to the clients, i.e. not new
    def populateMailbox(self, username):
        # Here will the mail directory of the user be stored
        pathShort = "/var/vmail/" + self.domain + "/" + username
        pathLong = pathShort + "/Maildir"
        # Create those directories
        os.mkdir(pathShort)
        mailbox = Maildir(pathLong)
        # And now populate that directory
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
        
        