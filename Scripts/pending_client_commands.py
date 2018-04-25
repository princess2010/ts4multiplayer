from threading import Lock

from protocolbuffers import Consts_pb2

pending_commands = dict()
pending_commands_lock = Lock()

pendable_functions = (
    "has_choices",
    "generate_choices"
)

command_to_pb = {
    Consts_pb2.MSG_OBJECT_IS_INTERACTABLE: "has_choices",
    Consts_pb2.MSG_PIE_MENU_CREATE       : "generate_choices"
}


def get_command_function_from_pb(pb):
    if pb in command_to_pb:
        return command_to_pb[pb]
    else:
        return None


def try_get_client_id_of_pending_command(command):
    with pending_commands_lock:
        if command in pending_commands:
            if len(pending_commands[command]) > 0:
                return pending_commands[command][0]
        else:
            return None

    return None


def remove_earliest_command_client(command):
    with pending_commands_lock:
        if command in pending_commands:
            pending_commands[command].pop(0)
