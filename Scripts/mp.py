from update import output, output_irregardelessly
import sims4
import socket
from mp_utils import get_current_user_directory
try:
    is_client = False
    try:
        open("{}client.txt".format(get_current_user_directory()), "rb")
        is_client = True
        
    except Exception:
        pass

        
    import multiplayer_server
    import multiplayer_client
    if is_client:
        client_instance = multiplayer_client.Client()
        client_instance.listen()
        client_instance.send()
    else:
        server_instance = multiplayer_server.Server()
        server_instance.listen()
        server_instance.send()

            
    @sims4.commands.Command('shutdown', command_type=sims4.commands.CommandType.Live)
    def shutdown_server(_connection=None):
        server_instance.shutdown(socket.SHUT_RDWR)
        server_instance.close()
except Exception as e:
    output("errors", str(e))