from update import output, output_irregardelessly
from mp import is_client
from mp_essential import incoming_commands, outgoing_commands, incoming_lock, outgoing_lock
from mp_essential import server_sync, client_sync, Message

import sims4, services
from server_commands.interaction_commands import has_choices, generate_choices, generate_phone_choices,  select_choice, cancel_mixer_interaction, cancel_super_interaction, push_interaction
from server_commands.clock_commands import set_speed
from server_commands.sim_commands import set_active_sim
import server.client as client

import omega

from decorator import decorator
from undecorated import undecorated  







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


def send_message_server(self, msg_id, msg):
        #Send message override for the server.
        #This overrides it so any message for a client with an id of 1000 gets packed into a Message and is placed in the outgoing_commands list for
        #sending out to the multiplayer clients.
        #Only supports one multiplayer client at the moment.
        
        global outgoing_commands
        if self.id != 1000:                
            if self.active:

                omega.send(self.id, msg_id, msg.SerializeToString())
                # output_irregardelessly("msg", msg)
        else:
            message = Message(msg_id, msg.SerializeToString())
            output("locks", "acquiring outgoing lock")
            #We use a lock here because outgoing_commands is also being altered by the client socket thread.
            with outgoing_lock:
                outgoing_commands.append(message)
            output("locks", "releasing outgoing lock")
            pass
            
def send_message_client(self, msg_id, msg):
    #Send Message override for the client.
    #We don't want any of the original server sending stuff to the client.
    #So we override it to do absolutely nothing.
    pass
    
@decorator
def wrapper_client(func, *args, **kwargs):
    #Wrapper for functions that have their data needed to be sent to the server.
    #This is used for client commands so the server can respond.
    #For example, selecting a choice from the pie menu.
    #Only supports one multiplayer client at the moment. 
    output("locks", "acquiring outgoing lock")

    with outgoing_lock:
        global outgoing_commands
        output_irregardelessly("arg_handler", "\n" + str(func.__name__) + ", " + str(args) + "  " + str(kwargs))

        outgoing_commands.append("\n" + str(func.__name__) + ", " + str(args) +  "  " + str(kwargs))
        def do_nothing():
            pass
        return do_nothing
    output("locks", "releasing outgoing lock")


def on_tick_client():
    #On Tick override for the client.
    #If we don't have any client, that means we aren't in a zone yet.
    #If we do have at least one client, that means we are in a zone and can sync information.
    try:
        client = services.client_manager().get_first_client()
        if client == None:
            return
    except Exception:
        return
    client_sync()

def on_tick_server():
    #On Tick override for the client.
    #If we don't have any client, that means we aren't in a zone yet.
    #If we do have at least one client, that means we are in a zone and can sync information.
    try:
        client = services.client_manager().get_first_client()
        if client == None:
            return
    except Exception:
        return
    server_sync()


if is_client:
    client.Client.send_message = send_message_client
    sims4.core_services.on_tick = on_tick_client
    
    for index in range(len(command_names)):
        functions[index] = sims4.commands.Command(command_names[index], command_type=sims4.commands.CommandType.Live)(wrapper_client(undecorated(functions[index])))
        
else:
    client.Client.send_message = send_message_server
    sims4.core_services.on_tick = on_tick_server

