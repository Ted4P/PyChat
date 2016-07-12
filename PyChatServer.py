#PyChat LAN server 1.0
import socket
import thread
import sys
import signal
import time
import os.path
import json

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
                            self.log("Removing client " + client.name + "\n");
                time.sleep(optdict['sleep_time']);
                self.elapsed+=optdict['sleep_time'];
    def nameAlreadyExists(self,name):
        if self.clientList:
            for client in self.clientList:
                if client.name == name:
                    return True;
        return False;
    def globalMsg(self, msg):
        self.log(msg);
        for client in self.clientList:
            client.conn.sendall(msg);
    def log(self,msg):
        currtime = self.elapsed;
        timestamp= [currtime/3600];
        currtime %= 3600;
        timestamp.append(currtime/60);
        currtime %= 60;
        timestamp.append(currtime);
        msg = str(timestamp) + " " + msg + "\n";
        self.logfile.write(msg);
        print msg.rstrip();

class Client:
    def __init__(self, name, conn):
        self.name = name.rstrip();
        self.conn = conn;

def newClient(conn,msgQ):
    conn.sendall("Enter your name: ");
    name = conn.recv(optdict['nm_length']);
    while(msgQ.nameAlreadyExists(name)):
        conn.sendall("Error (Name already exists). Please enter a new name: ");
        name = conn.recv(optdict['nm_length']);
    msgQ.globalMsg("User " + name.rstrip() + " has joined the channel\n");
    msgQ.addClient(Client(name,conn));

def signal_handler(signal, frame):      #Handle graceful exit on ctrl-c
    global s;
    global msgQ;
    s.close();
    msgQ.logfile.close();
    sys.exit(0);

def acceptClients(s, msgQ):
    s.listen(optdict['max_clients']);
    while True:         #Wait for new connections, spin out new thread w/ sock, hand thread ref to msgQ
        client,addr = s.accept();
        msgQ.log("Accepting new client...");
        thread.start_new_thread(newClient,(client,msgQ));


if os.path.isfile("./serv_conf.txt"):
    print "Found config file, reading prefrences from ./serv_conf.txt";
    conf = open("./serv_conf.txt", 'r');
    optdict = json.loads(conf.read());
    conf.close();
else:
    print "No config file found, generating and writing default file";
    optdict = {
        'sleep_time' : 1,
        'msg_length' : 128,
        'nm_length' : 16,
        'hostname' : '127.0.0.1',
        'port' : 90,
        'max_clients' : 50,
        'logfile' : './serv_log.txt',
        }
    default = open("./serv_conf.txt",'w');
    default.write(json.dumps(optdict));
    default.close();

msgQ = MessageQueue(open(optdict['logfile'],'a'));
thread.start_new_thread(msgQ.sendAndRec,());
s = socket.socket();
s.bind((optdict['hostname'],optdict['port']));
signal.signal(signal.SIGINT, signal_handler);
acceptClients(s,msgQ);
