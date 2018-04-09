import socket                                         
import pickle
from struct import unpack, pack
import threading
import time
import sys
from update import output 
from mp_essential import incoming_commands, outgoing_commands
from mp_essential import incoming_lock, outgoing_lock

from networking import generic_send_loop, generic_listen_loop
class Client:
    def __init__(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.serversocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.host =  "192.168.1.23"                    
        self.port = 9999       
        self.connected = False

    def listen(self):
        threading.Thread(target = self.listen_loop, args = []).start()

    def send(self):
        threading.Thread(target = self.send_loop, args = []).start()
        
    def send_loop(self):
        self.serversocket.connect((self.host, self.port))    
        self.connected = True
        
        while True:
            output("locks", "acquiring outgoing lock")

            with outgoing_lock:
                for data in outgoing_commands:
                    generic_send_loop(data, self.serversocket)
                    outgoing_commands.remove(data)
                    
            output("locks", "releasing outgoing lock")
            # time.sleep(1)

    def listen_loop(self):
        global incoming_commands
        serversocket = self.serversocket
        
        size = None 
        data = b''
        while True:
            if self.connected:
                incoming_commands, data, size = generic_listen_loop(serversocket, incoming_commands, data, size)
            # time.sleep(1)
