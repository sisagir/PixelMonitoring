
def get_number_of_rocs(phase, sub_system):

    if phase == 0:
        if sub_system == "Barrel": 
            number_of_rocs = {
                "PixelBarrel_BmI_S1_LAY1": 96,
                "PixelBarrel_BmI_S1_LAY2": 96,
                "PixelBarrel_BmI_S1_LAY3": 160,
                "PixelBarrel_BmI_S2_LAY1": 64,
                "PixelBarrel_BmI_S2_LAY2": 128,
                "PixelBarrel_BmI_S2_LAY3": 192,
                "PixelBarrel_BmI_S3_LAY1": 64,
                "PixelBarrel_BmI_S3_LAY2": 128,
                "PixelBarrel_BmI_S3_LAY3": 192,
                "PixelBarrel_BmI_S4_LAY1": 64,
                "PixelBarrel_BmI_S4_LAY2": 128,
                "PixelBarrel_BmI_S4_LAY3": 128,
                "PixelBarrel_BmI_S5_LAY1": 64,
                "PixelBarrel_BmI_S5_LAY2": 128,
                "PixelBarrel_BmI_S5_LAY3": 128,
                "PixelBarrel_BmI_S6_LAY1": 64,
                "PixelBarrel_BmI_S6_LAY2": 128,
                "PixelBarrel_BmI_S6_LAY3": 192,
                "PixelBarrel_BmI_S7_LAY1": 64,
                "PixelBarrel_BmI_S7_LAY2": 128,
                "PixelBarrel_BmI_S7_LAY3": 192,
                "PixelBarrel_BmI_S8_LAY1": 96,
                "PixelBarrel_BmI_S8_LAY2": 96,
                "PixelBarrel_BmI_S8_LAY3": 160,
                "PixelBarrel_BmO_S1_LAY1": 96,
                "PixelBarrel_BmO_S1_LAY2": 96,
                "PixelBarrel_BmO_S1_LAY3": 160,
                "PixelBarrel_BmO_S2_LAY1": 64,
                "PixelBarrel_BmO_S2_LAY2": 128,
                "PixelBarrel_BmO_S2_LAY3": 192,
                "PixelBarrel_BmO_S3_LAY1": 64,
                "PixelBarrel_BmO_S3_LAY2": 128,
                "PixelBarrel_BmO_S3_LAY3": 192,
                "PixelBarrel_BmO_S4_LAY1": 64,
                "PixelBarrel_BmO_S4_LAY2": 128,
                "PixelBarrel_BmO_S4_LAY3": 128,
                "PixelBarrel_BmO_S5_LAY1": 64,
                "PixelBarrel_BmO_S5_LAY2": 128,
                "PixelBarrel_BmO_S5_LAY3": 128,
                "PixelBarrel_BmO_S6_LAY1": 64,
                "PixelBarrel_BmO_S6_LAY2": 128,
                "PixelBarrel_BmO_S6_LAY3": 192,
                "PixelBarrel_BmO_S7_LAY1": 64,
                "PixelBarrel_BmO_S7_LAY2": 128,
                "PixelBarrel_BmO_S7_LAY3": 192,
                "PixelBarrel_BmO_S8_LAY1": 96,
                "PixelBarrel_BmO_S8_LAY2": 96,
                "PixelBarrel_BmO_S8_LAY3": 160,
                "PixelBarrel_BpI_S1_LAY1": 96,
                "PixelBarrel_BpI_S1_LAY2": 96,
                "PixelBarrel_BpI_S1_LAY3": 160,
                "PixelBarrel_BpI_S2_LAY1": 64,
                "PixelBarrel_BpI_S2_LAY2": 128,
                "PixelBarrel_BpI_S2_LAY3": 192,
                "PixelBarrel_BpI_S3_LAY1": 64,
                "PixelBarrel_BpI_S3_LAY2": 128,
                "PixelBarrel_BpI_S3_LAY3": 192,
                "PixelBarrel_BpI_S4_LAY1": 64,
                "PixelBarrel_BpI_S4_LAY2": 128,
                "PixelBarrel_BpI_S4_LAY3": 128,
                "PixelBarrel_BpI_S5_LAY1": 64,
                "PixelBarrel_BpI_S5_LAY2": 128,
                "PixelBarrel_BpI_S5_LAY3": 128,
                "PixelBarrel_BpI_S6_LAY1": 64,
                "PixelBarrel_BpI_S6_LAY2": 128,
                "PixelBarrel_BpI_S6_LAY3": 192,
                "PixelBarrel_BpI_S7_LAY1": 64,
                "PixelBarrel_BpI_S7_LAY2": 128,
                "PixelBarrel_BpI_S7_LAY3": 192,
                "PixelBarrel_BpI_S8_LAY1": 96,
                "PixelBarrel_BpI_S8_LAY2": 96,
                "PixelBarrel_BpI_S8_LAY3": 160,
                "PixelBarrel_BpO_S1_LAY1": 96,
                "PixelBarrel_BpO_S1_LAY2": 96,
                "PixelBarrel_BpO_S1_LAY3": 160,
                "PixelBarrel_BpO_S2_LAY1": 64,
                "PixelBarrel_BpO_S2_LAY2": 128,
                "PixelBarrel_BpO_S2_LAY3": 192,
                "PixelBarrel_BpO_S3_LAY1": 64,
                "PixelBarrel_BpO_S3_LAY2": 128,
                "PixelBarrel_BpO_S3_LAY3": 192,
                "PixelBarrel_BpO_S4_LAY1": 64,
                "PixelBarrel_BpO_S4_LAY2": 128,
                "PixelBarrel_BpO_S4_LAY3": 128,
                "PixelBarrel_BpO_S5_LAY1": 64,
                "PixelBarrel_BpO_S5_LAY2": 128,
                "PixelBarrel_BpO_S5_LAY3": 128,
                "PixelBarrel_BpO_S6_LAY1": 64,
                "PixelBarrel_BpO_S6_LAY2": 128,
                "PixelBarrel_BpO_S6_LAY3": 192,
                "PixelBarrel_BpO_S7_LAY1": 64,
                "PixelBarrel_BpO_S7_LAY2": 128,
                "PixelBarrel_BpO_S7_LAY3": 192,
                "PixelBarrel_BpO_S8_LAY1": 96,
                "PixelBarrel_BpO_S8_LAY2": 96,
                "PixelBarrel_BpO_S8_LAY3": 160,
            }

        elif sub_system == "EndCap":
            number_of_rocs = {
                "PixelEndCap_BmI_D1_ROG1": 135,
                "PixelEndCap_BmI_D1_ROG2": 135,
                "PixelEndCap_BmI_D1_ROG3": 135,
                "PixelEndCap_BmI_D1_ROG4": 135,
                "PixelEndCap_BmI_D2_ROG1": 135,
                "PixelEndCap_BmI_D2_ROG2": 135,
                "PixelEndCap_BmI_D2_ROG3": 135,
                "PixelEndCap_BmI_D2_ROG4": 135,
                "PixelEndCap_BmO_D1_ROG1": 135,
                "PixelEndCap_BmO_D1_ROG2": 135,
                "PixelEndCap_BmO_D1_ROG3": 135,
                "PixelEndCap_BmO_D1_ROG4": 135,
                "PixelEndCap_BmO_D2_ROG1": 135,
                "PixelEndCap_BmO_D2_ROG2": 135,
                "PixelEndCap_BmO_D2_ROG3": 135,
                "PixelEndCap_BmO_D2_ROG4": 135,
                "PixelEndCap_BpI_D1_ROG1": 135,
                "PixelEndCap_BpI_D1_ROG2": 135,
                "PixelEndCap_BpI_D1_ROG3": 135,
                "PixelEndCap_BpI_D1_ROG4": 135,
                "PixelEndCap_BpI_D2_ROG1": 135,
                "PixelEndCap_BpI_D2_ROG2": 135,
                "PixelEndCap_BpI_D2_ROG3": 135,
                "PixelEndCap_BpI_D2_ROG4": 135,
                "PixelEndCap_BpO_D1_ROG1": 135,
                "PixelEndCap_BpO_D1_ROG2": 135,
                "PixelEndCap_BpO_D1_ROG3": 135,
                "PixelEndCap_BpO_D1_ROG4": 135,
                "PixelEndCap_BpO_D2_ROG1": 135,
                "PixelEndCap_BpO_D2_ROG2": 135,
                "PixelEndCap_BpO_D2_ROG3": 135,
                "PixelEndCap_BpO_D2_ROG4": 135,
            }

    elif phase == 1:
        if sub_system == "Barrel": 
            number_of_rocs = {
                "PixelBarrel_BmI_S1_LAY1": 48,
                "PixelBarrel_BmI_S2_LAY1": 48,
                "PixelBarrel_BmI_S3_LAY1": 48,
                "PixelBarrel_BmI_S4_LAY1": 48,
                "PixelBarrel_BmI_S5_LAY1": 48,
                "PixelBarrel_BmI_S6_LAY1": 48,
                "PixelBarrel_BmI_S7_LAY1": 48,
                "PixelBarrel_BmI_S8_LAY1": 48,
                "PixelBarrel_BmO_S1_LAY1": 48,
                "PixelBarrel_BmO_S2_LAY1": 48,
                "PixelBarrel_BmO_S3_LAY1": 48,
                "PixelBarrel_BmO_S4_LAY1": 48,
                "PixelBarrel_BmO_S5_LAY1": 48,
                "PixelBarrel_BmO_S6_LAY1": 48,
                "PixelBarrel_BmO_S7_LAY1": 48,
                "PixelBarrel_BmO_S8_LAY1": 48,
                "PixelBarrel_BpI_S1_LAY1": 48,
                "PixelBarrel_BpI_S2_LAY1": 48,
                "PixelBarrel_BpI_S3_LAY1": 48,
                "PixelBarrel_BpI_S4_LAY1": 48,
                "PixelBarrel_BpI_S5_LAY1": 48,
                "PixelBarrel_BpI_S6_LAY1": 48,
                "PixelBarrel_BpI_S7_LAY1": 48,
                "PixelBarrel_BpI_S8_LAY1": 48,
                "PixelBarrel_BpO_S1_LAY1": 48,
                "PixelBarrel_BpO_S2_LAY1": 48,
                "PixelBarrel_BpO_S3_LAY1": 48,
                "PixelBarrel_BpO_S4_LAY1": 48,
                "PixelBarrel_BpO_S5_LAY1": 48,
                "PixelBarrel_BpO_S6_LAY1": 48,
                "PixelBarrel_BpO_S7_LAY1": 48,
                "PixelBarrel_BpO_S8_LAY1": 48,
                "PixelBarrel_BmI_S1_LAY2": 128,
                "PixelBarrel_BmI_S2_LAY2": 128,
                "PixelBarrel_BmI_S3_LAY2": 64,
                "PixelBarrel_BmI_S4_LAY2": 128,
                "PixelBarrel_BmI_S5_LAY2": 128,
                "PixelBarrel_BmI_S6_LAY2": 64,
                "PixelBarrel_BmI_S7_LAY2": 128,
                "PixelBarrel_BmI_S8_LAY2": 128,
                "PixelBarrel_BmO_S1_LAY2": 128,
                "PixelBarrel_BmO_S2_LAY2": 128,
                "PixelBarrel_BmO_S3_LAY2": 64,
                "PixelBarrel_BmO_S4_LAY2": 128,
                "PixelBarrel_BmO_S5_LAY2": 128,
                "PixelBarrel_BmO_S6_LAY2": 64,
                "PixelBarrel_BmO_S7_LAY2": 128,
                "PixelBarrel_BmO_S8_LAY2": 128,
                "PixelBarrel_BpI_S1_LAY2": 128,
                "PixelBarrel_BpI_S2_LAY2": 128,
                "PixelBarrel_BpI_S3_LAY2": 64,
                "PixelBarrel_BpI_S4_LAY2": 128,
                "PixelBarrel_BpI_S5_LAY2": 128,
                "PixelBarrel_BpI_S6_LAY2": 64,
                "PixelBarrel_BpI_S7_LAY2": 128,
                "PixelBarrel_BpI_S8_LAY2": 128,
                "PixelBarrel_BpO_S1_LAY2": 128,
                "PixelBarrel_BpO_S2_LAY2": 128,
                "PixelBarrel_BpO_S3_LAY2": 64,
                "PixelBarrel_BpO_S4_LAY2": 128,
                "PixelBarrel_BpO_S5_LAY2": 128,
                "PixelBarrel_BpO_S6_LAY2": 64,
                "PixelBarrel_BpO_S7_LAY2": 128,
                "PixelBarrel_BpO_S8_LAY2": 128,
                "PixelBarrel_BmI_S1_LAY3": 128,
                "PixelBarrel_BmI_S2_LAY3": 192,
                "PixelBarrel_BmI_S3_LAY3": 192,
                "PixelBarrel_BmI_S4_LAY3": 192,
                "PixelBarrel_BmI_S5_LAY3": 192,
                "PixelBarrel_BmI_S6_LAY3": 192,
                "PixelBarrel_BmI_S7_LAY3": 192,
                "PixelBarrel_BmI_S8_LAY3": 128,
                "PixelBarrel_BmO_S1_LAY3": 128,
                "PixelBarrel_BmO_S2_LAY3": 192,
                "PixelBarrel_BmO_S3_LAY3": 192,
                "PixelBarrel_BmO_S4_LAY3": 192,
                "PixelBarrel_BmO_S5_LAY3": 192,
                "PixelBarrel_BmO_S6_LAY3": 192,
                "PixelBarrel_BmO_S7_LAY3": 192,
                "PixelBarrel_BmO_S8_LAY3": 128,
                "PixelBarrel_BpI_S1_LAY3": 128,
                "PixelBarrel_BpI_S2_LAY3": 192,
                "PixelBarrel_BpI_S3_LAY3": 192,
                "PixelBarrel_BpI_S4_LAY3": 192,
                "PixelBarrel_BpI_S5_LAY3": 192,
                "PixelBarrel_BpI_S6_LAY3": 192,
                "PixelBarrel_BpI_S7_LAY3": 192,
                "PixelBarrel_BpI_S8_LAY3": 128,
                "PixelBarrel_BpO_S1_LAY3": 128,
                "PixelBarrel_BpO_S2_LAY3": 192,
                "PixelBarrel_BpO_S3_LAY3": 192,
                "PixelBarrel_BpO_S4_LAY3": 192,
                "PixelBarrel_BpO_S5_LAY3": 192,
                "PixelBarrel_BpO_S6_LAY3": 192,
                "PixelBarrel_BpO_S7_LAY3": 192,
                "PixelBarrel_BpO_S8_LAY3": 128,
                "PixelBarrel_BmI_S1_LAY4": 256,
                "PixelBarrel_BmI_S2_LAY4": 256,
                "PixelBarrel_BmI_S3_LAY4": 256,
                "PixelBarrel_BmI_S4_LAY4": 256,
                "PixelBarrel_BmI_S5_LAY4": 256,
                "PixelBarrel_BmI_S6_LAY4": 256,
                "PixelBarrel_BmI_S7_LAY4": 256,
                "PixelBarrel_BmI_S8_LAY4": 256,
                "PixelBarrel_BmO_S1_LAY4": 256,
                "PixelBarrel_BmO_S2_LAY4": 256,
                "PixelBarrel_BmO_S3_LAY4": 256,
                "PixelBarrel_BmO_S4_LAY4": 256,
                "PixelBarrel_BmO_S5_LAY4": 256,
                "PixelBarrel_BmO_S6_LAY4": 256,
                "PixelBarrel_BmO_S7_LAY4": 256,
                "PixelBarrel_BmO_S8_LAY4": 256,
                "PixelBarrel_BpI_S1_LAY4": 256,
                "PixelBarrel_BpI_S2_LAY4": 256,
                "PixelBarrel_BpI_S3_LAY4": 256,
                "PixelBarrel_BpI_S4_LAY4": 256,
                "PixelBarrel_BpI_S5_LAY4": 256,
                "PixelBarrel_BpI_S6_LAY4": 256,
                "PixelBarrel_BpI_S7_LAY4": 256,
                "PixelBarrel_BpI_S8_LAY4": 256,
                "PixelBarrel_BpO_S1_LAY4": 256,
                "PixelBarrel_BpO_S2_LAY4": 256,
                "PixelBarrel_BpO_S3_LAY4": 256,
                "PixelBarrel_BpO_S4_LAY4": 256,
                "PixelBarrel_BpO_S5_LAY4": 256,
                "PixelBarrel_BpO_S6_LAY4": 256,
                "PixelBarrel_BpO_S7_LAY4": 256,
                "PixelBarrel_BpO_S8_LAY4": 256,
            }

        elif sub_system == "EndCap":
            number_of_rocs = {
                "PixelEndCap_BpO_D1": 896,
                "PixelEndCap_BpO_D2": 896,
                "PixelEndCap_BpO_D3": 896,
                "PixelEndCap_BpI_D1": 896,
                "PixelEndCap_BpI_D2": 896,
                "PixelEndCap_BpI_D3": 896,
                "PixelEndCap_BmI_D1": 896,
                "PixelEndCap_BmI_D2": 896,
                "PixelEndCap_BmI_D3": 896,
                "PixelEndCap_BmO_D1": 896,
                "PixelEndCap_BmO_D2": 896,
                "PixelEndCap_BmO_D3": 896,
            }

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

