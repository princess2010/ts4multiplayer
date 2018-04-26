from mp_utils import get_sims_documents_directory

DEBUG_MODE = True


def ts4mp_log_debug(filename, string, force=False):
    global DEBUG_MODE

    if DEBUG_MODE is False and force is False:
        return

    logs_directory = "{}ts4mp_logs/".format(get_sims_documents_directory())

    with open("{}{}.txt".format(logs_directory, filename), 'a') as stream:
        stream.write(str(string) + "\n")
