import collections
import utils.SiPixelDetsUpdatedAfterFlippedChange as BFPix_pos
import utils.rogchannel_modules as rog_mod


class Module(object):
	#add module as an input
	def __init__(self,name):
		self.module_position = collections.namedtuple('module_position', 'R0 L0 Z0')
		self.module_size = collections.namedtuple('module_size', 'dR dL dZ')
		self.name = name
		pos = BFPix_pos.name_pos_map[self.name]
		self.position = self.module_position(pos[0],pos[1],pos[2])
		self.size = self.module_size(6.48, 1.62, 0.0285)
        # TODO: Check those hard-coded numbers!
		ppXS = 79.1
		self.conversionFactor=ppXS*10e-15/10e-27
		self.dr = 0.1

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
			# print "%s: fluence(%s) = %s"%(self.name,R,fluence_th2f.GetBinContent(fluence_th2f.GetXaxis().FindBin(R),fluence_th2f.GetYaxis().FindBin(self.position.Z0)))
			phi_eq+=fluence_th2f.GetBinContent(fluence_th2f.GetXaxis().FindBin(R),fluence_th2f.GetYaxis().FindBin(self.position.Z0))
			R+=self.dr
		return self.dr/self.size.dR*phi_eq*self.conversionFactor*lumi

class ROG(object):
	#add ROG as an input
	def __init__(self, rog_name):
		self.rog_name = rog_name
		self.rog = rog_mod.rogchannel_pc[rog_name]
        # TODO: Check those hard-coded numbers!
		ppXS = 79.1
		self.conversionFactor=ppXS*10e-15/10e-27
		self.list_of_modules = []
		for module_name in self.rog:
			self.list_of_modules.append(Module(module_name))

	def getAverageFluenceSum(self,fluence_th2f,lumi):
		fluence = 0
		for m in self.list_of_modules:
			fluence+=m.getAverageFluence(fluence_th2f,lumi)
		return fluence

	def getFluenceNearestSlice(self,fluence_th2f,aver_phi):
		my_mod = self.list_of_modules[0]
		phi_eq = self.conversionFactor*aver_phi/(self.getAverageFluenceSum(fluence_th2f,1.))*fluence_th2f.GetBinContent(fluence_th2f.GetXaxis().FindBin(my_mod.position.R0-my_mod.size.dR/2.+my_mod.dr/2.), fluence_th2f.GetYaxis().FindBin(my_mod.position.Z0))*len(self.list_of_modules)
		return phi_eq
