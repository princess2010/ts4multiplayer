import socket
import threading

import ts4mp
from ts4mp.debug.log import ts4mp_log
from ts4mp.core.mp_essential import outgoing_lock, outgoing_commands
from ts4mp.core.mp_essential import incoming_lock
from ts4mp.core.networking import generic_send_loop, generic_listen_loop, socket_lock

class Server:
    def __init__(self):
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serversocket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.host = ""
        self.port = 9999
        self.alive = True
        self.serversocket.bind((self.host, self.port))
        with socket_lock:
            self.clientsocket = None

    def listen(self):
        threading.Thread(target=self.listen_loop, args=[]).start()

    def send(self):
        threading.Thread(target=self.send_loop, args=[]).start()

    def send_loop(self):
        while self.alive:
            with socket_lock:
                if self.clientsocket is not None:
                    try:
                        ts4mp_log("locks", "acquiring outgoing lock for send")

                        with outgoing_lock:
                            for data in outgoing_commands:
                                generic_send_loop(data, self.clientsocket)
                                outgoing_commands.remove(data)

                        ts4mp_log("locks", "releasing outgoing lock for send")
                    except OSError as e:
                        with outgoing_lock:
                            with incoming_lock:
                                self.__init__()
                        ts4mp_log("network", "Network disconnect")

            # time.sleep(1)

    def listen_loop(self):
        while self.alive:


            ts4mp_log("network", "Listening for clients")

            self.serversocket.listen(5)

            clientsocket, address = self.serversocket.accept()

            ts4mp_log("network", "Client Connect")

            with socket_lock:
                self.clientsocket = clientsocket

            size = None
            data = b''

            while self.alive:
                try:
                    new_command, data, size = generic_listen_loop(clientsocket, data, size)
                    if new_command is not None:
                        ts4mp_log("locks", "acquiring incoming lock")

                        with incoming_lock:
                            ts4mp.core.mp_essential.incoming_commands.append(new_command)
                        ts4mp_log("locks", "releasing incoming lock")

                except OSError as e:
                    with outgoing_lock:
                        with incoming_lock:
                            self.__init__()
                    ts4mp_log("network", "Network disconnect")

                    break
    def kill(self):
        self.alive = False

