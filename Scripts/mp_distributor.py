from update import output_irregardelessly as output
import services, glob, sims4, inspect, re
from server.client import Client
import server.clientmanager
import distributor.distributor_service
import system_distributor
from mp import is_client
import server.account
import server.client
from distributor.system import Distributor
import distributor.system

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
        
@sims4.commands.Command('get_sel', command_type=sims4.commands.CommandType.Live)
def get_sel(_connection=None):
    output = sims4.commands.CheatOutput(_connection) 
    client = services.client_manager().get(1000)
    first_client = services.client_manager().get_first_client()
    for sim in client._selectable_sims:
        output(str(sim))
    
    output(str(len(client._selectable_sims)))
    
    for sim_info in first_client._selectable_sims:
        client._selectable_sims.add_selectable_sim_info(sim_info)
    client.set_next_sim()

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
    account = server.account.Account(865431, "Jon Snow")
    new_client = services.client_manager().create_client(1000, account, client._household_id)
    # new_client.clear_selectable_sims()
    # for sim_info in client._selectable_sims:
        # new_client._selectable_sims.add_selectable_sim_info(sim_info)
    # new_client.set_next_sim()

    output("Adding client")
    
@sims4.commands.Command('rem', command_type=sims4.commands.CommandType.Live)
def rem(_connection=None):      
    output = sims4.commands.CheatOutput(_connection) 
    output("Attempting to remove client")
    distributor.system._distributor_instance.remove_client_from_id(1000)
    client_manager = services.client_manager()
    client = client_manager.get(1000)
    client_manager.remove(client)

    output("Removed client")

def start(self):
    import animation.arb
    animation.arb.set_tag_functions(distributor.system.get_next_tag_id, distributor.system.get_current_tag_set)
    distributor.system._distributor_instance = system_distributor.SystemDistributor()

def stop(self):
    distributor.system._distributor_instance = None

def on_tick(self):
    distributor.system._distributor_instance.process()
    

            
def on_add(self):
    if self.id != 1000:
        account = server.account.Account(865431, "Jon Snow")
        new_client = services.client_manager().create_client(1000, account, 0)
    for sim_info in self._selectable_sims:
        new_client._selectable_sims.add_selectable_sim_info(sim_info)
        new_client.set_next_sim()
    if self._account is not None:
        self._account.register_client(self)
    for sim_info in self._selectable_sims:
        self.on_sim_added_to_skewer(sim_info)
    distributor = Distributor.instance()
    distributor.add_object(self)
    distributor.add_client(self)
    self.send_selectable_sims_update()
    self.selectable_sims.add_watcher(self, self.send_selectable_sims_update)
from distributor.rollback import ProtocolBufferRollback
from protocolbuffers import Sims_pb2
from objects import ALL_HIDDEN_REASONS
from distributor.ops import GenericProtocolBufferOp
from protocolbuffers.DistributorOps_pb2 import Operation
import distributor.ops
def send_selectable_sims_update(self):
    msg = Sims_pb2.UpdateSelectableSims()
    for sim_info in self._selectable_sims:
        with ProtocolBufferRollback(msg.sims) as new_sim:
            new_sim.id = sim_info.sim_id
            career = sim_info.career_tracker.get_currently_at_work_career()
            new_sim.at_work = career is not None and not career.is_at_active_event
            new_sim.is_selectable = sim_info.is_enabled_in_skewer
            (selector_visual_type, career_category) = self._get_selector_visual_type(sim_info)
            new_sim.selector_visual_type = selector_visual_type
            if career_category is not None:
                new_sim.career_category = career_category
            new_sim.can_care_for_toddler_at_home = sim_info.can_care_for_toddler_at_home
            if not sim_info.is_instanced(allow_hidden_flags=ALL_HIDDEN_REASONS):
                new_sim.instance_info.zone_id = sim_info.zone_id
                new_sim.instance_info.world_id = sim_info.world_id
                new_sim.firstname = sim_info.first_name
                new_sim.lastname = sim_info.last_name
                zone_data_proto = services.get_persistence_service().get_zone_proto_buff(sim_info.zone_id)
                if zone_data_proto is not None:
                    new_sim.instance_info.zone_name = zone_data_proto.name
    distributor = Distributor.instance().get_client(self.id)
    distributor.add_op_with_no_owner(GenericProtocolBufferOp(Operation.SELECTABLE_SIMS_UPDATE, msg))
import distributor.fields

    
    
if not is_client:
    distributor.distributor_service.DistributorService.start = start
    distributor.distributor_service.DistributorService.stop = stop
    distributor.distributor_service.DistributorService.on_tick = on_tick
    server.client.Client.on_add = on_add
    server.client.Client.send_selectable_sims_update = send_selectable_sims_update
