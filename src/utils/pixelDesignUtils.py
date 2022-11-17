import os
import json


def get_number_of_rocs(phase, sub_system):
    """Return number of ROCs for FPix or BPix.

    Args:
        phase (int)
        sub_system (str): (Pixel)?(Barrel|End[cC]ap) or [FB]Pix
    """

    directory = os.environ["PIXEL_MONITORING_DIR"] + "/config/number_of_rocs"

    if sub_system.startswith("Pixel"):
        sub_system = sub_system[5:]
    if sub_system.lower() == "barrel":
         sub_system = "BPix"
    elif sub_system.lower() in "endcap":
         sub_system = "FPix"

    file_name = "%s/%s/phase%d.json" % (directory, sub_system, phase)
    number_of_rocs = json.load(open(file_name))

    return number_of_rocs


# TODO: This should be double-checked!
# TODO: Should check temperature for Run3
# TODO: Shouldn't we get this value from a database
def get_coolant_temperature_for_fill(fill):
    if fill <= 2351:
        return 7
    elif fill <= 3599 and fill > 2351:
        return 0
    elif fill <= 5575  and fill > 3599:
        return -10
    elif fill > 5575 and fill <= 5900:
        return -20
    else:
        return -22


def get_layer_names(phase):
    if phase == 0:
        names = ["LAY1", "LAY3"]
    elif phase == 1:
        names = ["LAY14", "LAY23"]
    return names


def get_disk_names(phase):
    if phase == 0:
        names = []
    elif phase == 1:
        names = ["D1", "D2", "D3"]
    return names


def get_channel_names():
    names = [
        "channel000",
        "channel001",
        "channel002",
        "channel003",
    ]
    return names


def get_layer_name_from_cable_name(cable_name):
    sub_system = cable_name.split("_")[0]
    if sub_system == "PixelBarrel":
        return cable_name.split("/")[0].split("_")[-1]
    else:
        return cable_name.split("/")[0].split("_")[-2]

