from update import output_irregardelessly as output
import services, glob, sims4, inspect, re
from server.client import Client


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
        
@sims4.commands.Command('cly', command_type=sims4.commands.CommandType.Live)
def cly(_connection=None):      
    output = sims4.commands.CheatOutput(_connection) 
    client = services.client_manager().get_first_client()
    new_client = services.client_manager().create_client(1000, client._account, client._household_id)
    new_client = Client(1000, client._account, client._household_id)
    # zone = services.current_zone()
    # zone.on_client_connect(new_client)
    # services.on_client_connect(new_client)
    new_client.clear_selectable_sims()
    for sim_info in client._selectable_sims:
        new_client._selectable_sims.add_selectable_sim_info(sim_info)
    new_client.set_next_sim()

    output("Adding client")
@sims4.commands.Command('sel', command_type=sims4.commands.CommandType.Live)
def make_all_sims_selectable(_connection=None):
    client = services.client_manager().get_first_client()
    client.clear_selectable_sims()
    for sim_info in services.sim_info_manager().objects:
        client._selectable_sims.add_selectable_sim_info(sim_info)
    client.set_next_sim()

    
@sims4.commands.Command('checkid', command_type=sims4.commands.CommandType.Live)
def checkid (_connection=None):
    # obj = object_manager.get(object_id)
    for obj in list(services.object_manager().objects):
        output('obj', str(obj) + " " + str(obj.id) +"\n")
import distributor.system
from distributor.system import Journal, logger, _send_index, _distributor_log_enabled
import gsi_handlers
from protocolbuffers import Distributor_pb2 as protocols
from protocolbuffers.Consts_pb2 import MSG_OBJECTS_VIEW_UPDATE, MGR_UNMANAGED
from gsi_handlers.distributor_handlers import archive_operation
import weakref
from graph_algos import topological_sort

#to be moved to cly
def new_init(self):
    self.journal = Journal()

    self._pending_creates = weakref.WeakSet()
    self.client = None
    self.clients = []
    #we're keeping it here to not break other parts of the code that isn't the distributor
    self.events = []
    
def add_object(self, obj):
    logger.info('Adding {0}', obj)
    obj.visible_to_client = True
    if not obj.visible_to_client:
        return
    if not services.client_manager():
        return
    op = obj.get_create_op()
    if op is None:
        obj.visible_to_client = False
        return
    self.journal.add(obj, op, ignore_deferral=True)
    self._pending_creates.add(obj)
    if hasattr(obj, 'on_add_to_client'):
        obj.on_add_to_client()

def _add_ops_for_client_connect(self, client):
    node_gen = client.get_objects_in_view_gen()
    parents_gen_fn = lambda obj: obj.get_create_after_objs()
    create_order = topological_sort(node_gen, parents_gen_fn)
    for obj in create_order:
        create_op = obj.get_create_op()
        if create_op is not None:
            self.journal.add(obj, create_op)
    
def add_client(self, client):
    output("id", "New Client" + "\n")
    
    if client in self.clients:
        self.client = client
        raise ValueError('Client is already registered')
    self.process()
    logger.info('Adding {0}', client)
    self.clients.append(client)
    self._add_ops_for_client_connect(client)
    
def remove_client(self, client):
    logger.info('Removing {0}', client)
    self.process()
    self.clients.remove(client)

def _send_view_updates(self):
    for client in self.clients:
        if self.journal.entries:
            ops = list(self.journal.entries)
            self.journal.clear()
            try:
                self._send_view_updates_for_client(client, ops)
            except:
                logger.exception('Error sending view updates to client!')
                
    self._pending_creates.clear()    
        
def process_events(self):
    for (msg_id, msg) in self.events:
        for client in self.clients:
            client.send_message(msg_id, msg)
    del self.events[:]
    
def add_event(self, msg_id, msg, immediate=False):
    if len(self.clients) == 0:
        logger.error('Could not add event {0} because there are no attached clients', msg_id)
        return
    self.events.append((msg_id, msg))
    if immediate:
        self.process_events()
        
def add_op(self, obj, op):
        self.journal.add(obj, op)

def add_op_with_no_owner(self, op):
        self.journal.add(None, op)
        
def send_op_with_no_owner_immediate(self, op):
    global _send_index
    journal_seed = self.journal._build_journal_seed(op, obj=None)
    journal_entry = self.journal._build_journal_entry(journal_seed)
    (obj_id, operation, manager_id, obj_name) = journal_entry
    view_update = protocols.ViewUpdate()
    entry = view_update.entries.add()
    entry.primary_channel.id.manager_id = manager_id
    entry.primary_channel.id.object_id = obj_id
    entry.operation_list.operations.append(operation)
    if gsi_handlers.distributor_handlers.archiver.enabled or gsi_handlers.distributor_handlers.sim_archiver.enabled:
        _send_index += 1
        if _send_index >= 4294967295:
            _send_index = 0
        for client in self.clients:
            archive_operation(obj_id, obj_name, manager_id, operation, _send_index, client)
    for client in self.clients:
        client.send_message(MSG_OBJECTS_VIEW_UPDATE, view_update)
    if _distributor_log_enabled:
        logger.error('------- SENT IMMEDIATE --------')


        
distributor.system.Distributor.__init__ = new_init
distributor.system.Distributor.add_object = add_object
distributor.system.Distributor._add_ops_for_client_connect = _add_ops_for_client_connect

distributor.system.Distributor.add_client = add_client
distributor.system.Distributor.remove_client = remove_client
distributor.system.Distributor.send_op_with_no_owner_immediate = send_op_with_no_owner_immediate
distributor.system.Distributor.add_event = add_event
distributor.system.Distributor.add_op = add_op
distributor.system.Distributor.add_op_with_no_owner = add_op_with_no_owner


distributor.system.Distributor.process_events = process_events
distributor.system.Distributor._send_view_updates = _send_view_updates