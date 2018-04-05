from update import output_irregardelessly as output
import services, sims4
import server.clientmanager
import distributor.system


@sims4.commands.Command('get_con', command_type=sims4.commands.CommandType.Live)
def get_con(_connection=None):
    #Gets the current client connection
    output = sims4.commands.CheatOutput(_connection) 
    output(str(_connection))
    
@sims4.commands.Command('get_clients', command_type=sims4.commands.CommandType.Live)
def get_clients(_connection=None):
    output = sims4.commands.CheatOutput(_connection) 
    clients = services.client_manager()._objects.values()    
    #Gets all the current client connections
    for client in clients:
        output(str(client.id))
        
@sims4.commands.Command('add_client_sims', command_type=sims4.commands.CommandType.Live)
def add_client_sims(_connection=None):
    output = sims4.commands.CheatOutput(_connection) 
    client = services.client_manager().get(1000)
    first_client = services.client_manager().get_first_client()
    #Add the first client's selectable sims to the new client's. Only expecst one multiplayer client at the moment.
    for sim in client._selectable_sims:
        output(str(sim))
    
    output(str(len(client._selectable_sims)))
    
    for sim_info in first_client._selectable_sims:
        client._selectable_sims.add_selectable_sim_info(sim_info)
    client.set_next_sim()
    
    
@sims4.commands.Command('cnc', command_type=sims4.commands.CommandType.Live)
def cnc(_connection=None):      
    #Create a new client. Deprecated.
    output = sims4.commands.CheatOutput(_connection) 
    client = services.client_manager().get_first_client()
    account = server.account.Account(865431, "Jon Snow")
    new_client = services.client_manager().create_client(1000, account, client._household_id)
    # new_client.clear_selectable_sims()
    # for sim_info in client._selectable_sims:
        # new_client._selectable_sims.add_selectable_sim_info(sim_info)
    # new_client.set_next_sim()

    output("Adding client")
    
@sims4.commands.Command('rem', command_type=sims4.commands.CommandType.Live)
def rem(_connection=None):      
    #Forcefully remove the multiplayer client. Only supports one multiplayer client at the moment. 
    output = sims4.commands.CheatOutput(_connection) 
    output("Attempting to remove client")
    distributor.system._distributor_instance.remove_client_from_id(1000)
    client_manager = services.client_manager()
    client = client_manager.get(1000)
    client_manager.remove(client)

    output("Removed client")

