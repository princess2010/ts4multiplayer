import socket                                         
import pickle
from struct import unpack, pack
import threading
import time
import sys
from networking import generic_send_loop, generic_listen_loop
import update
class Server:
    def __init__(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.host = socket.gethostname()                           
        self.port = 9999                                           
        self.serversocket.bind((self.host, self.port))     
        self.clientsocket = None

    def listen(self, incoming_commands):
        threading.Thread(target = self.listen_loop, args = [incoming_commands]).start()

    def send(self, outgoing_commands):
        threading.Thread(target = self.send_loop, args = [outgoing_commands]).start()
        
    def send_loop(self, outgoing_commands):
        while True:
            if self.clientsocket is not None:
                for data in outgoing_commands:
                    generic_send_loop(data, self.clientsocket)
                    outgoing_commands.remove(data)
                    time.sleep(0.1)



    def listen_loop(self, incoming_commands):
        self.serversocket.listen(5)
        self.clientsocket,address = self.serversocket.accept()  
        clientsocket = self.clientsocket
        
        size = None 
        data = b''
        
        while True:
            incoming_commands, data, size = generic_listen_loop(clientsocket, incoming_commands, data, size)
            
