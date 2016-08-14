import socket
import time

#List of users with associated names, with method to automatically synchronize messages between all users every X seconds.
#Also supports global messages, adding and removing users, and logging
class MessageQueue:
    def __init__(self,logfile,optdict):
        self.optdict = optdict;
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
                        msg = client.conn.recv(self.optdict['msg_length']);
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
                time.sleep(self.optdict['sleep_time']);
                self.elapsed+=self.optdict['sleep_time'];
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
    def kickPerson(self,name):
        if not self.nameAlreadyExists(name):
            self.log("Error: cannot kick " + name + ", name not found");
        if self.clientList:
            for client in self.clientList:
                if client.name == name:
                     client.conn.sendall("You have been kicked by the admin!\n");
                     client.conn.close();
                     self.clientList.remove(client);
                     self.globalMsg("User " + name + " has been kicked by the admin\n");
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
