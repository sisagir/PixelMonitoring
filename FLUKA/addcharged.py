#!/usr/bin/env python 

from decimal import *

#writefile = open("z0_charged_6500GeV_phase0.txt", "a")

#change these:
modulepos = "z0" 
#modulepos = "zminus30"# for bpix
phase = "phase1"
#phase = "phase0"# for bpix

writefile = open(modulepos+"/"+modulepos+"_charged_6500GeV_"+phase+".txt", "a")

#To do: remove old file

with open(modulepos+"/"+modulepos+"_prot_6500GeV_"+phase+".txt", "r") as protfile:
   with open(modulepos+"/"+modulepos+"_aprot_6500GeV_"+phase+".txt", "r") as aprotfile:  
	with open(modulepos+"/"+modulepos+"_pions_6500GeV_"+phase+".txt", "r") as pionfile:
		aprotlines = aprotfile.read().splitlines();
		pionlines = pionfile.read().splitlines();
		for i, protline in enumerate(protfile):
			print("str(i) " + str(i))
			print("protline"+str(protline.split()[1]))
			print("aprotline"+str(aprotlines[i].split('\t')[1] ))
			print("pionline"+str(pionlines[i].split('\t')[1] ))
			writefile.write(str(protline.split()[0]) + '\t' + str('%.4E' % ( Decimal(protline.split()[1]) + Decimal(aprotlines[i].split('\t')[1]) + Decimal(pionlines[i].split('\t')[1]))) + '\n' )
writefile.close()
