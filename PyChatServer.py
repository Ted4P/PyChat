#PyChat LAN server 2.0
import socket
import thread
import sys
import signal
import os.path
import json
from MessageQueue import MessageQueue

CONFIG = "serv_conf.txt";

class Client:
    """Hold the name and network connection for a single client
    """
    def __init__(self, name, conn, addr):
        self.name = name.rstrip();
        self.conn = conn;
        self.addr = addr;

def newClient(conn,msgQ,addr):
    conn.sendall("Enter your name: ");
    name = conn.recv(optdict['nm_length']);
    while(msgQ.nameAlreadyExists(name)):
        conn.sendall("Error (Name already exists). Please enter a new name: ");
        name = conn.recv(optdict['nm_length']);
    conn.sendall("Welcome to PyChat v1.3, type /help for commands and /exit to exit\n");
    msgQ.globalMsg("User " + name.rstrip() + " has joined the channel\n");
    msgQ.addClient(Client(name,conn,addr));

def signal_handler(signal, frame):      #Handle graceful exit on ctrl-c 
    msgQ.log("Ctrl-c detected, server shutting down");
    msgQ.globalMsg("Server shutting down!\n");
    for client in msgQ.clientList:
        client.conn.close();
    s.close();
    msgQ.logfile.close();
    sys.exit(0);

def acceptClients(s, msgQ):
    s.listen(optdict['max_clients']);
    while True:         #Wait for new connections, spin out new thread w/ sock, hand thread ref to msgQ
        client,addr = s.accept();
        msgQ.log("Accepting new client...");
        thread.start_new_thread(newClient,(client,msgQ,addr));

def adminLoop(msgQ):
    print "For admin commands, type \"help\"";
    while True:
        cmd = raw_input("::");
        msgQ.log("Admin command: " + cmd);
        if cmd == "help":
            print "Configure the server at " + CONFIG + ". Commands:"
            print "kick [name] to remove [name] from the channel";
            print "shutdown to stop the server";
            print "list to list currently connected users";
        if cmd[:4] == "kick" and len(cmd)>5:
            msgQ.kickPerson(cmd[5:]);
        if cmd == "list":
            if msgQ.clientList:
                for client in msgQ.clientList:
                    print "> " + client.name + "@" + str(client.addr);
        if cmd == "shutdown":
            signal_handler(None,None);


if os.path.isfile(CONFIG):
    print "Found config file, reading prefrences from " + CONFIG;
    conf = open(CONFIG, 'r');
    optdict = json.loads(conf.read());
    conf.close();
else:
    print "No config file found, generating and writing default file";
    optdict = {
        'sleep_time' : 1,
        'msg_length' : 128,
        'nm_length' : 16,
        'hostname' : 'DEFAULT',
        'port' : 90,
        'max_clients' : 50,
        'logfile' : 'serv_log.txt',
        }
    default = open(CONFIG,'w');
    default.write(json.dumps(optdict));
    default.close();
    print "Default config written to " + CONFIG;

msgQ = MessageQueue(open(optdict['logfile'],'a'),optdict);
thread.start_new_thread(msgQ.sendAndRec,());        #Iterate through connected clients and send and recieve data in thread
s = socket.socket();
s.bind((socket.gethostname() if optdict['hostname'] == "DEFAULT" else optdict['hostname'],optdict['port']));
signal.signal(signal.SIGINT, signal_handler);
thread.start_new_thread(acceptClients,(s,msgQ,));           #Wait for incoming connections on specified port and add connections to messageQueue when initialized
adminLoop(msgQ);
