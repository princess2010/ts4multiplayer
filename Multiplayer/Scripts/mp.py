import distributor
from update import output
import server.client as client
import omega
import injector
import pickle
import zone
import time
import services, glob, sims4, inspect, re
from server_commands.interaction_commands import has_choices, generate_choices, generate_phone_choices,  select_choice, cancel_mixer_interaction, cancel_super_interaction, push_interaction
from server_commands.clock_commands import set_speed
from decorator import decorator
from undecorated import undecorated

class Message:
    def __init__(self, msg_id, msg):
        self.msg_id = msg_id
        self.msg = msg
        
msg_count = 0
is_client = False
try:
    open("C:/Users/theoj/Documents/Electronic Arts/The Sims 4/Mods/Heuristics/Scripts/client", "rb")
    is_client = True
    
except Exception:
    pass
# @injector.inject_to(zone.Zone, "on_loading_screen_animation_finished")
# def on_loading_screen_animation_finished(original, self):
    # original(self)
files = glob.glob("C:/Users/theoj/Documents/Electronic Arts/The Sims 4/Mods/Heuristics/Scripts/delicious pickles/*.*")
file_count = len(files)
msg_count = file_count
    
def send_message_server(self, msg_id, msg):
    global msg_count
    output('id', str(self.id))
    if self.active:
        if self.id != 1000:
            omega.send(self.id, msg_id, msg.SerializeToString())
            message = msg
            file = open("C:/Users/theoj/Documents/Electronic Arts/The Sims 4/Mods/Heuristics/Scripts/delicious pickles/{}/{}.txt".format(self.id, msg_count), "a")
            file.write(str(message))
            file.close()
            msg_count += 1

    # if self.id == 1000:
        # message = Message(msg_id, msg.SerializeToString())
        # pickle.dump(message, open("C:/Users/theoj/Documents/Electronic Arts/The Sims 4/Mods/Heuristics/Scripts/delicious pickles/{}/{}.pkl".format(self.id, msg_count), "ab"))
                
            
def send_message_client(self, msg_id, msg):
    pass
    # don't actually send any commands at all from the original client's server



last_synced_message_for_client = 1
files = glob.glob("C:/Users/theoj/Documents/Electronic Arts/The Sims 4/Mods/Heuristics/Scripts/delicious pickles/*.*")
file_count = len(files)
last_synced_message_for_client = file_count
def client_sync():
    global last_synced_message_for_client
    client_instance = services.client_manager().get_first_client()

    files = glob.glob("C:/Users/theoj/Documents/Electronic Arts/The Sims 4/Mods/Heuristics/Scripts/delicious pickles/*.*")
    file_count = len(files)

    for message_no in range(last_synced_message_for_client, file_count):
        msg_data = open("C:/Users/theoj/Documents/Electronic Arts/The Sims 4/Mods/Heuristics/Scripts/delicious pickles/{}.pkl".format(message_no), 'rb')
        unpacked_msg_data = pickle.load(msg_data)
        omega.send(client_instance.id, unpacked_msg_data.msg_id, unpacked_msg_data.msg)
            
    last_synced_message_for_client = file_count
    
last_synced_command_for_server = 0

def parse_arg(arg):
    new_arg = arg
    orig_arg = new_arg.replace('"', "").replace("(", "").replace(")", "").replace("'", "").replace(" ", "")
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
command_count = 1
regex = re.compile('[a-zA-Z]')

command_names = ['interactions.has_choices',
                                      'interactions.choices',
                                      'interactions.phone_choices',
                                      'interactions.select',
                                      'interactions.cancel',
                                      'interactions.cancel_si',
                                      'interactions.push',
                                      'clock.setspeed']
           
                                      
functions= [has_choices,
                    generate_choices,
                    generate_phone_choices,
                    select_choice,
                    cancel_mixer_interaction,
                    cancel_super_interaction,
                    push_interaction,
                    set_speed]

           
function_names = ["has_choices",
                    "generate_choices",
                    "generate_phone_choices",
                    "select_choice",
                    "cancel_mixer_interaction",
                    "cancel_super_interaction",
                    "push_interaction",
                    "set_speed"]


def server_update():
    global last_synced_command_for_server
    global command_count
    client_instance = services.client_manager().get_first_client()

    commands_to_be_processed = open("C:/Sandbox/Theo/DefaultBox/user/current/Documents/Electronic Arts/The Sims 4/Mods/Heuristics/Scripts/command_log.txt" , 'r')
    commands_to_be_processed = commands_to_be_processed.read()
    commands_to_be_processed = commands_to_be_processed.split('\n')

    for command in commands_to_be_processed[command_count : len(commands_to_be_processed)]:
        current_line = command.split(',')
        function_name = current_line[0]
        if function_name == '':
            continue
        parsed_args = []
        # output('arg_handler', str(current_line) + "\n")

        command_count += 1
        for arg_index in range(1, len(current_line)):
            arg = current_line[arg_index].replace(')', '').replace('{}', '').replace('(', '')
            if "'" not in arg:
                arg = regex.sub('', arg)
                arg = arg.replace('<._ = ', '').replace('>', '')
            parsed_arg = parse_arg(arg)
            parsed_args.append(parsed_arg)
        # output('arg_handler', "{}".format(function_name))
            
        function_to_execute = "{}({})".format(function_name, str(parsed_args).replace('[', '').replace(']',''))
        output('arg_handler', str(function_to_execute) + "\n" )
        exec(function_to_execute)



@decorator
def wrapper(func, *args, **kwargs):
    output("command_log",  "\n" + str(func.__name__) + ", " + str(args) +  "  " + str(kwargs))
    def do_nothing():
        pass
    # return func(*args, **kwargs)
    return do_nothing



# def server_process():
    # global last_synced_message_for_client
    # last_synced_message_for_server = 1s
    
def on_tick_client():
    try:
        client = services.client_manager().get_first_client()
    except Exception:
        return
    client_sync()


def on_tick_server():
    try:
        client = services.client_manager().get_first_client()
    except Exception:
        return
    server_update()
if is_client:
    sims4.core_services.on_tick = on_tick_client
    client.Client.send_message = send_message_client
    for index in range(len(command_names)):
        functions[index] = sims4.commands.Command(command_names[index], command_type=sims4.commands.CommandType.Live)(wrapper(undecorated(functions[index])))
        
else:
    client.Client.send_message = send_message_server
    sims4.core_services.on_tick = on_tick_server

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

