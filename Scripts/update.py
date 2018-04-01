import gsi_handlers.posture_graph_handlers
import xml.etree
import services
import sims4.commands
from server_commands.argument_helpers import OptionalTargetParam, get_optional_target, TunableInstanceParam

# gsi_handlers.posture_graph_handlers.archiver._archive_enabled = True
import services
from postures.posture_specs import PostureSpec

def output(filename, string):
    with open("C:/Users/theoj/Documents/Electronic Arts/The Sims 4/Mods/Heuristics/Scripts/{}.txt".format(filename), 'a') as output:
        output.write(string)
