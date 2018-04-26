import os


def get_current_user_directory():
    return os.path.dirname(os.path.abspath(__file__)) + os.sep


def get_sims_documents_directory():
    root_path = ""

    root_file = os.path.normpath(os.path.dirname(os.path.realpath(__file__))).replace(os.sep, '/')
    root_file_split = root_file.split('/')

    exit_index = len(root_file_split) - root_file_split.index('Mods')

    for index in range(0, len(root_file_split) - exit_index):
        root_path += str(root_file_split[index]) + '/'

    return root_path
