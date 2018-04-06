from threading import Lock
from update import output
from update import output_irregardelessly

import omega, re
import services
from pending_client_commands import pending_commands_lock, pendable_functions, pending_commands
incoming_commands = []
outgoing_commands = []

outgoing_lock = Lock()
incoming_lock = Lock()

class Message:
    def __init__(self, msg_id, msg):
        self.msg_id = msg_id
        self.msg = msg
        
def parse_arg(arg):
    #Horrible, hacky way of parsing arguments from the client commands.
    new_arg = arg
    orig_arg = new_arg.replace('"', "").replace("(", "").replace(")", "").replace("'", "").replace(" ", "")
    new_arg = orig_arg
    try:
        new_arg = float(orig_arg)

        try: 
            new_arg = int(orig_arg)
        except BaseException:
            pass 
    except BaseException:
        pass 
    output("arg_handler", str(new_arg) + "\n")

    return new_arg
    
    
def client_sync():
    output("locks", "acquiring incoming lock 1")

    with incoming_lock:
        global incoming_commands
        client_instance = services.client_manager().get_first_client()
        output("receive", "{} \n".format(len(incoming_commands)))
        for unpacked_msg_data in incoming_commands:
            omega.send(client_instance.id, unpacked_msg_data.msg_id, unpacked_msg_data.msg)
            incoming_commands.remove(unpacked_msg_data)
    output("locks", "releasing incoming lock")

   

regex = re.compile('[a-zA-Z]')

def server_sync():
  output("locks", "acquiring incoming lock 1")
  with incoming_lock:
    global incoming_commands
    client_instance = services.client_manager().get_first_client()

    for command in incoming_commands:
        
        current_line = command.split(',')
        function_name = current_line[0]
        if function_name == '':
            continue
        parsed_args = []

        for arg_index in range(1, len(current_line)):
            arg = current_line[arg_index].replace(')', '').replace('{}', '').replace('(', '')
            if "'" not in arg:
                arg = regex.sub('', arg)
                arg = arg.replace('<._ = ', '').replace('>', '')
            parsed_arg = parse_arg(arg)
            parsed_args.append(parsed_arg)
        #set connection to other client
        client_id = 1000
        parsed_args[-1] = client_id
        function_to_execute = "{}({})".format(function_name, str(parsed_args).replace('[', '').replace(']',''))
        function_name = function_name.strip()
        output_irregardelessly("client_specific", "New function called {} recieved".format(function_name))
        if function_name in pendable_functions:
            with pending_commands_lock:
                if function_name not in pending_commands:
                    pending_commands[function_name] = []
                if client_id not in pending_commands[function_name]:
                    pending_commands[function_name].append(client_id)
        output_irregardelessly('arg_handler', str(function_to_execute) )
        try:
            exec(function_to_execute)
        except:
            output("Execution Errors", "Something happened")
        incoming_commands.remove(command)
  output("locks", "releasing incoming lock")

