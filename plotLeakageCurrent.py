from pathlib import Path
import math
import argparse 

import numpy as np
import ROOT

from utils import eraUtils as eraUtl
from utils import pixelDesignUtils as designUtl
from utils import generalUtils as gUtl
from constants import *


ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetOptFit(0o001)


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_fills_file_name",
        help="Fills file",
        required=False,
        default="fills_info/fills.csv",
    )
    parser.add_argument(
        "-l", "--input_lumi_file_name",
        help="Luminosity file",
        required=False,
        default="fills_info/integrated_luminosity_per_fill.csv",
    )
    parser.add_argument(
        "-c", "--input_currents_directory",
        help="Currents directory",
        required=False,
        default="./txt",
    )
    parser.add_argument(
        "-b", "--bad_fills_file_name",
        help="Bad fills file",
        required=False,
        default="fills_info/bad_fills.txt",
    )
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory name",
        required=False,
        default="./plots/leakage_current",
    )
    parser.add_argument(
        "-ff", "--first_fill",
        help="First fill number to analyse",
        type=int,
        required=False,
    )
    parser.add_argument(
        "-lf", "--last_fill",
        help="Last fill number to analyse",
        type=int,
        required=False,
    )
    parser.add_argument(
        "-era", "--era",
        help="Era to analyse",
        required=False,
    ),
    parser.add_argument(
        "-s", "--sub_detector",
        help="Sub-detector to analyse",
        choices=["Barrel", "EndCap"],
        required=True,
    )

    return parser.parse_args()


def __do_sanity_checks(args):
    assert (args.first_fill and args.last_fill) or args.era
    assert (args.first_fill and args.last_fill) != args.era


### Function translating ROC average current in Leakage current @ degrees C
def __get_leakage_current(I, T):
    I_vol = I/rocVol
    #print "Average current per ROC: ", I
    a = -Eg/(2*kb)
    b =  (1./Tref) - (1./T)
    expo = a * b
    IatZero = I_vol * math.pow(Tref/T, 2) *math.exp(expo)
#    return I_vol#IatZero
    return IatZero


class Current:
    pass


# *********************************************************************
# Currents per Layer                                                  
#
# Get the sum of the currents/ROC for each layer for each fill number
#
# *********************************************************************


def __get_currents_per_layer(sub_detector, fills, currents_directory):
    currents = {}

    for fill in fills:

        T_coolant = designUtl.get_coolant_temperature_for_fill(fill)
        ### Sensor temperature in Kelvin
        T_sensor = T_coolant + T_diff + Kfact
        #print "Sensor Temperature: ", T_sensor
        filename = currents_directory + "/" + str(fill) + "_" + sub_detector + "_HV_ByLayer.txt"
        f = open(filename, 'r+')
        I = Current()
        I.i_roc_layer1 = 0.
        I.i_roc_layer2 = 0.
        I.i_roc_layer3 = 0.
        I.i_roc_layer4 = 0.
        I.nLay1 = 0
        I.nLay2 = 0
        I.nLay3 = 0
        I.nLay4 = 0
        for row in f.readlines():
            if "LAY1" in row :
                I.i_roc_layer1 += float(row.rsplit('LAY1 ')[1])
                I.nLay1+=1
            elif "LAY2" in row :
                I.i_roc_layer2 += float(row.rsplit('LAY2 ')[1])
                I.nLay2+=1
            elif "LAY3" in row :
                I.i_roc_layer3 += float(row.rsplit('LAY3 ')[1])
                I.nLay3+=1
            elif "LAY4" in row :
                I.i_roc_layer4 += float(row.rsplit('LAY4 ')[1])
                I.nLay4+=1
            elif "D1" in row :
                I.i_roc_layer1 += float(row.rsplit('D1 ')[1])
                I.nLay1+=1
            elif "D2" in row :
                I.i_roc_layer2 += float(row.rsplit('D2 ')[1])
                I.nLay2+=1
            elif "D3" in row :
                I.i_roc_layer3 += float(row.rsplit('D3 ')[1])
                I.nLay3+=1

        I.i_leak_layer1 = __get_leakage_current(I.i_roc_layer1, T_sensor)
        I.i_leak_layer2 = __get_leakage_current(I.i_roc_layer2, T_sensor)
        I.i_leak_layer3 = __get_leakage_current(I.i_roc_layer3, T_sensor)
        I.i_leak_layer4 = __get_leakage_current(I.i_roc_layer4, T_sensor)

        if(I.nLay1!=0):I.i_leak_layer1 /= I.nLay1
        if(I.nLay2!=0):I.i_leak_layer2 /= I.nLay2
        if(I.nLay3!=0):I.i_leak_layer3 /= I.nLay3
        if(I.nLay4!=0):I.i_leak_layer4 /= I.nLay4

        currents[str(fill)]= I

        if currents[str(fill)].i_leak_layer1>200 and I.i_leak_layer2 >200 and I.i_leak_layer3 >200 and I.i_leak_layer4 >200 and fill > 2000 and fill < 2500:
            print("Fill " + str(fill) + "has current > 200\n")

    return currents

# *********************************************************************
# Analog and Digital currents per group                                                  
#
# Get the sum of the currents/ROC for each layer for each fill number
#
# *********************************************************************




def __get_analog_and_digital_currents(sub_detector, fills, curType, currents_directory):
    currents = {}
    for fill in fills:
        filename = currents_directory + "/" + str(fill) + "_" + sub_detector + "_"+curType+".txt"
        f = open(filename, 'r+')
        I = Current()
        I.Ana_layer14 = 0.
        I.Ana_layer3 = 0.
        nLay14=0
        nLay23=0
        #print "===>We are in fill number: ", str(fill)
        for row in f.readlines():
            if "layer14" in row:

                I.Ana_layer14 += float(row.rsplit('LAY14 ')[1])
                nLay14+=1
                #print "Found analog current for layer14: ", I.Ana_layer14
            elif "layer3" in row:
                I.Ana_layer3 += float(row.rsplit('LAY3 ')[1])
                nLay23+=1

        if(nLay14!=0): I.Ana_layer14 /= nLay14
        if(nLay23!=0): I.Ana_layer3 /= nLay23
        currents[str(fill)]= I
        #print "Current = ", currents[str(fill)]

    #print "===>Checking current values for Iana: ", currents
    return  currents


# *********************************************************************
# Currents vs Phi                                                  
#
# Get the sum of the currents/ROC vs Phi for each fill number
#
# *********************************************************************


def __get_currents_vs_phi(sub_detector, fill, currents_directory, z="m"):

    T_coolant = designUtl.get_coolant_temperature_for_fill(fill)
    ### Sensor temperature in Kelvin
    T_sensor = T_coolant + T_diff + Kfact

    #print "Fill number: ", fill
    #print "Sensor Temperature: ", T_sensor
    filename = currents_directory + "/" + str(fill) + "_" + sub_detector + "_HV_ByLayer.txt"
    f = open(filename, 'r+')
    phiMod = {"S1_O": 0., "S2_O": 0., "S3_O": 0., "S4_O": 0., "S5_O": 0., "S6_O": 0., "S7_O": 0., "S8_O": 0., "S1_I": 0., "S2_I": 0., "S3_I": 0., "S4_I": 0., "S5_I": 0., "S6_I": 0., "S7_I": 0., "S8_I": 0.,}

    nLay1 = 0
    mapCurr = {}
    for k in list(phiMod.keys()):
        mapCurr[k] = []

    for row in f.readlines():
        if ("layer1" in row ):
            if("BpI" not in row):
                r = row.split('_')
                key = r[2] + "_" + r[1][2]
                zSide =  r[1][1]
                if(zSide == z):mapCurr[key].append(__get_leakage_current(float(row.rsplit('LAY1 ')[1]), T_sensor))

    for k in  list(mapCurr.keys()):
        if(len(mapCurr[k])!=0):phiMod[k] = sum(mapCurr[k])/len(mapCurr[k])
        else:phiMod[k]

    #print "PhiMod ====> ",phiMod
    return phiMod


def __add_dict(dict1, dict2):
    phiMod = {}
    for k in list(dict1.keys()):
        phiMod[k] = dict2[k] - dict1[k]
            
    return phiMod

        
def __plot_azimuth(fills, z="m"):

    x_label = "Fill Number"
    y_label = "Leakage current I [#mu A / cm^{3}]"

    outFill = fills[-1]
    #print "Last fill: ", outFill
    inFill = fills[0]
    #print "First fill: ", inFill
    phiDict2 = __get_currents_vs_phi(outFill,z)
    # print "1st set: ", phiDict2
    phiDict1 = __get_currents_vs_phi(inFill,z)
    # print "2nd set: ", phiDict1
    # print "First fill: ", inFill
    # print "Last fill: ", outFill
    phiMod =  __add_dict(phiDict1, phiDict2)
    #print "--->Difference: ", phiMod
    phi_ = 22.5
    phi0_ = 11.25
    phi = []
    I_phi = []
    slices = ["S4_I", "S3_I", "S2_I", "S1_I", "S1_O", "S2_O", "S3_O", "S4_O", "S5_O", "S6_O", "S7_O", "S8_O", "S8_I", "S7_I", "S6_I", "S5_I"]
    i = 0
    for s in slices:
        phi.append((phi0_ + i*phi_)*ROOT.TMath.DegToRad())
        #print "phi: ", phi0_ + i*phi_
        I_phi.append(phiMod[s])
        #print "phiMod: ",phiMod[s]
        #print 
        i+=1
        
    g1 = gUtl.get_graph(phi, I_phi, x_label, y_label, "Layer 1")
    colour = ROOT.kRed+1
    if(z =="m"): colour = ROOT.kBlack
    g1.SetLineColor(colour)
    g1.SetMarkerColor(colour)
    g1.SetMarkerStyle(22)
    g1.SetMarkerSize(0.8)
    g1.GetXaxis().SetTitle("#Phi")
    g1.GetYaxis().SetTitle("I_{leak} [#mu A / cm^{3}]")
#    g1.GetYaxis().SetTitle("I_{leak} [#mu A / cm^{3}] (corr. to 0#circC)")
   # for i in xrange(len(phi)):
    #    b =  g1.GetXaxis().FindBin(phi[i])
    #    g1.GetXaxis().SetBinLabel(b, slices[i])
    return g1


# TODO: Check if this old function is really obsolete or not

# def __plot_currents(currents, fills, plotType="Leakage"):

#     fill_array = array('f', fills)
#     if(plotType=="Leakage"):
#         i_leak_L1_array = array('f',  [currents[str(f)].i_leak_layer1 for f in fills])
#         i_leak_L2_array = array('f',  [currents[str(f)].i_leak_layer2 for f in fills])
#         i_leak_L3_array = array('f',  [currents[str(f)].i_leak_layer3 for f in fills])
#         i_leak_L4_array = array('f',  [currents[str(f)].i_leak_layer4 for f in fills])
#     elif(plotType=="ROC"):
#         i_leak_L1_array = array('f',  [currents[str(f)].i_roc_layer1 for f in fills])
#         i_leak_L2_array = array('f',  [currents[str(f)].i_roc_layer2 for f in fills])
#         i_leak_L3_array = array('f',  [currents[str(f)].i_roc_layer3 for f in fills])
#         i_leak_L4_array = array('f',  [currents[str(f)].i_roc_layer4 for f in fills])
#     elif(plotType=="DI"):
#         i_leak_L1_array = array('f',  [(currents[str(f)].i_leak_layer1 - currents[str(fills[0])].i_leak_layer1) for f in fills])
#         i_leak_L2_array = array('f',  [(currents[str(f)].i_leak_layer2 - currents[str(fills[0])].i_leak_layer2) for f in fills])
#         i_leak_L3_array = array('f',  [(currents[str(f)].i_leak_layer3 - currents[str(fills[0])].i_leak_layer3) for f in fills])
#         i_leak_L4_array = array('f',  [(currents[str(f)].i_leak_layer4 - currents[str(fills[0])].i_leak_layer4) for f in fills])
#     elif(plotType=="DeltaROC"):
#         print("DIROC")
#         i_leak_L1_array = array('f',  [(currents[str(f)].i_roc_layer1 - currents[str(fills[0])].i_roc_layer1) for f in fills])
#         i_leak_L2_array = array('f',  [(currents[str(f)].i_roc_layer2 - currents[str(fills[0])].i_roc_layer2) for f in fills])
#         i_leak_L3_array = array('f',  [(currents[str(f)].i_roc_layer3 - currents[str(fills[0])].i_roc_layer3) for f in fills])
#         i_leak_L4_array = array('f',  [(currents[str(f)].i_roc_layer4 - currents[str(fills[0])].i_roc_layer4) for f in fills])
 
 
#     i_leak = ROOT.TMultiGraph("mg", "")
#     g1 = __get_graph(i_leak_L1_array,fill_array, "Layer 1")
#     g1.SetLineColor(ROOT.kTeal+4)
#     g1.SetMarkerColor(ROOT.kTeal+4)
#     g1.SetMarkerStyle(22)
#     g1.SetMarkerSize(0.8)
#     #g1.Fit("pol1", "F");

#     g2 = __get_graph(i_leak_L2_array,fill_array, "Layer 2")
#     g2.SetLineColor(ROOT.kRed+1)
#     g2.SetMarkerColor(ROOT.kRed+1 )
#     g2.SetMarkerStyle(22)
#     g2.SetMarkerSize(0.8)
#     #g2.Fit("pol1", "F");
    
#     g3 = __get_graph(i_leak_L3_array,fill_array, "Layer 3")
#     g3.SetLineColor(ROOT.kBlue+2)
#     g3.SetMarkerStyle(22)
#     g3.SetMarkerColor(ROOT.kBlue+2)
#     g3.SetMarkerSize(0.8)

#     g4 = __get_graph(i_leak_L4_array,fill_array, "Layer 4")
#     g4.SetLineColor(ROOT.kBlack)
#     g4.SetMarkerStyle(22)
#     g4.SetMarkerColor(ROOT.kBlack)
#     g4.SetMarkerSize(0.8)


#     #g3.Fit("pol1", "F");
#     i_leak.Add(g1)
#     i_leak.Add(g2)
#     i_leak.Add(g3)
#     i_leak.Add(g4)
#     return i_leak


def __mask_low_currents(currents):
    n = len(currents)
    n_ranges = n // 20
    ranges = np.linspace(0, n, n_ranges)
    mask = np.array([], dtype=bool)
    for r in zip(ranges[:-1], ranges[1:]):
        currents_this_range = currents[math.ceil(r[0]):math.ceil(r[1])]
        mask_this_range = currents_this_range > 0.1 * currents_this_range[currents_this_range > 0].mean()
        mask = np.concatenate((mask, mask_this_range), axis=0)
    return mask, currents[mask]


def __get_multi_graph(sub_detector, era, fluence, currents, fills, integrated_lumi_per_fill, plotType, Xaxis, min_current=0):

    x_label = "Fill Number"
    y_label = "Leakage current I [#mu A / cm^{3}]"

    lumi = np.array([integrated_lumi_per_fill[fill] for fill in fills])
    if Xaxis == "lumi":
        x_L1 = lumi
        x_L2 = lumi
        x_L3 = lumi
        x_L4 = lumi
    elif Xaxis=="fluence": 
        x_L1 = fluence["L1"] * lumi
        x_L2 = fluence["L2"] * lumi
        x_L3 = fluence["L3"] * lumi
        x_L4 = lumi
        # x_L4 = fluence["L4"] * lumi  # TODO: why no number for L4?!

    if(plotType=="Leakage"):
        y_L1 = np.array([currents[str(f)].i_leak_layer1 for f in fills])
        y_L2 = np.array([currents[str(f)].i_leak_layer2 for f in fills])
        y_L3 = np.array([currents[str(f)].i_leak_layer3 for f in fills])
        y_L4 = np.array([currents[str(f)].i_leak_layer4 for f in fills])
    elif(plotType=="ROC"):
        y_L1 = np.array([currents[str(f)].i_roc_layer1 for f in fills])
        y_L2 = np.array([currents[str(f)].i_roc_layer2 for f in fills])
        y_L3 = np.array([currents[str(f)].i_roc_layer3 for f in fills])
        y_L4 = np.array([currents[str(f)].i_roc_layer4 for f in fills])
    elif(plotType=="DI"):
        y_L1 = np.array([(currents[str(f)].i_leak_layer1 - currents[str(fills[0])].i_leak_layer1) for f in fills])
        y_L2 = np.array([(currents[str(f)].i_leak_layer2 - currents[str(fills[0])].i_leak_layer2) for f in fills])
        y_L3 = np.array([(currents[str(f)].i_leak_layer3 - currents[str(fills[0])].i_leak_layer3) for f in fills])
        y_L4 = np.array([(currents[str(f)].i_leak_layer4 - currents[str(fills[0])].i_leak_layer4) for f in fills])
    elif(plotType=="DeltaROC"):
        y_L1 = np.array([(currents[str(f)].i_roc_layer1 - currents[str(fills[0])].i_roc_layer1) for f in fills])
        y_L2 = np.array([(currents[str(f)].i_roc_layer2 - currents[str(fills[0])].i_roc_layer2) for f in fills])
        y_L3 = np.array([(currents[str(f)].i_roc_layer3 - currents[str(fills[0])].i_roc_layer3) for f in fills])
        y_L4 = np.array([(currents[str(f)].i_roc_layer4 - currents[str(fills[0])].i_roc_layer4) for f in fills])
    elif(plotType.startswith("Analog") or plotType=="Digital"):
        y_L1 = np.array([currents[str(f)].Ana_layer14  for f in fills])
        y_L2 = np.array([])
        #print "currents: ", y_L1
        y_L3 = np.array([currents[str(f)].Ana_layer3 for f in fills])
        y_L4 = np.array([])

    mask_L1, y_L1 = __mask_low_currents(y_L1)
    mask_L2, y_L2 = __mask_low_currents(y_L2)
    mask_L3, y_L3 = __mask_low_currents(y_L3)
    mask_L4, y_L4 = __mask_low_currents(y_L4)

    x_L1 = x_L1[mask_L1]
    x_L2 = x_L2[mask_L2]
    x_L3 = x_L3[mask_L3]
    x_L4 = x_L4[mask_L4]

    i_leak_lumi = ROOT.TMultiGraph("mg", "")
    
    g1 = gUtl.get_graph(x_L1, y_L1, x_label, y_label, "Layer 1")
    g1.SetLineColor(ROOT.kTeal+4)
    g1.SetMarkerColor(ROOT.kTeal+4)
    g1.SetMarkerStyle(22)
    g1.SetMarkerSize(0.8)

    FitHisto1 = ROOT.TF1("f1", "[0] +[1]*x", 29100, 30000)
    # FitHisto.SetParLimits(0, 400, 600)
    # FitHisto.SetParLimits(1, 0.09, 0.1)
    #g1.Fit("f1");
    #g1.Fit("pol1", "F");
    # print "Layer1: "
    #print "p0: ", FitHisto1.GetParameter(0)
    #print "p1: ", FitHisto1.GetParameter(1)
    i_leak_lumi.Add(g1)
    
    if(not plotType.startswith("Analog") and plotType!="Digital"):
        g2 = gUtl.get_graph(x_L2, y_L2, x_label, y_label, "Layer 2")
        g2.SetLineColor(ROOT.kBlue+2)
        g2.SetMarkerColor(ROOT.kBlue+2)
        g2.SetMarkerStyle(22)
        g2.SetMarkerSize(0.8)
        FitHisto2 = ROOT.TF1("f2", "[0] +[1]*x", 29100, 30000)
        #g2.Fit("f2");
        #print "Layer2: "
        #print "p0: ", FitHisto2.GetParameter(0)
        #print "p1: ", FitHisto2.GetParameter(1)
        i_leak_lumi.Add(g2)

    g3 = gUtl.get_graph(x_L3, y_L3, x_label, y_label, "Layer 2 & 3")
    if(not plotType.startswith("Analog") and plotType!="Digital"): g3.SetName("Layer 3")
    g3.SetLineColor(ROOT.kRed+1)
    g3.SetMarkerStyle(22)
    g3.SetMarkerColor(ROOT.kRed+1)
    g3.SetMarkerSize(0.8)
    FitHisto3 = ROOT.TF1("f3", "[0] +[1]*x", 29100, 30000)
    #g3.Fit("f3");
    #print "Layer3: "
    #print "p0: ", FitHisto3.GetParameter(0)
    #print "p1: ", FitHisto3.GetParameter(1)
    i_leak_lumi.Add(g3)


    if(not plotType.startswith("Analog") and plotType!="Digital"):
        if (sub_detector != "Barrel" and era !="2016"): 
            g4 = gUtl.get_graph(x_L4, y_L4, x_label, y_label, "Layer 4")
            g4.SetLineColor(ROOT.kBlack+1)
            g4.SetMarkerStyle(22)
            g4.SetMarkerColor(ROOT.kBlack+1)
            g4.SetMarkerSize(0.8)
            FitHisto4 = ROOT.TF1("f4", "[0] +[1]*x", 29100, 30000)
            i_leak_lumi.Add(g4) #sleontsi

    return i_leak_lumi


def __plot_currents(output_directory, sub_detector, settings, currents, fluence, 
                    fills, integrated_lumi_per_fill, curTypeObj, Xaxis, era,
                    text):
    ### curTypeObj is an element of settings, i.e. a tuple

    c = ROOT.TCanvas(settings["base_output_file_name"].strip(".pdf"))
    c.cd()
    legEdges = settings["legend_coordinates"]
    leg = ROOT.TLegend(legEdges[0], legEdges[1], legEdges[2], legEdges[3])
    ROOT.SetOwnership(leg,0)
     
 
    I = __get_multi_graph(sub_detector, era, fluence, currents, fills, 
                          integrated_lumi_per_fill, curTypeObj, Xaxis)
    ROOT.SetOwnership(I,0)
    I.Draw("AP")
    if (Xaxis=="lumi"):
        I.GetXaxis().SetTitle("Integrated Luminosity [fb^{-1}]")
    elif (Xaxis=="fill"):
        I.GetXaxis().SetTitle("Fill number")
    elif (Xaxis=="fluence"):
        I.GetXaxis().SetTitle("Total fluence #Phi [1 MeV Neu Eq.]")
    I.GetYaxis().SetTitle(settings["y_label"])
    I.GetYaxis().SetTitleOffset(1.3)
    I.GetYaxis().SetRangeUser(settings["y_range"][0], settings["y_range"][1])
  
    leg.SetNColumns(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetBorderSize(0)

    nLayers = I.GetListOfGraphs().GetSize()
    print("How many layers? ", nLayers)

    if(nLayers==2):
        if(sub_detector == "EndCap"):
            leg.AddEntry(I.GetListOfGraphs()[0], "Disk 1","P")
            leg.AddEntry(I.GetListOfGraphs()[1], "Disk 2","P")
        else:
            leg.AddEntry(I.GetListOfGraphs()[0], "Layers 1 & 4","P")
            leg.AddEntry(I.GetListOfGraphs()[1], "Layers 2 & 3","P")
    if(nLayers==3):
        if(sub_detector == "EndCap"):
            leg.AddEntry(I.GetListOfGraphs()[0], "Disk 1","P")
            leg.AddEntry(I.GetListOfGraphs()[1], "Disk 2","P")
            leg.AddEntry(I.GetListOfGraphs()[2], "Disk 3","P")
        else:
            leg.AddEntry(I.GetListOfGraphs()[0], "Layer 1","P")
            leg.AddEntry(I.GetListOfGraphs()[1], "Layer 2","P")
            leg.AddEntry(I.GetListOfGraphs()[2], "Layer 3","P")
    if(nLayers==4 and sub_detector == "Barrel" and era!="2016"):
        leg.AddEntry(I.GetListOfGraphs()[0], "Layer 1","P")
        leg.AddEntry(I.GetListOfGraphs()[1], "Layer 2","P")
        leg.AddEntry(I.GetListOfGraphs()[2], "Layer 3","P")
        leg.AddEntry(I.GetListOfGraphs()[3], "Layer 4","P")
    #else: leg.AddEntry(I.GetListOfGraphs()[0], "Layer 1&2","P")
    #leg.AddEntry(I.GetListOfGraphs()[nLayers-1], "Layer 3","P")
    leg.Draw("same")

    ### Latex box
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(61)
    latex.SetTextAlign(11)
    latex.DrawLatex(0.1, .93, "CMS");
    #    latex.SetTextFont(52)
    latex.DrawLatex(0.18, .93, "Pixel");

    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextFont(42)
    latex2.SetTextSize(0.043)
    latex2.SetTextAlign(11)
    latex2.DrawLatex(0.53, .83, settings["sub_detector_text"]);

    latex3 = ROOT.TLatex()
    latex3.SetNDC()
    latex3.SetTextFont(42)
    latex3.SetTextSize(0.043)
    latex3.SetTextAlign(11)
    latex3.DrawLatex(0.53, .77, settings["current_text"]);

    latex4 = ROOT.TLatex()
    latex4.SetNDC()
    latex4.SetTextFont(42)
    latex4.SetTextSize(0.043)
    latex4.SetTextAlign(11)
    latex4.DrawLatex(0.53, .71, text);

          
    figure_name = output_directory + "/" + settings["base_output_file_name"]
    if Xaxis == "lumi":
        figure_name += "_integrated_lumi"
    elif Xaxis == "fill":
        figure_name += "_fill"
    elif Xaxis=="fluence":
        figure_name += "_fluence"

    extensions = (".pdf", ".png", ".C")
    for extension in extensions:
        c.Print(figure_name + extension)


def __print_azimuth():
    gr_m = __plot_azimuth("m")
    gr_p = __plot_azimuth("p")

    leg = ROOT.TLegend(0.7, 0.7, 0.85, 0.85)
    ROOT.SetOwnership(leg,0)

    leg.SetNColumns(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetBorderSize(0)

    c = ROOT.TCanvas()
    c.cd()
    gr_p.GetYaxis().SetRangeUser(1000., 2100.)
    gr_m.GetYaxis().SetRangeUser(1000., 2100.)
    gr_p.GetYaxis().SetTitleOffset(1.2)

    fsin = ROOT.TF1("fsin", "[0]*sin([1]*x)", 0., 6.3)
    fsin.SetLineColor(ROOT.kRed)

    gr_p.SetTitle("")
    gr_p.Draw("AP")
    gr_m.Draw("Psame")
  
    leg.AddEntry(gr_p, "Layer 1, +z", "P")
    leg.AddEntry(gr_m, "Layer 1, -z", "P")
    leg.Draw("same")
    
    ### Latex box
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(61)
    latex.SetTextAlign(11)
    latex.DrawLatex(0.1, .93, "CMS");
    latex.SetTextFont(52)
    latex.DrawLatex(0.18, .93, "Preliminary");

    latex2 = ROOT.TLatex()
    latex2.SetNDC()
    latex2.SetTextFont(42)
    latex2.SetTextSize(0.04)
    latex2.SetTextAlign(11)
    latex2.DrawLatex(0.615, 0.93, " 42.45 fb^{-1} at #sqrt{s} =13 TeV");

    #gr_m.Fit("fsin")
    
    c.Print("i_leak_Azimuth.pdf")
    c.Print("i_leak_Azimuth.png")


def main(args):

    __do_sanity_checks(args)
    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    sub_detector = args.sub_detector
    era = args.era or ""

    # TODO: Where is this hard-coded list coming from?
    bad_fills = gUtl.get_bad_fills(args.bad_fills_file_name)

    # TODO: Where are these hard-coded numbers come from?
    # TODO: Add unit in comment
    fluence = {
        "L1": 3.850588e+12,
        "L2": 1.634252e+12,
        "L3": 1.023023e+12,
    }

    fills_info = gUtl.get_fill_info(args.input_fills_file_name)
    fills = gUtl.get_fills(fills_info, bad_fills, args.first_fill, args.last_fill, args.era)
    integrated_lumi_per_fill = gUtl.get_integrated_lumi_per_fill(args.input_lumi_file_name)

    currents = __get_currents_per_layer(sub_detector, fills, args.input_currents_directory)

    AnaCurrents  = __get_analog_and_digital_currents(sub_detector, fills, "Ana", args.input_currents_directory)
    AnaPerRocCurrents  = __get_analog_and_digital_currents(sub_detector, fills, "AnaPerRoc", args.input_currents_directory)
    DigCurrents  = __get_analog_and_digital_currents(sub_detector, fills, "Dig", args.input_currents_directory)

    plotting_settings = {
        "Digital": {
            "y_label": "I_{digital} [A]",
            "base_output_file_name": "I_dig_" + era,
            "legend_coordinates": (0.15, 0.7, 0.35, 0.85),
            "y_range": (2., 5.5),
            "sub_detector_text": "CMS " + args.sub_detector + " Pixel Detector",
            "current_text": "Digital Current",
        },
        "AnalogPerRoc" : {
            "y_label": "I_{analog}/ROC [A]",
            "base_output_file_name": "I_ana_perRoc_" + era,
            "legend_coordinates": (0.15, 0.7, 0.35, 0.85),
            "y_range": (0.023, 0.032),
            "sub_detector_text": "CMS " + args.sub_detector + " Pixel Detector",
            "current_text": "Analog Current",
        },
        "Analog": {
            "y_label": "I_{analog} [A]",
            "base_output_file_name": "I_ana_" + era,
            "legend_coordinates": (0.15, 0.7, 0.35, 0.85),
            "y_range": (0., 4.),
            "sub_detector_text": "CMS " + args.sub_detector + " Pixel Detector",
            "current_text": "Analog Current",
        },
        "Leakage": {
            "y_label": "I_{leak} [#muA / cm^{3}], (corr.to 0 #circC)",
            "base_output_file_name": "i_leak_" + era,
            "legend_coordinates": (0.15, 0.7, 0.35, 0.85),
            "y_range": (0., 7000.),
            "sub_detector_text": "CMS " + args.sub_detector + " Pixel Detector",
            "current_text": "Leakage Current",
        },
        # TODO:
        # "Leakage"      :("I_{leak} [#muA / cm^{3}], (corr.to 0#circC)", "i_leak_lumi_"+era, (0.15, 0.7, 0.35, 0.85), (0.,1400.), "CMS Barrel Pixel Detector",  "Leakage Current")
        # "Leakage"      :("I_{leak} [#muA / cm^{3}], (corr.to 0#circC)", "i_leak_lumi_"+era, (0.15, 0.7, 0.35, 0.85), (0.,30.), "CMS Forward Pixel Detector", "Leakage Current")
    }



    # settings = {
    #     "Digital": (
    #         "I_{digital} [A]",
    #         "I_dig_" + era,
    #         (0.15, 0.7, 0.35, 0.85),
    #         (2., 5.5),
    #         "CMS " + args.sub_detector + " Pixel Detector",
    #         "Digital Current",
    #     ),
    #     "AnalogPerRoc" : (
    #         "I_{analog}/ROC [A]",
    #         "I_ana_perRoc_" + era,
    #         (0.15, 0.7, 0.35, 0.85),
    #         (0.023, 0.032),
    #         "CMS " + args.sub_detector + " Pixel Detector",
    #         "Analog Current",
    #     ),
    #     "Analog": (
    #         "I_{analog} [A]",
    #         "I_ana_" + era,
    #         (0.15, 0.7, 0.35, 0.85),
    #         (0., 4.),
    #         "CMS " + args.sub_detector + " Pixel Detector",
    #         "Analog Current",
    #     ),
    #     "Leakage": (
    #         "I_{leak} [#muA / cm^{3}], (corr.to 0 #circC)",
    #         "i_leak_" + era,
    #         (0.15, 0.7, 0.35, 0.85),
    #         (0., 4000.),
    #         "CMS " + args.sub_detector + " Pixel Detector",
    #         "Leakage Current",
    #     ),
    #     # TODO:
    #     # "Leakage"      :("I_{leak} [#muA / cm^{3}], (corr.to 0#circC)", "i_leak_lumi_"+era, (0.15, 0.7, 0.35, 0.85), (0.,1400.), "CMS Barrel Pixel Detector",  "Leakage Current")
    #     # "Leakage"      :("I_{leak} [#muA / cm^{3}], (corr.to 0#circC)", "i_leak_lumi_"+era, (0.15, 0.7, 0.35, 0.85), (0.,30.), "CMS Forward Pixel Detector", "Leakage Current")
    # }

    text = eraUtl.get_date_from_era(era) if era != "" else ""

    #__print_azimuth()
    #__plot_currents(DigCurrents, integrated_lumi_per_fill, "Digital")
    #__plot_currents(AnaCurrents, integrated_lumi_per_fill, "Analog", "fill")
    #__plot_currents(AnaPerRocCurrents, integrated_lumi_per_fill, "AnalogPerRoc")
    #__plot_currents(currents, integrated_lumi_per_fill, "Leakage", "fill")
    variables_to_plot = ("Leakage", )
    for variable in variables_to_plot:
        settings = plotting_settings[variable]
        __plot_currents(args.output_directory, sub_detector, settings, currents,
                        fluence, fills, integrated_lumi_per_fill, variable,
                        "lumi", era, text)
        #__plot_currents(args.output_directory, sub_detector, settings, currents,
        #                fluence, fills, integrated_lumi_per_fill, variable,
        #                "fluence", era, text)


if __name__ == "__main__":

    args = __get_arguments()
    main(args)