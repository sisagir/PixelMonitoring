import sys
#sys.argv.append('-b')

import matplotlib.pyplot as plt
import math
import optparse
import ROOT
import copy

from array import array
from .constants import *

style = ROOT.TStyle();
style.SetOptFit(0o001);


usage = 'usage: %prog --BarrelorEndCap BarrelOrEndCap --phase Phase'
parser = optparse.OptionParser(usage)
#parser.add_option('-r', '--run', dest='run', type='int', help='Number of the run to analyze')
parser.add_option("","--BarrelOrEndCap",dest="BarrelOrEndCap",type="string",default="Barrel",help="Indicate if you wish to access current informations for BPix or FPix. Allowed choices: Barrel, EndCap.")
#parser.add_option("-p","--phase",dest="phase",type="string",default="Phase0",help="Indicate if you wish to access current informations for phase0 or phase1 pixel detector. Allowed choices: phase0, phase1")

(opt, args) = parser.parse_args()


barrelOrEndCap = opt.BarrelOrEndCap

fluenceL1 =  3.850588e+12
fluenceL2 = 1.634252e+12
fluenceL3 = 1.023023e+12

fillFile = open('FillInfo_TotLumi.txt', 'r+')

period = "2016"
#period = "Run2"
#periond = "Run1plus2"
years = {"Run2": "Mar 2015 - Dec 2016", "Run1plus2": "Mar 2010 - Dec 2016", "2017":"Apr 2017 - today", "2016":"Apr 2016 - Dec 2016"}

fillListArray = []
badFills = [1013, 1019, 1022, 1023, 1026, 1031,1033,1635,1640,1839,2028,2085,2117,2240,2256,2350,2509,2523,2632,2719,2734,2810,2842,2852,2883,2977,2993,3023,3108,3160,3225,3310,3314,3319,3850,3851,3857,3981,4205,4214,4219,4220,4231]


goodRun = False

for row in fillFile:

    if(period =="Run1-2012"): goodRun = int(row.split(' ')[0]) >= 3114 and int(row.split(' ')[0]) < 3819
    elif(period =="Run2"): goodRun =  int(row.split(' ')[0]) >= 3819 and int(row.split(' ')[0]) <= 5456
    elif(period =="2016"): goodRun =  int(row.split(' ')[0]) >= 4851 and int(row.split(' ')[0]) <= 5456
    #elif(period =="2016"): goodRun =  int(row.split(' ')[0]) >= 5420 and int(row.split(' ')[0]) <= 5456
    elif(period =="2015"): goodRun =  int(row.split(' ')[0]) >= 3819 and int(row.split(' ')[0]) < 4851
    elif(period == "Run1plus2"):goodRun = int(row.split(' ')[0]) >= 5300 and int(row.split(' ')[0]) <= 5456
#    elif(period =="2017"): goodRun =  int(row.split(' ')[0]) >= 5576 and int(row.split(' ')[0]) <= 7000
    elif(period =="2017"): goodRun =  int(row.split(' ')[0]) >= 5698 and int(row.split(' ')[0]) <= 7000

#    elif(period =="2017"):  goodRun =  int(row.split(' ')[0]) > 5884 and int(row.split(' ')[0]) < 5886
    
    else:  goodRun = True
    if "None" not in row and "2013-" not in row and goodRun and int(row.split(' ')[0]) not in badFills:
        fillListArray.append(int(row.split(' ')[0]))


fileNameList = []
fill_nums = [fillListArray[i] for i in range(len(fillListArray)) ]
#print "list of fill numbers: ", fill_nums
#barrelOrEndCap = "EndCap"
#barrelOrEndCap = "Barrel"

## #### --------------------------------------------------------------------------------------------------------------
## #### Constants
## kb = 8.6173324 * math.pow(10, -5) # [eV * K^{-1}]
## Eg = 1.21 # [eV]
## Kfact = 273.15
## Tref = Kfact
## ### Coolant temperature
## T_coolant = -10
## ### Actual sensor temperature is higher than coolant temperature. Considering here +10 degrees.
## T_diff = 10
## ### Sensor volume
## rocVol = 0.81 * 0.81 * 0.0285
## #### --------------------------------------------------------------------------------------------------------------


### Function translating ROC average current in Leakage current @ degrees C
def getLeakageCurrent(I, T):
    I_vol = I/rocVol
    #print "Average current per ROC: ", I
    a = -Eg/(2*kb)
    b =  (1./Tref) - (1./T)
    expo = a * b
    IatZero = I_vol * math.pow(Tref/T, 2) *math.exp(expo)
#    return I_vol#IatZero
    return IatZero


class current:
    pass


# *********************************************************************
# Currents per Layer                                                  
#
# Get the sum of the currents/ROC for each layer for each fill number
#
# *********************************************************************

Currents = {}

for fn in range(len(fill_nums)):

    if fill_nums[fn] <= 2351:
        T_coolant = 7
    elif fill_nums[fn] <= 3599 and fill_nums[fn] > 2351:
        T_coolant = 0
    elif fill_nums[fn] <= 5575  and fill_nums[fn] > 3599:
        T_coolant = -10
    elif fill_nums[fn] > 5575 and fill_nums[fn] <= 5900:
        T_coolant = -20
    else: T_coolant = -22
    ### Sensor temperature in Kelvin
    T_sensor = T_coolant + T_diff + Kfact
    #print "Sensor Temperature: ", T_sensor
    filename ="txt/" + str(fill_nums[fn]) + "_" + barrelOrEndCap + "_HV_ByLayer.txt"
    f = open(filename, 'r+')
    I = current()
    I.I_ROC_LAY1 = 0.
    I.I_ROC_LAY2 = 0.
    I.I_ROC_LAY3 = 0.
    I.I_ROC_LAY4 = 0.
    I.nLay1 = 0
    I.nLay2 = 0
    I.nLay3 = 0
    I.nLay4 = 0
    for row in f.readlines():
        if "LAY1" in row :
            I.I_ROC_LAY1 += float(row.rsplit('LAY1 ')[1])
            I.nLay1+=1
        elif "LAY2" in row :
            I.I_ROC_LAY2 += float(row.rsplit('LAY2 ')[1])
            I.nLay2+=1
        elif "LAY3" in row :
            I.I_ROC_LAY3 += float(row.rsplit('LAY3 ')[1])
            I.nLay3+=1
        elif "LAY4" in row :
            I.I_ROC_LAY4 += float(row.rsplit('LAY4 ')[1])
            I.nLay4+=1
        elif "D1" in row :
            I.I_ROC_LAY1 += float(row.rsplit('D1 ')[1])
            I.nLay1+=1
        elif "D2" in row :
            I.I_ROC_LAY2 += float(row.rsplit('D2 ')[1])
            I.nLay2+=1
        elif "D3" in row :
            I.I_ROC_LAY3 += float(row.rsplit('D3 ')[1])
            I.nLay3+=1

    I.I_leak_LAY1 = getLeakageCurrent(I.I_ROC_LAY1, T_sensor)
    I.I_leak_LAY2 = getLeakageCurrent(I.I_ROC_LAY2, T_sensor)
    I.I_leak_LAY3 = getLeakageCurrent(I.I_ROC_LAY3, T_sensor)
    I.I_leak_LAY4 = getLeakageCurrent(I.I_ROC_LAY4, T_sensor)

    if(I.nLay1!=0):I.I_leak_LAY1 /= I.nLay1
    if(I.nLay2!=0):I.I_leak_LAY2 /= I.nLay2
    if(I.nLay3!=0):I.I_leak_LAY3 /= I.nLay3
    if(I.nLay4!=0):I.I_leak_LAY4 /= I.nLay4

    Currents[str(fill_nums[fn])]= I

    if Currents[str(fill_nums[fn])].I_leak_LAY1>200 and I.I_leak_LAY2 >200 and I.I_leak_LAY3 >200 and I.I_leak_LAY4 >200 and fill_nums[fn] > 2000 and fill_nums[fn] < 2500:
      print("Fill " + str(fill_nums[fn]) + "has current > 200\n")


# *********************************************************************
# Analog and Digital currents per group                                                  
#
# Get the sum of the currents/ROC for each layer for each fill number
#
# *********************************************************************

AnaCurrents = {}
DigCurrents = {}

def getAnaDigCurrent(fill_nums, curType):
    currents = {}
    for fn in range(len(fill_nums)):
        filename ="txt/" + str(fill_nums[fn]) + "_" + barrelOrEndCap + "_"+curType+".txt"
        f = open(filename, 'r+')
        I = current()
        I.Ana_LAY14 = 0.
        I.Ana_LAY3 = 0.
        nLay14=0
        nLay23=0
        #print "===>We are in fill number: ", str(fill_nums[fn])
        for row in f.readlines():
            if "LAY14" in row:

                I.Ana_LAY14 += float(row.rsplit('LAY14 ')[1])
                nLay14+=1
                #print "Found analog current for LAY14: ", I.Ana_LAY14
            elif "LAY3" in row:
                I.Ana_LAY3 += float(row.rsplit('LAY3 ')[1])
                nLay23+=1

        if(nLay14!=0): I.Ana_LAY14 /= nLay14
        if(nLay23!=0): I.Ana_LAY3 /= nLay23
        currents[str(fill_nums[fn])]= I
        #print "Current = ", currents[str(fill_nums[fn])]

    #print "===>Checking current values for Iana: ", currents
    return  currents


AnaCurrents  = getAnaDigCurrent(fill_nums, "Ana")
AnaPerRocCurrents  = getAnaDigCurrent(fill_nums, "AnaPerRoc")
DigCurrents  = getAnaDigCurrent(fill_nums, "Dig")

# *********************************************************************
# Assign fills to integrated lumi
# for when we want to plot current vs lumi
# *********************************************************************
fill_lumis = {} 

for fn in fill_nums:

    lumiFile = open('FillInfo_TotLumi.txt', 'r+')
    for row in lumiFile:

        if fn == 4988 and (str(fn)==row.split(' ')[0]): print("testing row splitting: ",row.split(' '))
        if (str(fn)==row.split(' ')[0]) and "None" not in row and int(fn) not in badFills:
            fill_lumis[fn] = (float(row.split(' ')[7])/1000.) 
            if (period=="2017"):fill_lumis[fn] = (float(row.split(' ')[7])/1000.) - 73810.286
             
            if fn == 4988:
                print("====> Fill number: ", str(fn))

# *********************************************************************
# Currents vs Phi                                                  
#
# Get the sum of the currents/ROC vs Phi for each fill number
#
# *********************************************************************


def sumElList(l): 
    x = 0
    for i in range(len(l)) :
        x += l[i]

    return x 


def getCurrentVsPhi(fill, z="m"):

    if fill < 5900:
        print("===========> New temperature ")
        T_coolant = -20
    else: T_coolant = -22
    ### Sensor temperature in Kelvin
    T_sensor = T_coolant + T_diff + Kfact

    #print "Fill number: ", fill
    #print "Sensor Temperature: ", T_sensor
    filename = "txt/" + str(fill) + "_" + barrelOrEndCap + "_HV_ByLayer.txt"
    f = open(filename, 'r+')
    phiMod = {"S1_O": 0., "S2_O": 0., "S3_O": 0., "S4_O": 0., "S5_O": 0., "S6_O": 0., "S7_O": 0., "S8_O": 0., "S1_I": 0., "S2_I": 0., "S3_I": 0., "S4_I": 0., "S5_I": 0., "S6_I": 0., "S7_I": 0., "S8_I": 0.,}

    nLay1 = 0
    mapCurr = {}
    for k in list(phiMod.keys()):
        mapCurr[k] = []


    for row in f.readlines():
        if ("LAY1" in row ):
            if("BpI" not in row):
                r = row.split('_')
                key = r[2] + "_" + r[1][2]
                zSide =  r[1][1]
                if(zSide == z):mapCurr[key].append(getLeakageCurrent(float(row.rsplit('LAY1 ')[1]), T_sensor))


    for k in  list(mapCurr.keys()):
        if(len(mapCurr[k])!=0):phiMod[k] = sumElList(mapCurr[k])/len(mapCurr[k])
        else:phiMod[k]

    #print "PhiMod ====> ",phiMod
    return phiMod


def AddDict(dict1, dict2, sign = -1):
    phiMod = {}
    for k in list(dict1.keys()):
        phiMod[k] = dict2[k] - dict1[k]
            
    return phiMod


        
def getGraph(I_leak_array, fill_array, name=""):
        I_graph = ROOT.TGraph( len(fill_array),  fill_array, I_leak_array)
        I_graph.GetXaxis().SetTitle("Fill Number")
        I_graph.GetYaxis().SetTitle("Leakage current I [#mu A / cm^{3}]")
        I_graph.SetTitle(name)
        return I_graph

def plotAzimuth(z="m"):

    outFill = fill_nums[-1]
    #print "Last fill: ", outFill
    inFill = fill_nums[0]
    #print "First fill: ", inFill
    phiDict2 = getCurrentVsPhi(outFill,z)
    # print "1st set: ", phiDict2
    phiDict1 = getCurrentVsPhi(inFill,z)
    # print "2nd set: ", phiDict1
    # print "First fill: ", inFill
    # print "Last fill: ", outFill
    phiMod =  AddDict(phiDict1, phiDict2)
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
        
    # print phi
    phi_array = array('f', phi)
    I_phi_array = array('f', I_phi)

    g1 = getGraph(I_phi_array,phi_array, "Layer 1")
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

def plotCurrents(Currents, fill_nums, plotType="Leakage"):

    fill_array = array('f', fill_nums)
    if(plotType=="Leakage"):
        I_leak_L1_array = array('f',  [Currents[str(f)].I_leak_LAY1 for f in fill_nums])
        I_leak_L2_array = array('f',  [Currents[str(f)].I_leak_LAY2 for f in fill_nums])
        I_leak_L3_array = array('f',  [Currents[str(f)].I_leak_LAY3 for f in fill_nums])
        I_leak_L4_array = array('f',  [Currents[str(f)].I_leak_LAY4 for f in fill_nums])
    elif(plotType=="ROC"):
        I_leak_L1_array = array('f',  [Currents[str(f)].I_ROC_LAY1 for f in fill_nums])
        I_leak_L2_array = array('f',  [Currents[str(f)].I_ROC_LAY2 for f in fill_nums])
        I_leak_L3_array = array('f',  [Currents[str(f)].I_ROC_LAY3 for f in fill_nums])
        I_leak_L4_array = array('f',  [Currents[str(f)].I_ROC_LAY4 for f in fill_nums])
    elif(plotType=="DI"):
        I_leak_L1_array = array('f',  [(Currents[str(f)].I_leak_LAY1 - Currents[str(fill_nums[0])].I_leak_LAY1) for f in fill_nums])
        I_leak_L2_array = array('f',  [(Currents[str(f)].I_leak_LAY2 - Currents[str(fill_nums[0])].I_leak_LAY2) for f in fill_nums])
        I_leak_L3_array = array('f',  [(Currents[str(f)].I_leak_LAY3 - Currents[str(fill_nums[0])].I_leak_LAY3) for f in fill_nums])
        I_leak_L4_array = array('f',  [(Currents[str(f)].I_leak_LAY4 - Currents[str(fill_nums[0])].I_leak_LAY4) for f in fill_nums])
    elif(plotType=="DeltaROC"):
        print("DIROC")
        I_leak_L1_array = array('f',  [(Currents[str(f)].I_ROC_LAY1 - Currents[str(fill_nums[0])].I_ROC_LAY1) for f in fill_nums])
        I_leak_L2_array = array('f',  [(Currents[str(f)].I_ROC_LAY2 - Currents[str(fill_nums[0])].I_ROC_LAY2) for f in fill_nums])
        I_leak_L3_array = array('f',  [(Currents[str(f)].I_ROC_LAY3 - Currents[str(fill_nums[0])].I_ROC_LAY3) for f in fill_nums])
        I_leak_L4_array = array('f',  [(Currents[str(f)].I_ROC_LAY4 - Currents[str(fill_nums[0])].I_ROC_LAY4) for f in fill_nums])
 
 
    I_leak = ROOT.TMultiGraph("mg", "")
    g1 = getGraph(I_leak_L1_array,fill_array, "Layer 1")
    g1.SetLineColor(ROOT.kTeal+4)
    g1.SetMarkerColor(ROOT.kTeal+4)
    g1.SetMarkerStyle(22)
    g1.SetMarkerSize(0.8)
    #g1.Fit("pol1", "F");

    g2 = getGraph(I_leak_L2_array,fill_array, "Layer 2")
    g2.SetLineColor(ROOT.kRed+1)
    g2.SetMarkerColor(ROOT.kRed+1 )
    g2.SetMarkerStyle(22)
    g2.SetMarkerSize(0.8)
    #g2.Fit("pol1", "F");
    
    g3 = getGraph(I_leak_L3_array,fill_array, "Layer 3")
    g3.SetLineColor(ROOT.kBlue+2)
    g3.SetMarkerStyle(22)
    g3.SetMarkerColor(ROOT.kBlue+2)
    g3.SetMarkerSize(0.8)

    g4 = getGraph(I_leak_L4_array,fill_array, "Layer 4")
    g4.SetLineColor(ROOT.kBlack)
    g4.SetMarkerStyle(22)
    g4.SetMarkerColor(ROOT.kBlack)
    g4.SetMarkerSize(0.8)


    #g3.Fit("pol1", "F");
    I_leak.Add(g1)
    I_leak.Add(g2)
    I_leak.Add(g3)
    I_leak.Add(g4)
    return I_leak


def plotCurrentsVsLumi(Currents, fill_lumis, plotType="Leakage", Xaxis = "lumi"):

    if (Xaxis == "lumi"): lumi = [fill_lumis[fn] for fn in fill_nums]    
    elif(Xaxis == "fluence"): lumi = [fill_lumis[fn] for fn in fill_nums]
    else: lumi = fill_nums    
    fill_array = array('f', lumi)
    if(plotType=="Leakage"):
        I_L1_array = array('f',  [Currents[str(f)].I_leak_LAY1 for f in fill_nums])
        I_L2_array = array('f',  [Currents[str(f)].I_leak_LAY2 for f in fill_nums])
        I_L3_array = array('f',  [Currents[str(f)].I_leak_LAY3 for f in fill_nums])
        I_L4_array = array('f',  [Currents[str(f)].I_leak_LAY4 for f in fill_nums])
    elif(plotType=="ROC"):
        I_L1_array = array('f',  [Currents[str(f)].I_ROC_LAY1 for f in fill_nums])
        I_L2_array = array('f',  [Currents[str(f)].I_ROC_LAY2 for f in fill_nums])
        I_L3_array = array('f',  [Currents[str(f)].I_ROC_LAY3 for f in fill_nums])
        I_L4_array = array('f',  [Currents[str(f)].I_ROC_LAY4 for f in fill_nums])
    elif(plotType=="DI"):
        I_L1_array = array('f',  [(Currents[str(f)].I_leak_LAY1 - Currents[str(fill_nums[0])].I_leak_LAY1) for f in fill_nums])
        I_L2_array = array('f',  [(Currents[str(f)].I_leak_LAY2 - Currents[str(fill_nums[0])].I_leak_LAY2) for f in fill_nums])
        I_L3_array = array('f',  [(Currents[str(f)].I_leak_LAY3 - Currents[str(fill_nums[0])].I_leak_LAY3) for f in fill_nums])
        I_L4_array = array('f',  [(Currents[str(f)].I_leak_LAY4 - Currents[str(fill_nums[0])].I_leak_LAY4) for f in fill_nums])
    elif(plotType=="DeltaROC"):
        I_L1_array = array('f',  [(Currents[str(f)].I_ROC_LAY1 - Currents[str(fill_nums[0])].I_ROC_LAY1) for f in fill_nums])
        I_L2_array = array('f',  [(Currents[str(f)].I_ROC_LAY2 - Currents[str(fill_nums[0])].I_ROC_LAY2) for f in fill_nums])
        I_L3_array = array('f',  [(Currents[str(f)].I_ROC_LAY3 - Currents[str(fill_nums[0])].I_ROC_LAY3) for f in fill_nums])
        I_L4_array = array('f',  [(Currents[str(f)].I_ROC_LAY4 - Currents[str(fill_nums[0])].I_ROC_LAY4) for f in fill_nums])
    elif(plotType.startswith("Analog") or plotType=="Digital"):
        I_L1_array = array('f',  [Currents[str(f)].Ana_LAY14  for f in fill_nums])
        #print "currents: ", I_L1_array
        I_L3_array = array('f',  [Currents[str(f)].Ana_LAY3 for f in fill_nums])

    I_leak_lumi = ROOT.TMultiGraph("mg", "")
    
    if(Xaxis=="fluence"): 
        lumi = [fill_lumis[fn]*fluenceL1 for fn in fill_nums]
        fill_array = array('f', lumi)
    g1 = getGraph(I_L1_array,fill_array, "Layer 1")
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
    I_leak_lumi.Add(g1)
    
    if(not plotType.startswith("Analog") and plotType!="Digital"):
        if(Xaxis=="fluence"):
            lumi = [fill_lumis[fn]*fluenceL2 for fn in fill_nums] 
            fill_array = array('f', lumi)
        g2 = getGraph(I_L2_array,fill_array, "Layer 2")
        g2.SetLineColor(ROOT.kBlue+2)
        g2.SetMarkerColor(ROOT.kBlue+2)
        g2.SetMarkerStyle(22)
        g2.SetMarkerSize(0.8)
        FitHisto2 = ROOT.TF1("f2", "[0] +[1]*x", 29100, 30000)
        #g2.Fit("f2");
        #print "Layer2: "
        #print "p0: ", FitHisto2.GetParameter(0)
        #print "p1: ", FitHisto2.GetParameter(1)
        I_leak_lumi.Add(g2)

    if(Xaxis=="fluence"):
        lumi = [fill_lumis[fn]*fluenceL3 for fn in fill_nums] 
        fill_array = array('f', lumi)
    g3 = getGraph(I_L3_array,fill_array, "Layer 2 & 3")
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
    I_leak_lumi.Add(g3)



    if(not plotType.startswith("Analog") and plotType!="Digital"):
        if (barrelOrEndCap != "Barrel" and period !="2016"): 
            g4 = getGraph(I_L4_array,fill_array, "Layer 4")
            g4.SetLineColor(ROOT.kBlack+1)
            g4.SetMarkerStyle(22)
            g4.SetMarkerColor(ROOT.kBlack+1)
            g4.SetMarkerSize(0.8)
            FitHisto4 = ROOT.TF1("f4", "[0] +[1]*x", 29100, 30000)
            I_leak_lumi.Add(g4) #sleontsi

    return I_leak_lumi


settings = {

#### Key:     ( yaxisLabel, outfileName, (legend coordinates) )
    "Digital"      :("I_{digital} [A]","I_dig_"+period, (0.15, 0.7, 0.35, 0.85), (2., 5.5), "CMS Barrel Pixel Detector","Digital current"),
    "AnalogPerRoc" :("I_{analog}/ROC [A]", "I_ana_perRoc_"+period, (0.15, 0.7, 0.35, 0.85), (0.023, 0.032), "CMS Barrel Pixel Detector", "Analog Current"),
    "Analog"       :("I_{analog} [A]", "I_ana_"+period, (0.15, 0.7, 0.35, 0.85), (0., 4.), "CMS Barrel Pixel Detector"," Analog Current"),
    "Leakage"      :("I_{leak} [#muA / cm^{3}], (corr.to 0#circC)", "I_leak_lumi_"+period, (0.15, 0.7, 0.35, 0.85), (0.,4000.), "CMS Barrel Pixel Detector",  "Leakage Current")
#    "Leakage"      :("I_{leak} [#muA / cm^{3}], (corr.to 0#circC)", "I_leak_lumi_"+period, (0.15, 0.7, 0.35, 0.85), (0.,1400.), "CMS Barrel Pixel Detector",  "Leakage Current")
#    "Leakage"      :("I_{leak} [#muA / cm^{3}], (corr.to 0#circC)", "I_leak_lumi_"+period, (0.15, 0.7, 0.35, 0.85), (0.,30.), "CMS Forward Pixel Detector", "Leakage Current")
}





def printCurrentVsLumi(currents, fill_lumis, curTypeObj, Xaxis="lumi"):
    ### curTypeObj is an element of settings, i.e. a tuple
    c = ROOT.TCanvas(settings[curTypeObj][1].strip(".pdf"))
    c.cd()
    legEdges = settings[curTypeObj][2]
    leg = ROOT.TLegend(legEdges[0], legEdges[1], legEdges[2],legEdges[3])
    ROOT.SetOwnership(leg,0)
     
 
    I = plotCurrentsVsLumi(currents, fill_lumis, curTypeObj, Xaxis)
    ROOT.SetOwnership(I,0)
    I.Draw("AP")
    I.GetXaxis().SetTitle("Integrated Luminosity (pb^{-1})")
    if (Xaxis=="fill"):    I.GetXaxis().SetTitle("Fill number")
    elif (Xaxis=="fluence"):    I.GetXaxis().SetTitle("Total fluence #Phi [1 MeV Neu Eq.]")
    I.GetYaxis().SetTitle(settings[curTypeObj][0])
    I.GetYaxis().SetTitleOffset(1.3)
    I.GetYaxis().SetRangeUser(settings[curTypeObj][3][0], settings[curTypeObj][3][1])
  
    leg.SetNColumns(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetBorderSize(0)

    nLayers = I.GetListOfGraphs().GetSize()
    print("How many layers? ", nLayers)

    if(nLayers==2):
        if(barrelOrEndCap == "EndCap"):
            leg.AddEntry(I.GetListOfGraphs()[0], "Disk 1","P")
            leg.AddEntry(I.GetListOfGraphs()[1], "Disk 2","P")
        else:
            leg.AddEntry(I.GetListOfGraphs()[0], "Layers 1 & 4","P")
            leg.AddEntry(I.GetListOfGraphs()[1], "Layers 2 & 3","P")
    if(nLayers==3):
        if(barrelOrEndCap == "EndCap"):
            leg.AddEntry(I.GetListOfGraphs()[0], "Disk 1","P")
            leg.AddEntry(I.GetListOfGraphs()[1], "Disk 2","P")
            leg.AddEntry(I.GetListOfGraphs()[2], "Disk 3","P")
        else:
            leg.AddEntry(I.GetListOfGraphs()[0], "Layer 1","P")
            leg.AddEntry(I.GetListOfGraphs()[1], "Layer 2","P")
            leg.AddEntry(I.GetListOfGraphs()[2], "Layer 3","P")
    if(nLayers==4 and barrelOrEndCap == "Barrel" and period!="2016"):
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
    latex2.DrawLatex(0.53, .83, settings[curTypeObj][4]);

    latex3 = ROOT.TLatex()
    latex3.SetNDC()
    latex3.SetTextFont(42)
    latex3.SetTextSize(0.043)
    latex3.SetTextAlign(11)
    latex3.DrawLatex(0.53, .77, settings[curTypeObj][5]);

    latex4 = ROOT.TLatex()
    latex4.SetNDC()
    latex4.SetTextFont(42)
    latex4.SetTextSize(0.043)
    latex4.SetTextAlign(11)
    latex4.DrawLatex(0.53, .71, years[period]);

          
    c.Print(settings[curTypeObj][1] + ".pdf")
    c.Print(settings[curTypeObj][1] + ".png")
    c.Print(settings[curTypeObj][1] + ".C")
    if(Xaxis=="fill"):
        c.Print(settings[curTypeObj][1] + "_fill.pdf")
        c.Print(settings[curTypeObj][1] + "_fill.png")
        c.Print(settings[curTypeObj][1] + "_fill.C")
    elif(Xaxis=="fluence"):
        c.Print(settings[curTypeObj][1] + "_fluence.pdf")
        c.Print(settings[curTypeObj][1] + "_fluence.png")
        c.Print(settings[curTypeObj][1] + "_fluence.C")

def printAzimuth():
    gr_m = plotAzimuth("m")
    gr_p = plotAzimuth("p")

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
    
    c.Print("I_leak_Azimuth.pdf")
    c.Print("I_leak_Azimuth.png")

#printAzimuth()
#printCurrentVsLumi(DigCurrents, fill_lumis, "Digital")
#printCurrentVsLumi(AnaCurrents, fill_lumis, "Analog", "fill")
#printCurrentVsLumi(AnaPerRocCurrents, fill_lumis, "AnalogPerRoc")
#printCurrentVsLumi(Currents, fill_lumis, "Leakage", "fill")
printCurrentVsLumi(Currents, fill_lumis, "Leakage", "fluence")
