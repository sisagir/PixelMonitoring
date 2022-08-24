import sys
sys.argv.append('-b')

import matplotlib.pyplot as plt
import math
import ROOT
import copy

from array import array
from .constants import *

style = ROOT.TStyle();
style.SetOptFit(0o001);


startFillRaw = input("Enter start fill number: ")
endFillRaw = input("Enter end fill number: ")

startFill = int(startFillRaw)
endFill = int(endFillRaw)

fillFile = open('FillInfo_TotLumi.txt', 'r+')



fillListArray = []
badFills = [1013, 1019, 1022, 1023, 1026, 1031,1033,1635,1640,1839,2028,2085,2117,2240,2256,2350,2509,2523,2632,2719,2734,2810,2842,2852,2883,2977,2993,3023,3108,3160,3225,3310,3314,3319,3850,3851,3857,3981,4205,4214,4219,4220,4231]




for row in fillFile:
    goodRun = int(row.split(' ')[0]) >= startFill and int(row.split(' ')[0]) < endFill
#    print "ROW: ", row
 #   print "goodRun? ", goodRun
    if "None" not in row and "2013-" not in row and goodRun and int(row.split(' ')[0]) not in badFills:
        fillListArray.append(int(row.split(' ')[0]))

fileNameList = []
fill_nums = [fillListArray[i] for i in range(len(fillListArray)) ]

print("==> List of Fills: ", fill_nums)
#fill_nums = [5564, 5565, 5568, 5569, 5570, 5571, 5573]
barrelOrEndCap = "Barrel"

# *********************************************************************
# Currents per Layer                                                  
#
# Get the sum of the currents/ROC for each layer for each fill number
#
# *********************************************************************

Temps = {}

for fn in range(len(fill_nums)):



    filename ="txt/" + str(fill_nums[fn]) + "_TAIR.txt"
    f = open(filename, 'r+')
    temp = 0.
    n = 0.
    for row in f.readlines():
        #        print "Row: ", row
#        print "Temperature: ", row.split()[1]
        temp += float(row.split()[1])

        n +=1

    if(n!=0):temp = temp/n

    Temps[str(fill_nums[fn])]= temp





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
            fill_lumis[fn] = float(row.split(' ')[7])/1000.
            if fn == 4988:
                print("====> Fill number: ", str(fn))
                print("=====> Luminosity: ", fill_lumis[fn])


        
def getGraph(y_array, x_array, name=""):
        graph = ROOT.TGraph( len(x_array),  x_array, y_array)
        graph.GetXaxis().SetTitle("Fill Number")
        graph.GetYaxis().SetTitle("BPix ambient temperature [#degree C]")
        graph.SetTitle(name)
        return graph

def plotTemperature(Temps, fill_nums):

    fill_array = array('f', fill_nums)
    
    temp_array = array('f',  [Temps[str(f)] for f in fill_nums])
 
    g = getGraph(temp_array,fill_array)
    g.SetLineColor(ROOT.kTeal+4)
    g.SetMarkerColor(ROOT.kTeal+4)
    g.SetMarkerStyle(22)
    g.SetMarkerSize(0.8)


    return g


    
def printTempsVsLumi(Temps, fill_lumis):
    ### curTypeObj is an element of settings, i.e. a tuple
    c = ROOT.TCanvas("Temperature.pdf")
    c.cd()
    leg = ROOT.TLegend(0.15, 0.7, 0.35, 0.85)
    ROOT.SetOwnership(leg,0)
     
 
    T = plotTemperature(Temps, fill_lumis)
    ROOT.SetOwnership(T,0)
    T.Draw("AP")
    T.GetXaxis().SetTitle("Temperature")
 #   T.GetYaxis().SetTitle(settings[curTypeObj][0])
    T.GetYaxis().SetTitleOffset(1.3)
#    T.GetYaxis().SetRangeUser(settings[curTypeObj][3][0], settings[curTypeObj][3][1])
  
    leg.SetNColumns(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetBorderSize(0)


    ### Latex box
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(61)
    latex.SetTextAlign(11)
    latex.DrawLatex(0.1, .93, "CMS");
    latex.SetTextFont(52)
    latex.DrawLatex(0.18, .93, "Preliminary");

    c.Print("Temperatures.pdf")
    c.Print( "Temperatures.png")



printTempsVsLumi(Temps, fill_lumis)

