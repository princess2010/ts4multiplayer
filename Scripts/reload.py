import sims4.commands

import sims4.reload as r

import os.path



@sims4.commands.Command('reload', command_type=sims4.commands.CommandType.Live)

def reload_maslow(module:str, _connection=None):

    output = sims4.commands.CheatOutput(_connection)

    try:

        dirname = os.path.dirname(os.path.realpath(__file__))

        filename = os.path.join(dirname, module) + ".py"

        output("Reloading {}".format(filename))

        reloaded_module = r.reload_file(filename)

        if reloaded_module is not None:

            output("Done reloading!")

        else:

            output("Error loading module or module does not exist")

    except BaseException as e:

        output("Reload failed: ")

        for v in e.args:

            output(v)
