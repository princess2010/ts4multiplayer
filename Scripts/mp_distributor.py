from update import output_irregardelessly as output
import services, glob, sims4, inspect, re
from server.client import Client
import server.clientmanager

@sims4.commands.Command('get_con', command_type=sims4.commands.CommandType.Live)
def get_con(_connection=None):
    output = sims4.commands.CheatOutput(_connection) 
    output(str(_connection))
    
@sims4.commands.Command('get_cl', command_type=sims4.commands.CommandType.Live)
def get_cl(_connection=None):
    output = sims4.commands.CheatOutput(_connection) 
    clients = services.client_manager()._objects.values()    
    for client in clients:
        output(str(client.id))
        
def get_first_client(self):
    for client in self._objects.values():
        # output("log", client.id)

        if client.id == 1000:
            continue
        return client
        
server.clientmanager.ClientManager.get_first_client = get_first_client

@sims4.commands.Command('cly', command_type=sims4.commands.CommandType.Live)
def cly(_connection=None):      
    output = sims4.commands.CheatOutput(_connection) 
    client = services.client_manager().get_first_client()
    new_client = services.client_manager().create_client(1000, client._account, client._household_id)
    new_client.clear_selectable_sims()
    for sim_info in client._selectable_sims:
        new_client._selectable_sims.add_selectable_sim_info(sim_info)
    new_client.set_next_sim()

    output("Adding client")
