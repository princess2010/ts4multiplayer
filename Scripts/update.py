from config import user_directory

def output(filename, string):
    # return
    with open("{}{}.txt".format(user_directory, filename), 'a') as output:
        output.write(str(string) + "\n")

def output_irregardelessly(filename, string):
    # return
    with open("{}{}.txt".format(user_directory, filename), 'a') as output:
        output.write(str(string) + "\n")
