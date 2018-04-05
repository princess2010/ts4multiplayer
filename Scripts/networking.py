import sys
import pickle
from struct import unpack, pack
from mp_essential import Message
from update import output
def generic_send_loop(data, socket):
    data  = pickle.dumps(data)
    length = pack('>Q', sys.getsizeof(data))
    socket.sendall(length)
    socket.sendall(data)

    
def generic_listen_loop(socket, recieved_commands, data, size):
    # output("receive", "{}, {} \n".format(size, sys.getsizeof(data)))
    if size == None:
        size = socket.recv(8)
        (size,) = unpack('>Q', size)

        size = int(size)
    
    elif size > sys.getsizeof(data):
        bytes_to_recieve = size - sys.getsizeof(data)
        new_data = socket.recv(bytes_to_recieve)
        data += new_data
        
    elif size == sys.getsizeof(data):
        data = pickle.loads(data)
        output("locks", "acquiring incoming lock")
        with mp.incoming_lock:
            recieved_commands.append(data)
        output("locks", "releasing incoming lock")

        size = None
        data = b''
        
    return recieved_commands, data, size