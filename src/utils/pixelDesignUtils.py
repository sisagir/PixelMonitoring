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
        names = ["LYR1", "LYR3"]
    elif phase == 1:
        names = ["LYR14", "LYR23"]
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
        return cable_name.split("/")[0].split("_")[-1].replace("LAY", "LYR")
    else:
        return cable_name.split("/")[0].split("_")[-2]


def get_readout_group_name_from_omds_leakage_current_cable_name(omds_channel_name, phase=1):
    """Get readout group name from OMDS database channel name.

    Args:
        omds_channel_name (str): e.g. PixelBarrel_BmI_S4_LAY14/channel002
        phase (int): Pixel phase number
    
    Returns:
        str
    """

    if phase != 1:
        raise NotImplementedError

    db_readout_group_name, db_channel_name = omds_channel_name.split("/")
    db_sub_system_name = db_readout_group_name.split("_")[0]
    db_channel = db_channel_name[-1]

    if db_sub_system_name == "PixelBarrel":
        _, half_cylinder, db_sector, db_layer = db_readout_group_name.split("_")
        sector = db_sector.replace("S", "")
        db_layer = db_layer.replace("LAY", "")
        if db_layer == "14":
            if db_channel == "2":
                layer = "1"
            elif db_channel == "3":
                layer = "4"
            else:
                raise ValueError(f"Invalid OMDS channel name {omds_channel_name}")

        elif db_layer == "23":
            if db_channel == "2":
                layer = "3"
            elif db_channel == "3":
                layer = "2"
            else:
                raise ValueError(f"Invalid OMDS channel name {omds_channel_name}")

        else:
            raise ValueError(f"Invalid layer name in OMDS channel name {omds_channel_name}")
        
        readout_group_name = "BPix_%s_SEC%s_LYR%s" % (
                           half_cylinder,
                           sector,
                           layer,
                       )

    elif db_sub_system_name == "PixelEndCap":
        # TODO
        # example: PixelEndCap_BpO_D3_ROG1/channel003
        #_, half_cylinder, db_disk, db_rog = readout_group_name.split("_")
        raise NotImplementedError

    else:
        raise ValueError(f"Invalid sub-system in OMDS channel name {omds_channel_name}")

    return readout_group_name



def get_omds_readout_group_name_from_readout_group_name(readout_group_name, phase=1):

    if phase != 1:
        raise NotImplementedError

    sub_system = readout_group_name.split("_")[0]
    if sub_system == "BPix":
        _, half_cylinder, sector, layer = readout_group_name.split("_")
        db_sector = sector.replace("SEC", "")
        layer = layer[-1]
        if layer == "1":
            db_layer   = "14"
        elif layer == "2":
            db_layer   = "23"
        elif layer == "3":
            db_layer   = "23"
        elif layer == "4":
            db_layer   = "14"
        else:
            raise ValueError(f"Invalid readout group name {readout_group_name}")
        
        omds_name = "PixelBarrel_%s_S%s_LAY%s" % (
                           half_cylinder,
                           db_sector,
                           db_layer,
                       )

    elif sub_system == "FPix":
        raise NotImplementedError

    return omds_name


def get_omds_leakage_current_cable_name_from_readout_group_name(readout_group_name, phase=1):

    if phase != 1:
        raise NotImplementedError

    sub_system = readout_group_name.split("_")[0]
    if sub_system == "BPix":
        _, _, _, layer = readout_group_name.split("_")
        layer = layer[-1]
        if layer in ("1", "3"):
            db_channel = "2"
        elif layer in ("2", "4"):
            db_channel = "3"
        else:
            raise ValueError(f"Invalid readout group name {readout_group_name}")
        
        omds_readout_name = get_omds_readout_group_name_from_readout_group_name(readout_group_name)
        channel_name = "%s/channel00%s" % (omds_readout_name, db_channel)

    elif sub_system == "FPix":
        raise NotImplementedError

    else:
        raise ValueError(f"Invalid module name {readout_group_name}")

    return channel_name


def get_omds_hv_cable_name_from_readout_group_name(readout_group_name, phase=1):
    """Get OMDS database channel name from readout group name.

    Args:
        readout_group_name (str): e.g. BPix_BmI_SEC4_LYR1
        phase (int): Pixel phase number
    
    Returns:
        str
    """

    if phase != 1:
        raise NotImplementedError

    sub_system = readout_group_name.split("_")[0]
    if sub_system == "BPix":
        _, _, _, layer = readout_group_name.split("_")
        layer = layer[-1]
        if layer in ("1", "3"):
            db_channel = "1"
        elif layer in ("2", "4"):
            db_channel = "2"
        else:
            raise ValueError(f"Invalid readout group name {readout_group_name}")
        
        omds_readout_name = get_omds_readout_group_name_from_readout_group_name(readout_group_name)
        channel_name = "%s/HV%s" % (omds_readout_name, db_channel)

    elif sub_system == "FPix":
        raise NotImplementedError

    else:
        raise ValueError(f"Invalid module name {readout_group_name}")

    return channel_name
