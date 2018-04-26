import objects.system
import services
import sims4.commands
import sims4.math

from ts4mp.debug.log import ts4mp_log


@sims4.commands.Command('plum', command_type=sims4.commands.CommandType.Live)
def create_plumbbob(_connection=None):
    # Gets the current client connection
    try:
        sim_instance = services.get_active_sim()
        sim_position = sim_instance.position

        new_plumbob_position = sims4.math.Vector3(float(sim_position.x), float(sim_position.y), float(sim_position.z))

        plumbob_object = objects.system.create_object(9716920233444718179)
        plumbob_object.move_to(translation=new_plumbob_position)

        # output = sims4.commands.CheatOutput(_connection)
        # output("Spawned plumbob")
        # SetAsHead.set_head_object(current_sim, created_obj, "0F97B21B")
        # output("plumb", dir(created_obj))

        plumbob_object.set_parent(sim_instance)
    except Exception as e:
        ts4mp_log("plumb", e)
