import os

import multiplayer_client
import multiplayer_server
from log import ts4mp_log_debug
from mp_utils import get_current_user_directory

try:
    # TODO: Implement a better way to test if user is a client/server
    is_client = False

    if os._exists("{}client.txt".format(get_current_user_directory())):
        is_client = True

    if is_client:
        client_instance = multiplayer_client.Client()
        client_instance.listen()
        client_instance.send()
    else:
        server_instance = multiplayer_server.Server()
        server_instance.listen()
        server_instance.send()

except Exception as e:
    ts4mp_log_debug("errors", str(e))
