import socket                                         
import pickle
from struct import unpack, pack
import threading
import time
import sys

from networking import generic_send_loop, generic_listen_loop
class Client:
    def __init__(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.host = socket.gethostname()                           
        self.port = 9999       
        self.connected = False

    def listen(self, incoming_commands):
        threading.Thread(target = self.listen_loop, args = [incoming_commands]).start()

    def send(self, outgoing_commands):
        threading.Thread(target = self.send_loop, args = [outgoing_commands]).start()
        
    def send_loop(self, outgoing_commands):
        self.serversocket.connect((self.host, self.port))    
        self.connected = True
    
        while True:
            for data in outgoing_commands:
                generic_send_loop(data, self.serversocket)
                outgoing_commands.remove(data)
                time.sleep(0.1)
            # time.sleep(0.1)
    def listen_loop(self, incoming_commands):
        serversocket = self.serversocket
        
        size = None 
        data = b''
        while True:
            if self.connected:
                incoming_commands, data, size = generic_listen_loop(serversocket, incoming_commands, data, size)

if __name__ == "__main__":   
    incoming_commands = []
    outgoing_commands = []
    client_instance = Client()
    client_instance.listen(incoming_commands)
    client_instance.send(outgoing_commands)

    count = 0
    while True:
        print(incoming_commands)
        incoming_commands = []
        outgoing_commands.append("Data from client: {}".format(count))
        count += 1
        time.sleep(1)