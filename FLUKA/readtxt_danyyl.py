#!/usr/bin/env python

from decimal import *
import os
import ROOT as rt

#in order of sections in ascii file:
#writefiles = ["z0_allpart_6500GeV_phase0.txt", "z0_neut_6500GeV_phase0.txt", "z0_aneut_6500GeV_phase0.txt", "z0_prot_6500GeV_phase0.txt", "z0_aprot_6500GeV_phase0.txt", "z0_pions_6500GeV_phase0.txt"]
writefiles = ["z0_allpart_6500GeV_phase1.txt", "z0_neut_6500GeV_phase1.txt", "z0_aneut_6500GeV_phase1.txt", "z0_prot_6500GeV_phase1.txt", "z0_aprot_6500GeV_phase1.txt", "z0_pions_6500GeV_phase1.txt"]
#writefiles = ["symtestzminus3/symtestzminus3_allpart_6500GeV_phase1.txt", "symtestzminus3/symtestzminus3_neut_6500GeV_phase1.txt", "symtestzminus3/symtestzminus3_aneut_6500GeV_phase1.txt", "symtestzminus3/symtestzminus3_prot_6500GeV_phase1.txt", "symtestzminus3/symtestzminus3_aprot_6500GeV_phase1.txt", "symtestzminus3/symtestzminus3_pions_6500GeV_phase1.txt"]
percerrwritefiles = ["symtestzminus3/symtestzminus3_allpart_6500GeV_phase1_perc_errors.txt", "symtestzminus3/symtestzminus3_neut_6500GeV_phase1_perc_errors.txt", "symtestzminus3/symtestzminus3_aneut_6500GeV_phase1_perc_errors.txt", "symtestzminus3/symtestzminus3_prot_6500GeV_phase1_perc_errors.txt", "symtestzminus3/symtestzminus3_aprot_6500GeV_phase1_perc_errors.txt", "symtestzminus3/symtestzminus3_pions_6500GeV_phase1_perc_errors.txt"]


# correspond to section index si = 1, 3, 5, 7, 9, 11. Want: neutrons, protons, pions = 3, 7, 11

rbins=200
rmin=0. #cm
rmax=20. #cm
rbinwidth=0.1 #cm
rpos=rbinwidth/2 # mid-bin = 0.0+halfbinwidth
zmin=-350. #cm
zmax=350. #cm
zbins=700
# zbinwidth = 1. #cm
#INTEGER!!! avg z pos from daneks mapping file phase1_dets.txt
#zpos = 50 # for FPix studie
#zpos = 30 # for FPix studie
# zpos = 0 # bin centre will be -0.5
#zpos = -23 # (bin centre will be -23.5) -23.7703304054 #zminus4
#zpos = -17 # -17.0711047297 #zminus3
#zpos = -10 # -10.3697412162 #zminus2
#zpos = -3 # -3.66952087838 #zminus1
#zpos = 4 # bin centre will be 3.5 # 3.02809885135 #zplus1
#zpos = 10 # 9.72911878378 #zplus2
#zpos = 17 # 16.4303945946 #zplus3
#zpos = 24 # 23.1287689189 #zplus4


#zpos = 11 # symtestzplus2
#zpos = 18 # symtestzplus3
#zpos = -9 # symtestzminus2
#zpos = -16 # symtestzminus3
zpos=zmin
zbinwidth=1. #cm
entriesPerLine=10.
linesPerZPos=rbins/entriesPerLine
startentry=linesPerZPos*((zpos-zmin-1)/zbinwidth) # bin left of z=0. (even number of bins, bin edge on 0)
errstartentry = startentry+(zbins*linesPerZPos)+3; #skip the data block and go three lines down to account for distance between the two blocks.
#with open("allpart_7000GeV.txt", "r") as readfile:
#with open("prot_7000GeV.txt", "r") as readfile:
#with open("pions_7000GeV.txt", "r") as readfile:
#with open("neut_7000GeV.txt", "r") as readfile:

def per_section(datafile):
    section = []
    for line in datafile:
        if (line.strip() == str(1)):
            print "IN FUNCTION per_section, end of section "
            tmp = section
            section = []
            if tmp: # don't count first empty one
                yield tmp
        else:
            section.append(line)
    print "IN FUNCTION per_section, end of last section "
    yield section # last one


# delete old files
print "Deleting old files ... "
for oldfile in writefiles:
    print oldfile;
    try:
         os.remove(oldfile);
    except:
        print "no such file";
# for olderrfile in percerrwritefiles:
#     print olderrfile;
#     try:
#          os.remove(olderrfile);
#     except:
#         print "no such file";

print "End of deletion process."
# end of deletion
th2f_fluence=[]
for tag in writefiles:
    th2f_fluence.append(rt.TH2F("fluence_"+tag[3:].rstrip('.txt'),"Fluence(r,z) "+tag[3:].rstrip('.txt'),rbins,rmin,rmax,zbins,zmin,zmax))
fluence_file = rt.TFile.Open("fluence_field.root","RECREATE")
#with open("cmsv3_20_1_0_usrbin_40_ascii", "r") as readfile: #phase0 6500 GeV
with open("cmsv3_23_1_0_usrbin_40_ascii", "r") as readfile: #phase1 6500 GeV
    for si, section in enumerate(per_section(readfile)):
        print " startentry = " + str(startentry) + " linesPerZPos " + str(linesPerZPos);
        print " errstartentry = " + str(errstartentry);
        rpos=rmin+rbinwidth/2 # mid-bin = 0.0+halfbinwidth
        zpos=zmin+zbinwidth/2 # mid-bin = 0.0+halfbinwidth
        print "si : index " + str(si);
		#	if ((int(si) == 3) or (int(si) == 7) or (int(si) == 11)): # only every second "discovered" section is one with data
		#		print "After filter, si : index " + str(si);
        with open(writefiles[int(si)], "a") as writefile:
            writefile.write('z = ' + str(  round(zpos,2)  ) + '\n');
            print "to writefile: " + str(writefile);
            for i, line in enumerate(section[8:]):
                if i < zbins*linesPerZPos:
                    # print("line nr: " + str(i) + "; line content: " + line);
                    if i%linesPerZPos == 0 and i!=0:
                        zpos += zbinwidth
                        rpos=rmin+rbinwidth/2 # mid-bin = 0.0+halfbinwidth
                        writefile.write('z = ' + str(  round(zpos,2)  ) + '\n');
                    for j, fluenceentry in enumerate(line.split()):
                        th2f_fluence[si].Fill(round(rpos,2),round(zpos,2),float(fluenceentry))
                        writefile.write(str(  round(rpos,2)  ) + '\t' + str(fluenceentry) + '\n');
                        rpos+=rbinwidth;
                elif i >= zbins*linesPerZPos + 3:
                    # print("line nr: " + str(i) + "; line content: " + line);
                    if (i-3)%linesPerZPos == 0:
                        if i == zbins*linesPerZPos + 3:
                            rpos=rmin+rbinwidth/2 # mid-bin = 0.0+halfbinwidth
                            zpos=zmin+zbinwidth/2 # mid-bin = 0.0+halfbinwidth
                        else:
                            zpos += zbinwidth
                            rpos=rmin+rbinwidth/2 # mid-bin = 0.0+halfbinwidth
                    for j, errentry in enumerate(line.split()):
                        th2f_fluence[si].SetBinError(int((rpos-rmin)/rbinwidth),int((zpos-zmin)/zbinwidth),th2f_fluence[si].GetBinContent(int((rpos-rmin)/rbinwidth),int((zpos-zmin)/zbinwidth))*float(errentry)*1e-2)
                        rpos+=rbinwidth;
        rpos=rmin+rbinwidth/2 # mid-bin = 0.0+halfbinwidth

        # errstartentry = startentry+(zbins*linesPerZPos)+3;
        # with open(percerrwritefiles[int(si)],"a") as percerrwritefile:
        #     print "to errorbar file: " + str(percerrwritefile)
        #     for ei, eline in enumerate(section[i+3:]):
        #         rpos=rbinwidth/2 # mid-bin = 0.0+halfbinwidth
        #         zpos=zbinwidth/2 # mid-bin = 0.0+halfbinwidth
        #         if ei%linesPerZPos:
        #             zpos += zbinwidth
        #             rpos=rbinwidth/2 # mid-bin = 0.0+halfbinwidth
        #         errstartentry=linesPerZPos*((zpos-zmin-1)/zbinwidth)
        #         if ((ei >= int(errstartentry)) and (ei < errstartentry + int(linesPerZPos))):
        #             for ej, errentry in enumerate(eline.split()):
        #                 percerrwritefile.write(str( round(rpos,2)) + '\t' + str(errentry) + '\n');
        #                 th2f_fluence.SetBinError(th2f_fluence.FindBin(rpos),th2f_fluence.FindBin(zpos),errentry)
        #                 rpos+=rbinwidth;
for th1f in th2f_fluence:
    th1f.Write()
fluence_file.Close()
print(startentry);
print(startentry+linesPerZPos);
#writefile.close();
