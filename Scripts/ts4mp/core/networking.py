import pickle
import sys
from struct import unpack, pack

from ts4mp.debug.log import ts4mp_log

import struct

def generic_send_loop(data, socket):
    data = pickle.dumps(data)
    length = pack('>Q', sys.getsizeof(data))
    ts4mp_log("network", "Attempting to send a message")

    socket.sendall(length)
    socket.sendall(data)
    ts4mp_log("network", "Sent a message with length of {} bytes".format(length))

def generic_listen_loop(socket, data, size):
    new_command = None
    # ts4mp_log_debug("receive", "{}, {} \n".format(size, sys.getsizeof(data)))
    if size is None:
        size = socket.recv(8)
        try:
            (size,) = unpack('>Q', size)
            size = int(size)
        except struct.error:
            # not enough bytes received
            size = None
            data = b''
            ts4mp_log("network", "Not enough bytes received")
            raise OSError()
    elif size > sys.getsizeof(data):
        bytes_to_receive = size - sys.getsizeof(data)
        new_data = socket.recv(bytes_to_receive)
        data += new_data
    elif size == sys.getsizeof(data):
        data = pickle.loads(data)


        new_command = data


        size = None
        data = b''

    return new_command, data, size
