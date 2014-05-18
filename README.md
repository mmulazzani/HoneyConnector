HoneyConnector
==============

HoneyConnector is a Python 2.7 script to detect sniffing Tor exit relays by using bait connections and checking for reconnects with unique login credentials.

What is it exactly?
--------

HoneyConnector conducts bait connections in plaintext protocols, currently FTP and IMAP, with unique credentials. If another connection with these credentials takes place, the exit relay the initial connection took place through can be considered for a closer inspection. It can be divided in four parts: client, IMAP server, FTP server and the underlying database backend.

The **database backend** is a PostgreSQL database, where the queue of nodes, all known nodes, used credentials and credentials in login attempts are stored.

The **client module** generates new credentials and transmits them to the corresponding server modules. When an account is created on a server, the client simulates a session (Thunderbird checking for new mails, FileZilla downloading a random file), closes the connection and initiates a deletion of the account on the server, since we don't want anyone to really log in there. Additionally, it fetches SSL certificates directly and through Tor and compares them.

The **FTP module** is powered by pyFTPd, whose status messages were adapted to imitate vsFTPd and which logs login attempts directly into the PostgreSQL database. It listens for control messages from the HoneyConnector client to create new users. After the creation of users, a random set of data from a directory is chosen and copied to the directory of the FTP server.

The **IMAP module** uses the Dovecot MTA with MySQL for the user backend. The HoneyConnector IMAP server module adds and deletes users in the MySQL database and creates a random amount of nonsensical e-mails in the user's mailbox (these messages are currently never transferred to the client). Dovecot loggs login attempts to its log file, so an extra part of the IMAP server parses this log file and transfers new login attempts into the common PostgreSQL database.

This all can be deployed on just one machine, or one machine each for every task. With some adaptions, you can add more servers for one protocol and become an overlord of the Tor anti-sniffing task force - it's all up to you. And please, report your findings to the Tor mailing list.

What has to be done
--------

This script was created for measurements used in a master's thesis and a correlating paper, being used over the course of about four months. For this, it was sufficient, but I think this project still needs some more work in the following sections:

*   Because I was new to Python when I started this: Core refractoring...
*   ... and proper exception handling...
*   ... and performance tuning, a lot of performance tuning
*   Creating an easier install routine
*   Collecting the config in a central place
*   Securing the connection between the server and the client modules properly
*   Currently it needs a restart about every 24 hours because of an error with too many open files - I couldn't track down, if this was a problem with psycopg2 or stem
*   Maybe check, if it already runs on Python 3.x, and adapt problems

Otherwise, have fun tracking down those Tor sniffers, and thank you for contributing if you fix any bugs or add new features!

- Richard
