import subprocess


def run_bash_command(bash_command):
    """Returns the output of a bash command.

    Args:
        bash_command (str)

    Returns:
        str
    """

    return subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")[:-1]


def read_txt_file(file_name, skip_comments=True):
    lines = open(file_name, "r").read().splitlines()
    if skip_comments:
        lines = [x for x in lines if not x.startswith("#")]
    return lines