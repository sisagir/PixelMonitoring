from functools import reduce
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


def list_to_str(list_, str_for_concatenation=""):
    f = lambda x, y: x + str_for_concatenation + y
    return reduce(f, list_)


def dict_linear_combination(dict1, dict2, a, b, reduce_to_common_keys=False):
    """Returns a * dict1 + b * dict2
    
    Args:
        dict1 (dict): dict with same keys as dict2
        dict2 (dict): dict with same keys as dict1
        a (int, float): dict1 coefficient
        b (int, float): dict2 coefficient
    """

    dict1_keys = set(dict1.keys())
    dict2_keys = set(dict2.keys())
    if dict1_keys != dict2_keys:
        if reduce_to_common_keys:
            keys = dict1_keys.intersection(dict2_keys)
        else:
            print("Error: dict do not have the same keys.")
            exit(1)
    else:
        keys = dict1_keys

    dict_ = {k: a * dict1[k] + b * dict2[k] for k in keys}
    return dict_
