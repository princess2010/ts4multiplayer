from update import output, output_irregardelessly
import sims4


try:
    is_client = False
    try:
        open("C:/Users/theoj/Documents/Electronic Arts/The Sims 4/Mods/Heuristics/Scripts/client", "rb")
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