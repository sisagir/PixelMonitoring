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


import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import os
import optparse
import copy
from numberOfROCs import *

usage = 'usage: %prog --BarrelorEndCap BarrelOrEndCap --phase Phase'
parser = optparse.OptionParser(usage)
#parser.add_option('-r', '--run', dest='run', type='int', help='Number of the run to analyze')
parser.add_option("","--BarrelOrEndCap",dest="BarrelOrEndCap",type="string",default="Barrel",help="Indicate if you wish to access current informations for BPix or FPix. Allowed choices: Barrel, EndCap.")
parser.add_option("-p","--phase",dest="phase",type="string",default="Phase1",help="Indicate if you wish to access current informations for phase0 or phase1 pixel detector. Allowed choices: phase0, phase1")

(opt, args) = parser.parse_args()


BarrelOrEndCap = opt.BarrelOrEndCap
Phase = opt.phase


print "BarrelOrEndacp? ", BarrelOrEndCap
print "Phase? ", Phase
startFillRaw = raw_input("Enter start fill number: ")
endFillRaw = raw_input("Enter end fill number: ")

startFill = int(startFillRaw)
endFill = int(endFillRaw)

fillNum = startFill


#HV_L3 = {}


while fillNum <= endFill:
    HV_L1 = {}
    HV_L2 = {}
    HV_L3_ch1 = {}
    HV_L3_ch2 = {}
    HV_L3 = {}
    HV_L4 = {}
    analog = {}
    digital = {}


    ### Open file and get bias, analog and digital currents
    #fileCurrents = "txt/" + str(fillNum) + "_" + BarrelOrEndCap + ".txt"
    fileCurrents = "" + str(fillNum) + "_" + BarrelOrEndCap + ".txt"
    if(os.path.exists(fileCurrents)):
        f = open(fileCurrents, "r+")
        lines = f.readlines()
        ### Opening output files
        HVfile_ = "txt/" + str(fillNum) + "_" + BarrelOrEndCap + "_HV_ByLayer.txt"
        anafile_ = "txt/" +  str(fillNum) + "_" + BarrelOrEndCap + "_Ana.txt"
        anafilePerRoc_ = "txt/" +  str(fillNum) + "_" + BarrelOrEndCap + "_AnaPerRoc.txt"
        test_ = "txt/" +  str(fillNum) + "_" + BarrelOrEndCap + "_Test.txt"
        digfile_ = "txt/" + str(fillNum) + "_" + BarrelOrEndCap + "_Dig.txt"


        HVFile = open(HVfile_, "w")
        anaFile = open(anafile_, "w")
        anaFilePerRoc = open(anafilePerRoc_, "w")
        testFile = open(test_, "w")
        digFile = open(digfile_, "w")

        for l in lines:
            line = l.split()
            #print "----->Check: ", line
            sector = line[0].rsplit('/')[0].strip()
            #print "-->Check: ", sector
            current =  line[1]
            if(Phase == "phase0"):
                if "LAY1/channel002" in l:
                    HV_L1[sector] = current
                elif("LAY1/channel003" in l):
                    HV_L2[line[0].rsplit('1/')[0].strip()+ "2"] = current
                elif("LAY3/channel002" in l):
                    HV_L3_ch1[sector] = current
                elif("LAY3/channel003" in l):
                    HV_L3_ch2[sector] = current

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


            if("channel000" in l):

#                print "digital current found"
                digital[sector] = current
#                print  "Digital current: ", digital[sector]
            elif("channel001" in l):
                analog[sector] = current
#                print "analog current found: ", analog[sector]
                #print "for sector: ", sector[:-1]
                #print "i.e. sector: ",sector[:-1] + "2"


        fillNum = fillNum + 1

    else:
        fillNum = fillNum + 1
        print("%s not found. Skipping." % fileCurrents)
        continue

#    print "Keys for analog: ", analog.keys()
    #print "Keys for LAY 3: ", HV_L3.keys()
    #print "Values for LAY 3: ", HV_L3.values()

    if(Phase == "phase0"):
        if(BarrelOrEndCap=="Barrel"): numberOfRocs=copy.deepcopy(numberOfRocsBarrel)
        else: numberOfRocs=numberOfRocsEndCap
        [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L1[k])/float(numberOfRocs[k]) ) + "\n") for k in HV_L1.keys() ]
        [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L2[k])/float(numberOfRocs[k]) ) + "\n") for k in HV_L2.keys() ]
        [HVFile.write(k + " " + str.format("{0:.4f}", (float(HV_L3_ch1[k]) + float(HV_L3_ch2[k]) )/float(numberOfRocs[k]) ) + "\n") for k in HV_L3_ch1.keys() ]
        [digFile.write(k + " " + str.format("{0:.4f}", float(digital[k])) + "\n") for k in digital.keys() ]
        [anaFile.write(k + " " + str.format("{0:.4f}", float(analog[k]) ) + "\n") for k in analog.keys() ]
        [anaFilePerRoc.write(k + " " + str.format("{0:.4f}", float(analog[k])/float(numberOfRocs[k]))  + "\n") if k.endswith("3") else anaFilePerRoc.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(numberOfRocs[k]) + float(numberOfRocs[k[:-1] + "2"])))  + "\n") for k in analog.keys() ]


        HVFile.close()
        digFile.close()
        anaFile.close()
        anaFilePerRoc.close()

    else:
        if(BarrelOrEndCap=="Barrel"): numberOfRocs=numberOfRocsBarrelPhase1
        else: numberOfRocs=numberOfRocsEndCapPhase1
        [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L1[k])/float(numberOfRocs[k]) ) + "\n") for k in HV_L1.keys() ]
        [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L2[k])/float(numberOfRocs[k]) ) + "\n") for k in HV_L2.keys() ]
#        [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L3[k])/float(numberOfRocs[k]) ) + "\n") for k in HV_L3.keys() ]
        for k in HV_L3.keys():
            if(fillNum-1==5730):
                #print "KEY: ", k
                #print "N.of ROCS: ", numberOfRocs[k]
                #print "Current values: ", HV_L3[k]
                current = float(HV_L3[k])/float(numberOfRocs[k])
                #print "Value: ", (k + " " + str.format("{0:.4f}", current ))
            HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L3[k])/float(numberOfRocs[k]) ) + "\n")
        [HVFile.write(k + " " + str.format("{0:.4f}", float(HV_L4[k])/float(numberOfRocs[k]) ) + "\n") for k in HV_L4.keys() ]
        [anaFile.write(k + " " + str.format("{0:.4f}", float(analog[k]) ) + "\n") for k in analog.keys() ]


        for k in analog.keys():
#            print "Key: ", k[:-1]
            if k.endswith("LAY3"):

#                print "analog current per roc: ", (k + " " + str.format("{0:.4f}", float(analog[k])/(float(numberOfRocs[k[:-1] + "2"]) + float(numberOfRocs[k[:-1] + "3"])))  + "\n")
                anaFilePerRoc.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(numberOfRocs[k[:-1] + "2"]) + float(numberOfRocs[k[:-1] + "3"])))  + "\n")
            elif(k.endswith("LAY14")):
 #               print "analog current per roc LAY14: ", (k + " " + str.format("{0:.4f}", float(analog[k])/(float(numberOfRocs[k[:-2] + "1"]) + float(numberOfRocs[k[:-2] + "4"])))  + "\n")
                anaFilePerRoc.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(numberOfRocs[k[:-2] + "1"]) + float(numberOfRocs[k[:-2] + "4"])))  + "\n")

#        [anaFilePerRoc.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(numberOfRocs[k[:-1] + "2"]) + float(numberOfRocs[k[:-1] + "3"])))  + "\n") if k.endswith("LAY3") else anaFilePerRoc.write(k + " " + str.format("{0:.4f}", float(analog[k])/(float(numberOfRocs[k[:-2] + "1"]) + float(numberOfRocs[k[:-2] + "4"])))  + "\n") for k in analog.keys() ]
        [digFile.write(k + " " + str.format("{0:.4f}", float(digital[k])) + "\n") for k in digital.keys() ]

        HVFile.close()
        digFile.close()
        anaFile.close()
        anaFilePerRoc.close()
