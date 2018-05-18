import os

from ts4mp.core.mp_utils import get_sims_documents_directory
from threading import Lock

fileLock = Lock()
DEBUG_MODE = True


def ts4mp_log(filename, string, force=False):
    global DEBUG_MODE

    if DEBUG_MODE is False and force is False:
        return



    logs_directory = "{}ts4mp_logs/".format(get_sims_documents_directory())

    if not os.path.exists(logs_directory):
        os.makedirs(logs_directory)

    with fileLock:
        with open("{}{}.txt".format(logs_directory, filename), 'a') as stream:
            stream.write(str(string) + "\n")
