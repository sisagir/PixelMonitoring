import os
import argparse

from utils import pixelDesignUtils as designUtl
from utils import eraUtils as eraUtl
from utils import pythonUtils as pyUtl


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_directory_name",
        help="Input directory containing currents files",
        required=False,
        default="./currents/from_database",
    )
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory name",
        required=False,
        default="./currents/processed",
    )
    parser.add_argument(
        "-ff", "--first_fill",
        help="First fill number to analyse",
        type=int,
        required=True,
    )
    parser.add_argument(
        "-lf", "--last_fill",
        help="Last fill number to analyse",
        type=int,
        required=True,
    )
    parser.add_argument(
        "-s", "--sub_system",
        help="Sub-detector to analyse",
        choices=["Barrel", "EndCap"],
        required=True,
    )

    return parser.parse_args()


def main(args):

    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    for fill in range(args.first_fill, args.last_fill+1):

        print(fill)
        phase = eraUtl.get_phase_from_fill(fill)

        # Read input file
        currents_file = args.input_directory_name + "/" + str(fill) + "_" + args.sub_system + ".txt"
        if not os.path.exists(currents_file):
            continue
        lines = pyUtl.read_txt_file(currents_file)

        # Book dictionaries to read currents
        hv_layer1 = {}
        hv_layer2 = {}
        hv_layer3_ch1 = {}
        hv_layer3_ch2 = {}
        hv_layer3 = {}
        hv_layer4 = {}
        analog = {}
        digital = {}

        number_of_rocs = designUtl.get_number_of_rocs(phase, args.sub_system)
        allowed_layers = designUtl.get_layer_names(phase) + designUtl.get_disk_names(phase)

        # Open output files
        prefix = args.output_directory + "/" + str(fill) + "_" + args.sub_system
        hv_currents_file_name = prefix + "_HV_ByLayer.txt"
        analog_currents_file_name = prefix + "_Ana.txt"
        analog_currents_per_roc_file_name = prefix + "_AnaPerRoc.txt"
        digital_currents_file_name = prefix + "_Dig.txt"

        # Open output files
        hv_currents_file = open(hv_currents_file_name, "w")
        analog_currents_file = open(analog_currents_file_name, "w")
        analog_currents_per_roc_file = open(analog_currents_per_roc_file_name, "w")
        digital_currents_file = open(digital_currents_file_name, "w")

        # Fill in output file
        for l in lines:
            line = l.split()
            cable_name = line[0]
            sector = line[0].rsplit('/')[0].strip()
            layer = designUtl.get_layer_name_from_cable_name(cable_name)
            current =  line[1]

            # There are aliases of the sectors names for phase-0 and phase-1
            # which creates problems, get rid of them using allowed_layers.
            if layer not in allowed_layers:
                continue

            if phase == 0:
                if "LAY1/channel002" in l:
                    hv_layer1[sector] = current
                elif("LAY1/channel003" in l):
                    hv_layer2[line[0].rsplit('1/')[0].strip()+ "2"] = current
                elif("LAY3/channel002" in l):
                    hv_layer3_ch1[sector] = current
                elif("LAY3/channel003" in l):
                    hv_layer3_ch2[sector] = current

            else:
                if "LAY14/channel002" in l:
                    hv_layer1[line[0].rsplit('14/')[0].strip()+ "1"] = current
                elif("LAY14/channel003" in l):
                    hv_layer4[line[0].rsplit('14/')[0].strip()+ "4"] = current
                elif("LAY23/channel002" in l):
                    hv_layer2[line[0].rsplit('23/')[0].strip()+ "3"] = current
                elif("LAY23/channel003" in l):
                    hv_layer3[line[0].rsplit('23/')[0].strip()+ "2"] = current
                elif("_D1_" in l and ("channel002" in l or "channel003" in l)):
                    hv_layer1[line[0].rsplit('1_')[0].strip()+ "1"] = current
                elif("_D2_" in l and ("channel002" in l or "channel003" in l)):
                    hv_layer2[line[0].rsplit('2_')[0].strip()+ "2"] = current
                elif("_D3_" in l and ("channel002" in l or "channel003" in l)):
                    hv_layer3[line[0].rsplit('3_')[0].strip()+ "3"] = current

            if "channel000" in l:
                digital[sector] = current
            elif "channel001" in l:
                analog[sector] = current


        if phase == 0:
            [hv_currents_file.write(k + " " + str.format("{0:.4f}", float(hv_layer1[k])/float(number_of_rocs[k]) ) + "\n") for k in hv_layer1.keys() ]
            [hv_currents_file.write(k + " " + str.format("{0:.4f}", float(hv_layer2[k])/float(number_of_rocs[k]) ) + "\n") for k in hv_layer2.keys() ]
            [hv_currents_file.write(k + " " + str.format("{0:.4f}", (float(hv_layer3_ch1[k]) + float(hv_layer3_ch2[k]) )/float(number_of_rocs[k]) ) + "\n") for k in hv_layer3_ch1.keys() ]
            [digital_currents_file.write(k + " " + str.format("{0:.4f}", float(digital[k])) + "\n") for k in digital.keys() ]
            [analog_currents_file.write(k + " " + str.format("{0:.4f}", float(analog[k]) ) + "\n") for k in analog.keys() ]
            [analog_currents_per_roc_file.write(k + " " + str.format("{0:.4f}", float(analog[k])/float(number_of_rocs[k]))  + "\n")
             if k.endswith("3")
             else analog_currents_per_roc_file.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(number_of_rocs[k]) + float(number_of_rocs[k[:-1] + "2"])))  + "\n")
             for k in analog.keys()
            ]

        else:
            [hv_currents_file.write(k + " " + str.format("{0:.4f}", float(hv_layer1[k])/float(number_of_rocs[k]) ) + "\n") for k in hv_layer1.keys() ]
            [hv_currents_file.write(k + " " + str.format("{0:.4f}", float(hv_layer2[k])/float(number_of_rocs[k]) ) + "\n") for k in hv_layer2.keys() ]
            for k in hv_layer3.keys():
                if(fill-1==5730):
                    current = float(hv_layer3[k])/float(number_of_rocs[k])
                hv_currents_file.write(k + " " + str.format("{0:.4f}", float(hv_layer3[k])/float(number_of_rocs[k]) ) + "\n")
            [hv_currents_file.write(k + " " + str.format("{0:.4f}", float(hv_layer4[k])/float(number_of_rocs[k]) ) + "\n") for k in hv_layer4.keys() ]
            [analog_currents_file.write(k + " " + str.format("{0:.4f}", float(analog[k]) ) + "\n") for k in analog.keys() ]


            for k in analog.keys():
                if k.endswith("LAY3"):
                    analog_currents_per_roc_file.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(number_of_rocs[k[:-1] + "2"]) + float(number_of_rocs[k[:-1] + "3"])))  + "\n")
                elif(k.endswith("LAY14")):
                    analog_currents_per_roc_file.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(number_of_rocs[k[:-2] + "1"]) + float(number_of_rocs[k[:-2] + "4"])))  + "\n")

            [digital_currents_file.write(k + " " + str.format("{0:.4f}", float(digital[k])) + "\n") for k in digital.keys() ]

        hv_currents_file.close()
        digital_currents_file.close()
        analog_currents_file.close()
        analog_currents_per_roc_file.close()

        for file_name in (hv_currents_file_name, analog_currents_file_name,
                          analog_currents_per_roc_file_name, digital_currents_file_name):
            print("%s has been saved." % file_name)
        print("")


if __name__ == "__main__":

    args = __get_arguments()
    main(args)
