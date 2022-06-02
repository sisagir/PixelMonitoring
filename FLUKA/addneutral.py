#!/usr/bin/env python 

from decimal import *

#writefile = open("z0_neutral_6500GeV_phase1.txt", "a")

#change these:
modulepos = "z0"
#modulepos = "zminus30" # for fpix
phase = "phase1"
#phase = "phase0" # for fpix

writefile = open(modulepos+"/"+modulepos+"_neutral_6500GeV_"+phase+".txt", "a")
#To do: remove old file

with open(modulepos+"/"+modulepos+"_neut_6500GeV_"+phase+".txt", "r") as neutfile:
   with open(modulepos+"/"+modulepos+"_aneut_6500GeV_"+phase+".txt", "r") as aneutfile:  
      aneutlines = aneutfile.read().splitlines();
      for i, neutline in enumerate(neutfile):
			print("str(i) " + str(i))
			print("neutline"+str(neutline.split()[1]))
			print("aneutline"+str(aneutlines[i].split('\t')[1] ))
			writefile.write(str(neutline.split()[0]) + '\t' + str('%.4E' % ( Decimal(neutline.split()[1]) + Decimal(aneutlines[i].split('\t')[1])) + '\n' ))
writefile.close()
