from threading import Lock
# noinspection PyUnresolvedReferences
from update import output
from update import output_irregardelessly

import omega, re, os
import services
from pending_client_commands import pending_commands_lock, pendable_functions, pending_commands

from server_commands.interaction_commands import has_choices, generate_choices, generate_phone_choices,  select_choice, cancel_mixer_interaction, cancel_super_interaction, push_interaction
from server_commands.clock_commands import set_speed, request_pause, unrequest_pause, toggle_pause_unpause
from server_commands.sim_commands import set_active_sim
from server_commands.ui_commands import ui_dialog_respond, ui_dialog_pick_result, ui_dialog_text_input
from server_commands.lighting_commands import set_color_and_intensity

from csn import mp_chat
from mp_utils import get_current_user_directory
incoming_commands = []
outgoing_commands = []

outgoing_lock = Lock()
incoming_lock = Lock()

class Message:
    def __init__(self, msg_id, msg):
        self.msg_id = msg_id
        self.msg = msg
        
class File: 
    def __init__(self, file_name, file_contents):
        self.file_name = file_name
        self.file_contents = file_contents
        
command_functions ={
                    "has_choices": has_choices,
                    "generate_choices":  generate_choices,
                    "generate_phone_choices": generate_phone_choices,
                    "select_choice": select_choice,
                    "cancel_mixer_interaction": cancel_mixer_interaction,
                    "cancel_super_interaction": cancel_super_interaction,
                    "push_interaction": push_interaction,
                    "set_speed": set_speed, 
                    "set_active_sim": set_active_sim,
                    "mp_chat": mp_chat,
                    "ui_dialog_respond": ui_dialog_respond,
                    "ui_dialog_pick_result": ui_dialog_pick_result,
                    "ui_dialog_text_input": ui_dialog_text_input,
                    'request_pause' : request_pause,
                    'unrequest_pause' : unrequest_pause,
                    'toggle_pause_unpause' : toggle_pause_unpause,
                    "set_color_and_intensity" : set_color_and_intensity}

        
        
def parse_arg(arg):
    #Horrible, hacky way of parsing arguments from the client commands.
    new_arg = arg
    orig_arg = new_arg.replace('"', "").replace("(", "").replace(")", "").replace("'", "").strip()
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
    
def get_file_matching_name(name):
    for root, dirs, files in os.walk("{}/saves/scratch".format(get_current_user_directory().replace("Mods/Heuristics/Scripts/", ""))):
        for file_name in files:
            replaced = file_name.replace("zoneObjects-", "").replace("-6.sav", "").strip()
            replaced = replaced[1:]
            output_irregardelessly("zone_id", "{} , {}".format(replaced, name))
            if name == replaced:
                file_path = str(os.path.join(root, file_name))
                break
    return file_path, file_name
    
def client_sync():
    output("locks", "acquiring incoming lock 1")

    with incoming_lock:
        global incoming_commands
        output("receive", "{} \n".format(len(incoming_commands)))
        for unpacked_msg_data in incoming_commands:
            if type(unpacked_msg_data) is Message:
                try:
                    client = services.client_manager().get_first_client()
                    client_instance = services.client_manager().get_first_client()
                    
                    if client == None:
                        return
                except Exception:
                    continue
                    
                omega.send(client_instance.id, unpacked_msg_data.msg_id, unpacked_msg_data.msg)
                incoming_commands.remove(unpacked_msg_data)

            elif type(unpacked_msg_data) is File:
                client_file = open(get_file_matching_name(unpacked_msg_data.file_name)[0], "wb")
                new_architecture_data = unpacked_msg_data.file_contents
                client_file.write(new_architecture_data)
                client_file.close()
                incoming_commands.remove(unpacked_msg_data)
    output("locks", "releasing incoming lock")

   

regex = re.compile('[a-zA-Z]')

def do_command(command_name, *args):
    command_exists = command_name in command_functions
    output_irregardelessly("commands", command_exists)
    if command_exists:
        command_functions[command_name](*args)
        output_irregardelessly("commands", "There is a command named: {}. Executing it.".format(command_name))

    else:
        output_irregardelessly("commands", "There is no such command named: {}!".format(command_name))
    return 
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
            do_command(function_name, *parsed_args)
        except Exception as e:
            output_irregardelessly("Execution Errors", "Something happened: {}".format(e))
        incoming_commands.remove(command)
  output("locks", "releasing incoming lock")

