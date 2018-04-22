from mp_utils import get_current_user_directory

def output(filename, string):
    return
    with open("{}{}.txt".format(get_current_user_directory(), filename), 'a') as output:
        output.write(str(string) + "\n")

def output_irregardelessly(filename, string):
    # return
    with open("{}{}.txt".format(get_current_user_directory(), filename), 'a') as output:
        output.write(str(string) + "\n")
