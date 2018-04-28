import os.path

import sims4.commands
from sims4 import reload
from ts4mp.core.mp_utils import get_sims_documents_directory


@sims4.commands.Command('ts4mp.reload', command_type=sims4.commands.CommandType.Live)
def reload_maslow(module: str, _connection=None):
    output = sims4.commands.CheatOutput(_connection)

    try:
        dirname = get_sims_documents_directory()
        filename = os.path.join(dirname, module) + ".py"

        output("Reloading {}".format(filename))

        reloaded_module = reload.reload_file(filename)

        if reloaded_module is not None:
            output("Done reloading!")
        else:
            output("Error loading module or module does not exist")

    except Exception as e:
        output("Reload failed: ")

        for v in e.args:
            output(v)
