import socket

import distributor.system
import persistence_module
import services
import sims4.commands
from protocolbuffers.FileSerialization_pb2 import ZoneObjectData
from server.account import Account
from world.travel_service import travel_sim_to_zone

from ts4mp.debug.log import ts4mp_log
from ts4mp.core.mp_essential import outgoing_commands, outgoing_lock, File, get_file_matching_name


@sims4.commands.Command('get_con', command_type=sims4.commands.CommandType.Live)
def get_con(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    # Gets the current client connection
    output(str(_connection))


@sims4.commands.Command('get_clients', command_type=sims4.commands.CommandType.Live)
def get_clients(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    # Gets all the current client connections
    clients = services.client_manager()._objects.values()

    for client in clients:
        output(str(client.id))


@sims4.commands.Command('add_client_sims', command_type=sims4.commands.CommandType.Live)
def add_client_sims(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    # Add the first client's selectable sims to the new client's. Only expecst one multiplayer client at the moment.
    client = services.client_manager().get(1000)
    first_client = services.client_manager().get_first_client()

    for sim in client._selectable_sims:
        output(str(sim))

    output(str(len(client._selectable_sims)))

    for sim_info in first_client._selectable_sims:
        client._selectable_sims.add_selectable_sim_info(sim_info)

    client.set_next_sim()


@sims4.commands.Command('cnc', command_type=sims4.commands.CommandType.Live)
def cnc(_connection=None):
    output = sims4.commands.CheatOutput(_connection)

    # Create a new client. Deprecated.
    client = services.client_manager().get_first_client()
    account = Account(865431, "Jon Snow")

    new_client = services.client_manager().create_client(1000, account, client._household_id)
    new_client.clear_selectable_sims()

    for sim_info in client._selectable_sims:
        new_client._selectable_sims.add_selectable_sim_info(sim_info)
        new_client.set_next_sim()

    output("Adding client")


@sims4.commands.Command('rem', command_type=sims4.commands.CommandType.Live)
def rem(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output("Attempting to remove client")

    # Forcefully remove the multiplayer client. Only supports one multiplayer client at the moment.
    distributor.system._distributor_instance.remove_client_from_id(1000)
    client_manager = services.client_manager()
    client = client_manager.get(1000)
    client_manager.remove(client)

    output("Removed client")


@sims4.commands.Command('get_name', command_type=sims4.commands.CommandType.Live)
def get_name(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output(str(socket.gethostname()))


@sims4.commands.Command('load_zone', command_type=sims4.commands.CommandType.Live)
def load_zone(_connection=None):
    try:
        zone = services.current_zone()
        name = str(hex(zone.id)).replace("0x", "")
        zone_objects_pb = ZoneObjectData()

        (file_path, _) = get_file_matching_name(name)
        zone_objects_message = open(file_path, "rb").read()

        ts4mp_log("msg", dir(zone_objects_pb))

        zone_objects_pb.ParseFromString(zone_objects_message)

        ts4mp_log("msg", zone_objects_pb)
        ts4mp_log("msg", zone_objects_message)

        persistence_module.run_persistence_operation(persistence_module.PersistenceOpType.kPersistenceOpLoadZoneObjects, zone_objects_pb, 0, None)
    except Exception as e:
        ts4mp_log("er", e)


@sims4.commands.Command('travel', command_type=sims4.commands.CommandType.Live)
def travel(_connection=None):
    client = services.client_manager().get_first_client()
    zone = services.current_zone()

    travel_sim_to_zone(client.active_sim.id, zone.id)


@sims4.commands.Command('get_zone', command_type=sims4.commands.CommandType.Live)
def get_zone_id(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    zone = services.current_zone()

    output(str(zone.id))


@sims4.commands.Command('send_lot_architecture_and_reload', command_type=sims4.commands.CommandType.Live)
def send_lot_architecture_and_reload(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    output("working")

    zone = services.current_zone()
    name = str(hex(zone.id)).replace("0x", "")

    ts4mp_log("zone_id", "{}, {}".format(name, zone.id))

    (file_path, file_name) = get_file_matching_name(name)

    if file_path is not None:
        with outgoing_lock:
            ts4mp_log("zone_id", "{}, {}".format(file_path, file_name))
            msg = File(name, open(file_path, "rb").read())
            outgoing_commands.append(msg)


@sims4.commands.Command('change_persona', command_type=sims4.commands.CommandType.Live)
def change_persona(_connection=None):
    output = sims4.commands.CheatOutput(_connection)
    client = services.client_manager().get_first_client()

    client._account._persona_name = "Corrin"
    output(client._account._persona_name)
