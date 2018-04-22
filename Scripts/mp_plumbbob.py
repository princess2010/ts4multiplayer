import objects
from update import output_irregardelessly as output
import services, sims4
from objects.parenting_utils import SetAsHead

@sims4.commands.Command('plum', command_type=sims4.commands.CommandType.Live)
def create_plumbbob(_connection=None):
    #Gets the current client connection
        try:
            created_obj = objects.system.create_object(9716920233444718179)
            current_sim = services.get_active_sim()
            pos = current_sim.position
            new_position = sims4.math.Vector3(float(pos.x), float(pos.y), float(pos.z))
            created_obj.move_to(translation=new_position)
            # output = sims4.commands.CheatOutput(_connection) 
            # output("Spawned plumbob")
            # SetAsHead.set_head_object(current_sim, created_obj, "0F97B21B")
            # output("plumb", dir(created_obj))
            created_obj.set_parent(current_sim)
        except Exception as e:
            output("plumb", e)