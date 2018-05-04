import os
import re
from threading import Lock

import omega
import services
from server_commands.clock_commands import set_speed, request_pause, unrequest_pause, toggle_pause_unpause
from server_commands.interaction_commands import has_choices, generate_choices, generate_phone_choices, select_choice, cancel_mixer_interaction, cancel_super_interaction, push_interaction
from server_commands.lighting_commands import set_color_and_intensity
from server_commands.sim_commands import set_active_sim
from server_commands.ui_commands import ui_dialog_respond, ui_dialog_pick_result, ui_dialog_text_input

from ts4mp.core.csn import mp_chat
from ts4mp.debug.log import ts4mp_log
from ts4mp.core.mp_utils import get_sims_documents_directory
from ts4mp.core.pending_client_commands import pending_commands_lock, pendable_functions, pending_commands

ALPHABETIC_REGEX = re.compile('[a-zA-Z]')

PERFORM_COMMAND_FUNCTIONS = {
    "has_choices"             : has_choices,
    "generate_choices"        : generate_choices,
    "generate_phone_choices"  : generate_phone_choices,
    "select_choice"           : select_choice,
    "cancel_mixer_interaction": cancel_mixer_interaction,
    "cancel_super_interaction": cancel_super_interaction,
    "push_interaction"        : push_interaction,
    "set_speed"               : set_speed,
    "request_pause"           : request_pause,
    "unrequest_pause"         : unrequest_pause,
    "toggle_pause_unpause"    : toggle_pause_unpause,
    "set_active_sim"          : set_active_sim,
    "mp_chat"                 : mp_chat,
    "ui_dialog_respond"       : ui_dialog_respond,
    "ui_dialog_pick_result"   : ui_dialog_pick_result,
    "ui_dialog_text_input"    : ui_dialog_text_input,
    "set_color_and_intensity" : set_color_and_intensity,
}

# TODO: Consider having a class that holds these instead of them being out in the open
incoming_commands = list()
outgoing_commands = list()

outgoing_lock = Lock()
incoming_lock = Lock()


def _do_command(command_name, *args):
    global PERFORM_COMMAND_FUNCTIONS

    if command_name in PERFORM_COMMAND_FUNCTIONS:
        PERFORM_COMMAND_FUNCTIONS[command_name](*args)

        ts4mp_log("commands", "There is a command named: {}. Executing it.".format(command_name))
    else:
        ts4mp_log("commands", "There is no such command named: {}!".format(command_name))


# TODO: Less generic names
class Message:
    def __init__(self, msg_id, msg):
        self.msg_id = msg_id
        self.msg = msg


class File:
    def __init__(self, file_name, file_contents):
        self.file_name = file_name
        self.file_contents = file_contents


def get_file_matching_name(name):
    scratch_directory = "{}saves/scratch".format(get_sims_documents_directory())

    file_path = ""
    file_name = ""

    for root, _, files in os.walk(scratch_directory):
        for file_name in files:
            replaced = file_name.replace("zoneObjects-", "").replace("-6.sav", "").strip()
            replaced = replaced[1:]

            ts4mp_log("zone_id", "{} , {}".format(replaced, name))

            if name == replaced:
                file_path = str(os.path.join(root, file_name))
                break

    return (file_path, file_name)


# TODO: Any kind of documentation for any of this so it's easier to understand in a year?
def client_sync():
    ts4mp_log("locks", "acquiring incoming lock 1")

    with incoming_lock:
        global incoming_commands

        ts4mp_log("receive", "{} \n".format(len(incoming_commands)))

        client_manager = services.client_manager()
        client = None

        if client_manager is not None:
            client = client_manager.get_first_client()

            if client is None:
                return

        for unpacked_msg_data in incoming_commands:
            if type(unpacked_msg_data) is Message:
                omega.send(client.id, unpacked_msg_data.msg_id, unpacked_msg_data.msg)
                incoming_commands.remove(unpacked_msg_data)
            elif type(unpacked_msg_data) is File:
                (file_path, _) = get_file_matching_name(unpacked_msg_data.file_name)
                client_file = open(file_path, "wb")
                new_architecture_data = unpacked_msg_data.file_contents

                client_file.write(new_architecture_data)
                client_file.close()

                incoming_commands.remove(unpacked_msg_data)

    ts4mp_log("locks", "releasing incoming lock")


def server_sync():
    ts4mp_log("locks", "acquiring incoming lock 1")

    with incoming_lock:
        global incoming_commands

        for command in incoming_commands:
            current_line = command.split(',')
            function_name = current_line[0]

            if not function_name:
                continue

            parsed_args = list()

            for arg_index in range(1, len(current_line)):
                arg = current_line[arg_index].replace(')', '').replace('{}', '').replace('(', '')

                if "'" not in arg:
                    arg = ALPHABETIC_REGEX.sub('', arg)
                    arg = arg.replace('<._ = ', '').replace('>', '')

                parsed_arg = _parse_arg(arg)
                parsed_args.append(parsed_arg)

            # set connection to other client
            client_id = 1000
            parsed_args[-1] = client_id

            function_to_execute = "{}({})".format(function_name, str(parsed_args).replace('[', '').replace(']', ''))
            function_name = function_name.strip()

            ts4mp_log("client_specific", "New function called {} recieved".format(function_name))

            if function_name in pendable_functions:
                with pending_commands_lock:
                    if function_name not in pending_commands:
                        pending_commands[function_name] = []
                    if client_id not in pending_commands[function_name]:
                        pending_commands[function_name].append(client_id)

            ts4mp_log('arg_handler', str(function_to_execute))

            try:
                _do_command(function_name, *parsed_args)
            except Exception as e:
                ts4mp_log("Execution Errors", str(e))

            incoming_commands.remove(command)

    ts4mp_log("locks", "releasing incoming lock")


def _parse_arg(arg):
    #Horrible, hacky way of parsing arguments from the client commands.
    #DO NOT EVER CHANGE THESE LINES OF CODE.
    #IT WILL SCREW UP OBJECT IDS AND VERY LONG NUMBERS, EVEN THOUGH IT SEEMS THAT THIS CODE IS COMPLETELY
    #USELESS. THE ASSIGNING OF THE VARIABLE TO ANOTHER VARIABLE CAUSES IT TO BREAK IF REMOVED
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
    ts4mp_log("arg_handler", str(new_arg) + "\n", force=False)

    return new_arg
