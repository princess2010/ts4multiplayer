import socket
import threading

import ts4mp
from ts4mp.debug.log import ts4mp_log
from ts4mp.core.mp_essential import outgoing_lock, outgoing_commands
from ts4mp.core.networking import generic_send_loop, generic_listen_loop
from ts4mp.configs.server_config import HOST, PORT


class Client:
    def __init__(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.host = HOST
        self.port = PORT
        self.alive = True
        # self.host = "192.168.1.23"
        # self.port = 9999
        self.connected = False

    def listen(self):
        threading.Thread(target=self.listen_loop, args=[]).start()

    def send(self):
        threading.Thread(target=self.send_loop, args=[]).start()

    def send_loop(self):
        self.serversocket.connect((self.host, self.port))
        self.connected = True

        while self.alive:
            ts4mp_log("locks", "acquiring outgoing lock")

            with outgoing_lock:
                for data in outgoing_commands:
                    generic_send_loop(data, self.serversocket)
                    outgoing_commands.remove(data)

            ts4mp_log("locks", "releasing outgoing lock")
            # time.sleep(1)

    def listen_loop(self):

        serversocket = self.serversocket
        size = None
        data = b''

        while self.alive:
            if self.connected:
                # TODO: Is this supposed to override the global variable? It's really unclear
                ts4mp.core.mp_essential.incoming_commands, data, size = generic_listen_loop(serversocket, ts4mp.core.mp_essential.incoming_commands, data, size)

            # time.sleep(1)

    def kill(self):
        self.alive = False
