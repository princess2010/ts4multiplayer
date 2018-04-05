from update import output, output_irregardelessly


try:

    import distributor
    import server.client as client
    import omega
    import injector
    import pickle
    import zone
    import time
    import services, glob, sims4, inspect, re
    from server_commands.interaction_commands import has_choices, generate_choices, generate_phone_choices,  select_choice, cancel_mixer_interaction, cancel_super_interaction, push_interaction
    from server_commands.clock_commands import set_speed
    from server_commands.sim_commands import set_active_sim
    from decorator import decorator
    from undecorated import undecorated
    from threading import Lock, RLock
    from protocolbuffers import DistributorOps_pb2
    from protocolbuffers import Consts_pb2
    from pending_client_commands import pending_commands_lock, pendable_functions
    protocol_constants = DistributorOps_pb2.Operation

    outgoing_lock = Lock()
    incoming_lock = Lock()

    incoming_commands = []
    outgoing_commands = []
    pending_commands = {}


    
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

    def send_message_server(self, msg_id, msg):
            global outgoing_commands
            if self.id != 1000:                
                if self.active:
                    # output_irregardelessly("messages original", msg)

                    omega.send(self.id, msg_id, msg.SerializeToString())
            else:
                # output_irregardelessly("messages client", msg)
                message = Message(msg_id, msg.SerializeToString())
                output("locks", "acquiring outgoing lock")
                # output_irregardelessly("messages", msg)
                with outgoing_lock:
                    outgoing_commands.append(message)
                output("locks", "releasing outgoing lock")
                pass

                
    def send_message_client(self, msg_id, msg):
        pass



    def client_sync():
        output("locks", "acquiring incoming lock 1")

        with incoming_lock:
            global incoming_commands
            client_instance = services.client_manager().get_first_client()
            output("receive", "{} \n".format(len(incoming_commands)))
            for unpacked_msg_data in incoming_commands:
                omega.send(client_instance.id, unpacked_msg_data.msg_id, unpacked_msg_data.msg)
                incoming_commands.remove(unpacked_msg_data)
        output("locks", "releasing incoming lock")

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
                                          'clock.setspeed',
                                          'sims.set_active']
               
                                          
    functions= [has_choices,
                        generate_choices,
                        generate_phone_choices,
                        select_choice,
                        cancel_mixer_interaction,
                        cancel_super_interaction,
                        push_interaction,
                        set_speed, 
                        set_active_sim]

               
    function_names = ["has_choices",
                        "generate_choices",
                        "generate_phone_choices",
                        "select_choice",
                        "cancel_mixer_interaction",
                        "cancel_super_interaction",
                        "push_interaction",
                        "set_speed",
                        "set_active_sim"]


    def server_update():
      output("locks", "acquiring incoming lock 1")

      with incoming_lock:
        
            global last_synced_command_for_server
            global command_count
            client_instance = services.client_manager().get_first_client()

            for command in incoming_commands:
                
                current_line = command.split(',')
                function_name = current_line[0]
                if function_name == '':
                    continue
                parsed_args = []

                command_count += 1
                for arg_index in range(1, len(current_line)):
                    arg = current_line[arg_index].replace(')', '').replace('{}', '').replace('(', '')
                    if "'" not in arg:
                        arg = regex.sub('', arg)
                        arg = arg.replace('<._ = ', '').replace('>', '')
                    parsed_arg = parse_arg(arg)
                    parsed_args.append(parsed_arg)
                #set connection to other client
                client_id = 1000
                parsed_args[-1] = client_id
                function_to_execute = "{}({})".format(function_name, str(parsed_args).replace('[', '').replace(']',''))
                function_name = function_name.strip()
                output_irregardelessly("client_specific", "New function called {} recieved".format(function_name))
                if function_name in pendable_functions:
                    with pending_commands_lock:
                        if function_name not in pending_commands:
                            pending_commands[function_name] = []
                        if client_id not in pending_commands[function_name]:
                            pending_commands[function_name].append(client_id)
                output_irregardelessly('arg_handler', str(function_to_execute) )
                try:
                    exec(function_to_execute)
                except:
                    output("Execution Errors", "Something happened")
                incoming_commands.remove(command)
      output("locks", "releasing incoming lock")


    @decorator
    def wrapper_client(func, *args, **kwargs):
        output("locks", "acquiring outgoing lock")
        with outgoing_lock:
            global outgoing_commands
            outgoing_commands.append("\n" + str(func.__name__) + ", " + str(args) +  "  " + str(kwargs))
            def do_nothing():
                pass
            return do_nothing
        output("locks", "releasing outgoing lock")


    def on_tick_client():
        try:
            client = services.client_manager().get_first_client()
            if client == None:
                return
        except Exception:
            return
        client_sync()

    def on_tick_server():
        try:
            client = services.client_manager().get_first_client()
            if client == None:
                return
        except Exception:
            return
        server_update()
        
        
    import multiplayer_server
    import multiplayer_client
    if is_client:
        client.Client.send_message = send_message_client
        sims4.core_services.on_tick = on_tick_client
        
        for index in range(len(command_names)):
            functions[index] = sims4.commands.Command(command_names[index], command_type=sims4.commands.CommandType.Live)(wrapper_client(undecorated(functions[index])))
            
        client_instance = multiplayer_client.Client()
        client_instance.listen()
        client_instance.send()
    else:
        client.Client.send_message = send_message_server
        sims4.core_services.on_tick = on_tick_server
        server_instance = multiplayer_server.Server()
        server_instance.listen()
        server_instance.send()

    @sims4.commands.Command('get_con', command_type=sims4.commands.CommandType.Live)
    def get_con(_connection=None):
        output = sims4.commands.CheatOutput(_connection) 
        output(str(_connection))
        
        
    @sims4.commands.Command('checkid', command_type=sims4.commands.CommandType.Live)
    def checkid (_connection=None):
        for obj in list(services.object_manager().objects):
            output('obj', str(obj) + " " + str(obj.id) +"\n")
            
    @sims4.commands.Command('shutdown', command_type=sims4.commands.CommandType.Live)
    def shutdown_server(_connection=None):
        server_instance.shutdown(socket.SHUT_RDWR)
        server_instance.close()
except Exception as e:
    output("errors", str(e))