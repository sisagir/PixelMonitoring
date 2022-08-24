# ****************************************************************
#
#  Authors: Annapaola de Cosa
#           decosa@cern.ch
#           Andrew Johnson
#           andrew.johnson@cern.ch
#           Sept/2015
#
#  Description:
#  This tool reads the output files produced by getCurrentsFromDB.py
#  for a range of lhc fills and produces 3 output files.
#  "_Dig.txt" and "_Ana.txt" files contain the sector/Layer name
#  and analog/digital currents as read from power group.
#  "HV_ByLayer.txt" contains for each sector and layer
#  the average HV current per ROC.
#
#  Usage: python getCurrents.py
# ****************************************************************


import os
import argparse
import copy
from .numberOfROCs import *


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_directory_name",
        help="Input directory containing currents files",
        required=False,
        default="./currents/",
    )
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory name",
        required=False,
        default="./txt/",
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
        "-s", "--sub_detector",
        help="Sub-detector to analyse",
        choices=["Barrel", "EndCap"],
        required=True,
    )
    parser.add_argument(
        "-p", "--phase",
        help="Indicate if you wish to access current informations for"
             "phase0 or phase1 pixel detector.",
        choices=[0, 1],
        type=int,
        default=1,
        required=False,
    )

    return parser.parse_args()


def main(args):

    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    for fill in range(args.first_fill, args.last_fill+1):
        HV_L1 = {}
        HV_L2 = {}
        HV_L3_ch1 = {}
        HV_L3_ch2 = {}
        HV_L3 = {}
        HV_L4 = {}
        analog = {}
        digital = {}


        ### Open file and get bias, analog and digital currents
        currents_file = args.input_directory_name + str(fill) + "_" + args.sub_detector + ".txt"
        if not os.path.exists(currents_file):
            print(("%s not found. Skipping." % currents_file))
            continue

        f = open(currents_file, "r+")
        lines = f.readlines()
        ### Opening output files
        prefix = args.output_directory + str(fill) + "_" + args.sub_detector
        HVfile_ = prefix + "_HV_ByLayer.txt"
        anafile_ = prefix + "_Ana.txt"
        anafilePerRoc_ = prefix + "_AnaPerRoc.txt"
        digfile_ = prefix + "_Dig.txt"


        HVFile = open(HVfile_, "w")
        anaFile = open(anafile_, "w")
        anaFilePerRoc = open(anafilePerRoc_, "w")
        digFile = open(digfile_, "w")

        for l in lines:
            line = l.split()
            sector = line[0].rsplit('/')[0].strip()
            current =  line[1]
            if args.phase == 0:
                if "LAY1/channel002" in l:
                    HV_L1[sector] = current
                elif("LAY1/channel003" in l):
                    HV_L2[line[0].rsplit('1/')[0].strip()+ "2"] = current
                elif("LAY3/channel002" in l):
                    HV_L3_ch1[sector] = current
                elif("LAY3/channel003" in l):
                    HV_L3_ch2[sector] = current
                #else:
                #    print l
                #    raise NotImplementedError

            else:
                if "LAY14/channel002" in l:
                    HV_L1[line[0].rsplit('14/')[0].strip()+ "1"] = current
                elif("LAY14/channel003" in l):
                    HV_L4[line[0].rsplit('14/')[0].strip()+ "4"] = current
                elif("LAY23/channel002" in l):
                    HV_L2[line[0].rsplit('23/')[0].strip()+ "3"] = current
                elif("LAY23/channel003" in l):
                    HV_L3[line[0].rsplit('23/')[0].strip()+ "2"] = current
                elif("_D1_" in l and ("channel002" in l or "channel003" in l)):
                    HV_L1[line[0].rsplit('1_')[0].strip()+ "1"] = current
                elif("_D2_" in l and ("channel002" in l or "channel003" in l)):
                    HV_L2[line[0].rsplit('2_')[0].strip()+ "2"] = current
                elif("_D3_" in l and ("channel002" in l or "channel003" in l)):
                    HV_L3[line[0].rsplit('3_')[0].strip()+ "3"] = current
                #else:
                #    print l
                #    raise NotImplementedError


            if "channel000" in l:
                digital[sector] = current
            elif "channel001" in l:
                analog[sector] = current
            #else:
            #    print l
            #    raise NotImplementedError



        if args.phase == 0:
            if(args.sub_detector=="Barrel"): numberOfRocs=copy.deepcopy(numberOfRocsBarrel)
            else: numberOfRocs=numberOfRocsEndCap
            [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L1[k])/float(numberOfRocs[k]) ) + "\n") for k in list(HV_L1.keys()) ]
            [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L2[k])/float(numberOfRocs[k]) ) + "\n") for k in list(HV_L2.keys()) ]
            for k in list(HV_L3_ch1.keys()):
                HV_L3_ch2[k]
                numberOfRocs[k]
            [HVFile.write(k + " " + str.format("{0:.4f}", (float(HV_L3_ch1[k]) + float(HV_L3_ch2[k]) )/float(numberOfRocs[k]) ) + "\n") for k in list(HV_L3_ch1.keys()) ]
            [digFile.write(k + " " + str.format("{0:.4f}", float(digital[k])) + "\n") for k in list(digital.keys()) ]
            [anaFile.write(k + " " + str.format("{0:.4f}", float(analog[k]) ) + "\n") for k in list(analog.keys()) ]
            [anaFilePerRoc.write(k + " " + str.format("{0:.4f}", float(analog[k])/float(numberOfRocs[k]))  + "\n")
             if k.endswith("3")
             else anaFilePerRoc.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(numberOfRocs[k]) + float(numberOfRocs[k[:-1] + "2"])))  + "\n")
             for k in list(analog.keys())
            ]

        else:
            if(args.sub_detector=="Barrel"): numberOfRocs=numberOfRocsBarrelPhase1
            else: numberOfRocs=numberOfRocsEndCapPhase1
            [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L1[k])/float(numberOfRocs[k]) ) + "\n") for k in list(HV_L1.keys()) ]
            [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L2[k])/float(numberOfRocs[k]) ) + "\n") for k in list(HV_L2.keys()) ]
            for k in list(HV_L3.keys()):
                if(fill-1==5730):
                    current = float(HV_L3[k])/float(numberOfRocs[k])
                HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L3[k])/float(numberOfRocs[k]) ) + "\n")
            [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L4[k])/float(numberOfRocs[k]) ) + "\n") for k in list(HV_L4.keys()) ]
            [anaFile.write(k + " " + str.format("{0:.4f}", float(analog[k]) ) + "\n") for k in list(analog.keys()) ]


            for k in list(analog.keys()):
                if k.endswith("LAY3"):
                    anaFilePerRoc.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(numberOfRocs[k[:-1] + "2"]) + float(numberOfRocs[k[:-1] + "3"])))  + "\n")
                elif(k.endswith("LAY14")):
                    anaFilePerRoc.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(numberOfRocs[k[:-2] + "1"]) + float(numberOfRocs[k[:-2] + "4"])))  + "\n")

            [digFile.write(k + " " + str.format("{0:.4f}", float(digital[k])) + "\n") for k in list(digital.keys()) ]

        HVFile.close()
        digFile.close()
        anaFile.close()
        anaFilePerRoc.close()


if __name__ == "__main__":

    args = __get_arguments()
    main(args)
