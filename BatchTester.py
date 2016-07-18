import thread
import time
import socket

SERVER_ADDR = "127.0.0.1";
SERVER_PORT = 90;

def testClient(num):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    s.connect((SERVER_ADDR,SERVER_PORT));
    s.recv(128);
    s.send("Client " + str(num));
    time.sleep(5);
    s.setblocking(0);
    while True:
        print "CLIENT # " + str(num) + ": " + s.recv(2048);
        s.send("SOME CRAP FROM CLIENT NUMBER " + str(num));
        time.sleep(3);

for i in range(35):
        thread.start_new_thread(testClient,(i,));
while True:
    time.sleep(30);     #I apoligize for this gross hack
