import socket
import threading

import ts4mp
from ts4mp.debug.log import ts4mp_log
from ts4mp.core.mp_essential import outgoing_lock, outgoing_commands

from ts4mp.core.networking import generic_send_loop, generic_listen_loop


class Server:
    def __init__(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.host = ""
        self.port = 9999
        self.alive = True
        self.serversocket.bind((self.host, self.port))
        self.clientsocket = None

    def listen(self):
        threading.Thread(target=self.listen_loop, args=[]).start()

    def send(self):
        threading.Thread(target=self.send_loop, args=[]).start()

    def send_loop(self):
        while self.alive:
            if self.clientsocket is not None:
                ts4mp_log("locks", "acquiring outgoing lock")

                with outgoing_lock:
                    for data in outgoing_commands:
                        generic_send_loop(data, self.clientsocket)
                        outgoing_commands.remove(data)

                ts4mp_log("locks", "releasing outgoing lock")

            # time.sleep(1)

    def listen_loop(self):
        self.serversocket.listen(5)
        self.clientsocket, address = self.serversocket.accept()

        ts4mp_log("network", "Client Connect")

        clientsocket = self.clientsocket
        size = None
        data = b''

        while self.alive:
            # output_irregardelessly("network", "Server Listen Update")
            ts4mp.core.mp_essential.incoming_commands, data, size = generic_listen_loop(clientsocket, ts4mp.core.mp_essential.incoming_commands, data, size)
            # time.sleep(1)

    def kill(self):
        self.alive = False

