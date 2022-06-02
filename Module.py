import collections
import ROOT as rt
import sys
import math
import os
class Module:
    def __init__(self,name):
        self.module_position = collections.namedtuple('module_position', 'R0 L0 Z0')
        self.module_size = collections.namedtuple('module_size', 'dR dL dZ')
        self.position = self.module_position(0,0,0)
        self.size = self.module_size(0,0,0)
        self.name = name
        ppXS = 79.1
        self.conversionFactor=ppXS*10e-15/10e-27
    def get_name(self):
        return self.name
    def getVolume(self):
        return self.size.dR*self.size.dL*self.size.dZ
    def getElemVolume(self,dr):
        return self.dr*self.size.dL*self.size.dZ
    def setPosition(self,R0,L0,Z0):
        self.position = self.module_position(R0,L0,Z0)
    def setSize(self,dR,dL,dZ):
        self.size = self.module_size(dR,dL,dZ)
    def setElemVolume(self,dr):
        self.dr=dr
    def getAverageFluence(self,fluence_th2f,lumi):
        R0=self.position.R0-self.size.dR/2.+self.dr/2.
        R=R0
        phi_eq=0
        while R<self.position.R0+self.size.dR/2.:
            # print "fluence(%s) = %s"%(R,fluence_th2f.GetBinContent(fluence_th2f.GetXaxis().FindBin(R),fluence_th2f.GetYaxis().FindBin(self.position.Z0)))
            phi_eq+=fluence_th2f.GetBinContent(fluence_th2f.GetXaxis().FindBin(R),fluence_th2f.GetYaxis().FindBin(self.position.Z0))
            R+=self.dr
        return self.dr/self.size.dR*phi_eq*self.conversionFactor*lumi

def getAverageFluenceSum(list_of_modules,fluence_th2f,lumi):
	fluence = 0
	for m in list_of_modules:
		fluence+=m.getAverageFluence(fluence_th2f,lumi)
	return fluence
