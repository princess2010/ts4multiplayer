import sys
import pickle
from struct import unpack, pack

def generic_send_loop(data, socket):
    data  = pickle.dumps(data)
    length = pack('>Q', sys.getsizeof(data))
    socket.send(length)
    socket.send(data)

    
def generic_listen_loop(socket, recieved_commands, data, size):
    print(size)
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
        recieved_commands.append(data)
        size = None
        data = b''
        
    return recieved_commands, data, size