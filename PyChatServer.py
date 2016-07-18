#PyChat LAN server 1.0
import socket
import thread
import sys
import signal
import time
import os.path
import json

CONFIG = "./serv_conf.txt";

class MessageQueue:
    def __init__(self,logfile):
        self.logfile = logfile;
        self.clientList = [];
        self.elapsed = 0;
    def addClient(self,client):
        client.conn.setblocking(0);
        self.clientList.append(client);
    def sendAndRec(self):
        while True:
            messageList = [];
            if self.clientList:
                for client in self.clientList:
                    try:
                        msg = client.conn.recv(optdict['msg_length']);
                        if msg[:1]=='/':
                            self.handleCommand(msg.rstrip(),client);
                        else:
                            msg = client.name + ": " + msg.rstrip() + "\n"; #Ensure 1 newline after all messages
                            self.log(msg.rstrip());
                            messageList.append(msg);
                    except socket.error:
                        pass;
                for client in self.clientList:
                    for msg in messageList:
                        try:
                            client.conn.sendall(msg);
                        except socket.error:
                            client.conn.close();
                            self.clientList.remove(client);
                            self.log("Removing client " + client.name);
                time.sleep(optdict['sleep_time']);
                self.elapsed+=optdict['sleep_time'];
    def nameAlreadyExists(self,name):
        if self.clientList:
            for client in self.clientList:
                if client.name == name:
                    return True;
        return False;
    def globalMsg(self, msg):
        self.log(msg.rstrip());
        for client in self.clientList:
            client.conn.sendall(msg);
    def handleCommand(self,msg,client):
        self.log("Command entered by " + client.name);
        if msg == "/exit":
            client.conn.close();
            self.clientList.remove(client);
            self.globalMsg("User " + client.name + " has left the channel.\n");
        elif msg == "/help":
            client.conn.sendall("::All commands are prefaced by /\n::Type /help for this text\n::/exit to leave\n");
        else:
            client.conn.sendall("::Uncrecognized command. Type /help for assistace\n");
    def log(self,msg):
        currtime = self.elapsed;
        timestamp= [currtime/3600];
        currtime %= 3600;
        timestamp.append(currtime/60);
        currtime %= 60;
        timestamp.append(currtime);
        msg = str(timestamp) + " " + msg.rstrip() + "\n";
        self.logfile.write(msg);
        print msg.rstrip();

class Client:
    """Hold the name and network connection for a single client
    """
    def __init__(self, name, conn):
        self.name = name.rstrip();
        self.conn = conn;

def newClient(conn,msgQ):
    conn.sendall("Enter your name: ");
    name = conn.recv(optdict['nm_length']);
    while(msgQ.nameAlreadyExists(name)):
        conn.sendall("Error (Name already exists). Please enter a new name: ");
        name = conn.recv(optdict['nm_length']);
    conn.sendall("Welcome to PyChat v1.3, type /help for commands and /exit to exit\n");
    msgQ.globalMsg("User " + name.rstrip() + " has joined the channel\n");
    msgQ.addClient(Client(name,conn));

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
        thread.start_new_thread(newClient,(client,msgQ));


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
        'logfile' : './serv_log.txt',
        }
    default = open(CONFIG,'w');
    default.write(json.dumps(optdict));
    default.close();
    print "Default config written to " + CONFIG;

msgQ = MessageQueue(open(optdict['logfile'],'a'));
thread.start_new_thread(msgQ.sendAndRec,());
s = socket.socket();
s.bind((socket.gethostname() if optdict['hostname'] == "DEFAULT" else optdict['hostname'],optdict['port']));
signal.signal(signal.SIGINT, signal_handler);
acceptClients(s,msgQ);
