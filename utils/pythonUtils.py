import subprocess


def run_bash_command(bash_command):
    """Returns the output of a bash command.

    Args:
        bash_command (str)

    Returns:
        str
    """

    return subprocess.Popen(bash_command, shell=True, stdout=subprocess.PIPE).stdout.read().decode("utf-8")[:-1]
