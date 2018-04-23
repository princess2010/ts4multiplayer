import os

def get_current_user_directory():
    dir = os.path.dirname(os.path.abspath(__file__)) + "/"
    return dir