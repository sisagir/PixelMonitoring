import cx_Oracle
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import os
import numpy as np
import math
###from numberOfROCs import numberOfRocs
import optparse
from numberOfROCs import *
import collections
import ROOT as rt
import sys

from modules_geom import Module,ROG
from rogring_pc import *
from fillIntLumi import *
from rogchannel_modules import *
from SiPixelDetsUpdatedAfterFlippedChange import *

sys.path.append('../pixmon/')
sys.path.append('../pom/cgi-bin/')

from currents import show_vmon as ivmon
from probes import get_temperatures_local as crp

usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage)
parser.add_option("-s", "--begin-fill", action="store", type="string", dest="beginFill")
parser.add_option("-f", "--end-fill", 	action="store", type="string", dest="endFill")
parser.add_option("-o", "--output-file", 	action="store", type="string", dest="outFile")
parser.add_option("-l", "--layer-tag", 	action="store", type="string", dest="layerTag")
parser.add_option("-t", "--temperature", 	action="store", type="string", dest="temp", default='')
parser.add_option("-p", "--part", 	action="store", type="string", dest="part")
parser.add_option("-g", "--rog", 	action="store", type="string", dest="rog")
parser.add_option("-r", "--ring", 	action="store", type="string", dest="ring")
parser.add_option("-d", "--disk", 	action="store", type="string", dest="disk")
# parser.add_option("-c", "--channel", 	action="store", type="string", dest="channel")
parser.add_option("", "--min20", 	action="store_true", dest="min20")
# parser.add_option("--histo", action="store", type="string", dest="histoName", default="dijet_mass")
(options, args) = parser.parse_args()

sensorMapOld_str=["4I_L1D2MN","4M_L1D2MN","4R_L1D2MN","3I_L2D1MN","3M_L2D1MN","3R_L2D1MN","4I_L2D2PN","4M_L2D2PN","4R_L2D2PN","2I_L3D1MN","2R_L3D1MN","5I_L3D3MN","5R_L3D3MN","1I_L4D2MN","1M_L4D2MN","1R_L4D2MN","6M_L4D3PN","6R_L4D3PN","6I_L4D4MN","6R_L4D4MN","3M_L1D1MF","3I_L1D1MF","3I_L2D1PF","3M_L2D1PF","3R_L2D1PF","2I_L3D1PF","2M_L3D1PF","2R_L3D2MF","2I_L3D2MF","1I_L4D2PF","1M_L4D2PF","1R_L4D2PF","6M_L4D3MF","6R_L4D3MF","4I_L2D2MF","4M_L2D2MF","4R_L2D2MF","6I_L4D4PF","6R_L4D4PF"]
sensorMapNew_str=["4R_L1D2MN","4I_L1D2MN","4M_L1D2MN","1I_L4D2MN","1M_L4D2MN","1R_L4D2MN","6R_L4D3PN","6M_L4D3PN","6I_L4D3PN","2R_L3D1MN","2I_L3D1MN","5R_L3D3MN","5I_L3D3MN","3I_L2D1MN","3M_L2D1MN","3R_L2D1MN","4M_L2D2PN","4R_L2D2PN","6R_L4D4MN","6I_L4D4MN","3I_L1D1MF","3M_L1D1MF","1I_L4D2PF","1M_L4D2PF","1R_L4D2PF","2M_L3D1PF","2I_L3D1PF","2I_L3D2MF","2R_L3D2MF","3I_L2D1PF","3M_L2D1PF","3R_L2D1PF","4M_L2D2MF","4R_L2D2MF","6I_L4D3MF","6M_L4D3MF","6R_L4D3MF","6R_L4D4PF","6I_L4D4PF"]
sensorMapNew=dict(zip(sensorMapOld_str, sensorMapNew_str))
good_sectors = ["BmO", "BmI", "BpO", "BpI"]
broken_sectors = ["PixelBarrel_BpI_S3_LAY3", "PixelBarrel_BpI_S3_LAY4", "PixelBarrel_BpI_S5_LAY4"]
oracleTimeMask = "DD-Mon-YYYY HH24.MI.SS.FF"
pythonTimeMask = "%d-%b-%Y %H.%M.%S.%f"
method=1
layer="layer1"

# pcboard_name="PixelEndcap_BmI_PC_1B"
# rog_channel="PixelEndCap_BmI_D3_ROG2/channel003"

# pcboard_name = options.temp
if options.ring == '1':
	channel = "channel003"
elif options.ring == '2':
	channel = "channel002"
else:
	raise ValueError("Ring number should be 1 or 2!")
part = options.part
disk = int(options.disk)
rog = int(options.rog)
ring = int(options.ring)
rog_channel = part_disk_rog_ring_to_rogchannel_pcboardtemp(part, disk, rog, ring, 'rogchannel')
if options.temp == '':
	pcboard_name = part_disk_rog_ring_to_rogchannel_pcboardtemp(part, disk, rog, ring, 'pcboard')
else:
	pcboard_name = options.temp
print("%s: %s"%("rog_channel",rog_channel))
print("%s: %s"%("pcboard_name",pcboard_name))
# "%s/%s"%(options.rog,channel)
# pcboard_name = rogchannel_to_pcboard(rog_channel)

ppXS = 79.1
conversionFactor=ppXS*10e-15/10e-27

def correctAlias( sensorName ):
	# print "pre correction %s"%sensorName

	# get substrings
	part1 = sensorName[0:16] # PixelBarrel_BmO_ -- part 16
	part2 = sensorName[16:25] # 4I_L1D2MN        -- part

	changed = 0 # change only once

	# change the wrong substring
  	# rebuild sensor name
	if part2 in sensorMapNew:
		part2=sensorMapNew[part2]
	newSensorName = part1 + part2

  	# print "post correction %s"%newSensorName

	return newSensorName

def Ileak_per_module_data(row,outFile):
	Ileak=dict(zip(["L1","L2","L3","L4","D1","D2","D3"],[[],[],[],[],[],[],[]]))
	dIleak=dict(zip(["L1","L2","L3","L4","D1","D2","D3"],[[],[],[],[],[],[],[]]))
	new_tag=""
	help_new_tag_arr=[]
	for l in row:
		# print l
		if "LAY14/channel002" in l[0]:
			new_tag = l[0].rsplit('14/')[0].strip()+ "1"
			Ileak_perROC=float(l[1])/numberOfRocsBarrelPhase1[new_tag]
			if Ileak_perROC is not None: Ileak["L1"].append(Ileak_perROC)
		elif("LAY14/channel003" in l[0]):
			new_tag = l[0].rsplit('14/')[0].strip()+ "4"
			Ileak_perROC=float(l[1])/numberOfRocsBarrelPhase1[new_tag]
			if Ileak_perROC is not None: Ileak["L4"].append(Ileak_perROC)
		elif("LAY23/channel002" in l[0]):
			new_tag = l[0].rsplit('23/')[0].strip()+ "3"
			Ileak_perROC=float(l[1])/numberOfRocsBarrelPhase1[new_tag]
			if Ileak_perROC is not None: Ileak["L3"].append(Ileak_perROC)
		elif("LAY23/channel003" in l[0]):
			help_new_tag_arr.append(new_tag)
			new_tag = l[0].rsplit('23/')[0].strip()+ "2"
			Ileak_perROC=float(l[1])/numberOfRocsBarrelPhase1[new_tag]
			if Ileak_perROC is not None: Ileak["L2"].append(Ileak_perROC)
		elif("_D1_" in l and ("channel002" in l or "channel003" in l)):
			new_tag = l[0].rsplit('1_')[0].strip()+ "1"
			# to be done soon
		elif("_D2_" in l and ("channel002" in l or "channel003" in l)):
			new_tag = l[0].rsplit('2_')[0].strip()+ "2"
			# to be done soon
		elif("_D3_" in l and ("channel002" in l or "channel003" in l)):
			new_tag = l[0].rsplit('3_')[0].strip()+ "3"
			# to be done soon
	# print "help_new_tag_arr=%s"%(help_new_tag_arr)
	# for i,l in enumerate(help_new_tag_arr):
	# 	print type(l)
	# 	outFile.write("%s\t%4.2f\n"%(l,float(Ileak[layerTag][i])))
	# print Ileak["L1"]
	for layer,i in Ileak.iteritems():
		if len(Ileak)>0:
			dIleak[layer] = np.array(Ileak[layer]).std()*16
			Ileak[layer] = np.array(Ileak[layer]).mean()*16
		else:
			Ileak[layer] = 0
			dIleak[layer] = 0

	return {"mean": Ileak, "sigma": dIleak}

# startFillRaw = raw_input("Enter start fill number: ")
# endFillRaw = raw_input("Enter end fill number: ")

startFillRaw = options.beginFill
endFillRaw	 = options.endFill

startFill = int(startFillRaw)
endFill   = int(endFillRaw)

option = "PixelBarrel"

fillNum = startFill
count=0
proFile = open(options.outFile,"w")
zeroCelsius=273.15
corrTemp=3.
# prevTemp=-999.
# def getTimes(db, ):
layerTag=options.layerTag

flukaInput={"L1": 8.9275E-02, "L2": 2.0853E-02, "L3": 1.0350E-02, "L4": 5.6419E-03}

totLumi=0.
fluence_file=rt.TFile.Open("FLUKA/fluence_field.root")
th2f_fluence = fluence_file.Get("fluence_allpart_6500GeV_phase1")

# module_list = []

# for m_name in rogchannel_pc[rog_channel]:
# 	module_list.append(Module(m_name))
# 	module_list[-1].setSize(6.48,1.62,0.0285)
# 	module_list[-1].setPosition(name_pos_map[m_name][0],name_pos_map[m_name][1],name_pos_map[m_name][2])
# 	module_list[-1].setElemVolume(0.1)

my_rog = ROG(rog_channel)

# print(blade.getAverageFluence(th2f_fluence,1))
# exit()
args = collections.namedtuple('args', 'minutes hours seconds starttime stoptime layer disk ring analog digital quantity')
my_iLeak=ivmon.leakageCurrentData()

while fillNum <= endFill:
	goodFillsFile = open('FillInfo_TotLumi.txt', 'r+')

	for row in goodFillsFile.readlines():
		#print "Fill numbers: ", row
		if str(fillNum) + "  " in row:
			print "If condition is satisfied"
			### Opening connection

### Define query to get begin and end time of stable beam for fillnumber specified in input
			query= """
select lhcfill, begintime, endtime
from CMS_RUNTIME_LOGGER.RUNTIME_SUMMARY
where  BEGINTIME IS NOT NULL and lhcfill is not null and lhcfill = :fillNum
"""
### Execute query
			connection = cx_Oracle.connect('cms_trk_r/1A3C5E7G:FIN@cms_omds_adg')
			cursor = connection.cursor()
			cursor.arraysize = 50
			cursor.execute(query, {"fillNum" : fillNum})

			fillTime = cursor.fetchall()

			print "Fill Number: ", fillNum
			begintime = fillTime[0][1]
			beginSTBtime = fillTime[0][1]
			if count == 0:
				proFile.write("BEGINTIME: %s\n"%beginSTBtime)
				proFile.write("delta t\tcorr T\tFl_n\t\tT\tI_leak\tstd I_leak\n")
			endSTBtime = fillTime[0][2]
			print "Start  Time: ", begintime
			#endtime =  begintime + datetime.timedelta(0,600) # 10 min into stable beam
			endtime =  begintime + datetime.timedelta(0,1200) # 20 min into stable beam
			begin20minSTB =  begintime + datetime.timedelta(0,1200) # 20 min into stable beam
			# endtime = endSTBtime
			print "Sta+10 Time: ", endtime
			print "EndSTB Time: ", endSTBtime

	### Define query to get currents for Barrel Pixels


			# query3="""
			# with IDs as (select id, rtrim(dpe_name,'.') as dp, substr(alias,instr(alias,'/',-1)+1) as part from CMS_TRK_DCS_PVSS_COND.aliases, CMS_TRK_DCS_PVSS_COND.dp_name2id where alias like 'PixelBarrel%%PF' and rtrim(CMS_TRK_DCS_PVSS_COND.aliases.dpe_name,'.') = CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname)
			#
			# select part, value_converted, change_date from CMS_TRK_DCS_PVSS_COND.tkplcreadsensor, IDs where IDs.id = CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.DPID and CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date >= :the_start_time AND CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date < :the_end_time order by part, CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date
			# """


			# if method == 1:
			query2 = """
			with IDs as ( select id, substr(alias,instr(alias,'/',-1)+1) as part from CMS_TRK_DCS_PVSS_COND.aliases, CMS_TRK_DCS_PVSS_COND.dp_name2id
			where (substr(alias,instr(alias,'/',-1)+1) like '""" + str(option + "%%" + "PF") + """'
			or substr(alias,instr(alias,'/',-1)+1) like '""" + str(option + "%%" + "PN") + """'
			or substr(alias,instr(alias,'/',-1)+1) like '""" + str(option + "%%" + "MF") + """'
			or substr(alias,instr(alias,'/',-1)+1) like '""" + str(option + "%%" + "MN") + """')
			and rtrim(CMS_TRK_DCS_PVSS_COND.aliases.dpe_name,'.') = CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname
			),
		
			temps as ( select part, max(change_date) as itime from CMS_TRK_DCS_PVSS_COND.tkplcreadsensor, IDs
			where IDs.id = CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.DPID
			and change_date >= :the_start_time
			and change_date <= :the_end_time
			and value_converted is not NULL
			group by part
			)
		
			select IDs.part, value_converted, change_date from CMS_TRK_DCS_PVSS_COND.tkplcreadsensor, IDs, temps
			where IDs.id = CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.DPID
			and change_date >= :the_start_time
			and change_date <= :the_end_time
			and change_date = temps.itime
			and IDs.part = temps.part
			order by part, change_date
			"""
			# else:
			# 	query2 = """
			# 	with IDs as ( select id, alias, since, rtrim(dpe_name,'.') as dp, substr(alias,instr(alias,'/',-1)+1) as part, update_count, CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname as dpname from CMS_TRK_DCS_PVSS_COND.aliases, CMS_TRK_DCS_PVSS_COND.dp_name2id
			# 	where CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname like  '%Pixel%' and  rtrim(CMS_TRK_DCS_PVSS_COND.aliases.dpe_name,'.') = CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname)
			# 	select part, alias, since, update_count, value_converted, change_date , dpname from CMS_TRK_DCS_PVSS_COND.tkplcreadsensor, IDs where IDs.id = CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.DPID and CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date >= :the_start_time  AND CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date < :the_end_time  order by part, CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date
			# 	"""
			# query2 = """WITH ids as
			# (SELECT id, substr(alias,instr(alias,'/',-1)+1) as part
			# FROM cms_trk_dcs_pvss_cond.aliases
			# JOIN cms_trk_dcs_pvss_cond.dp_name2id
			#  ON rtrim(CMS_TRK_DCS_PVSS_COND.aliases.dpe_name,'.') = CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname
			# WHERE REGEXP_LIKE(substr(alias,instr(alias,'/',-1)+1), :name))
			# SELECT part, value_converted, change_date
			# FROM ids
			# JOIN CMS_TRK_DCS_PVSS_COND.tkplcreadsensor ON ids.id = CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.DPID
			# WHERE CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date >= :start_time
			# AND CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date < :stop_time
			# ORDER BY part, CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date
			# """
			# query2_iLeak="""
			# with cables as (
			# select distinct substr(lal.alias,INSTR(lal.alias,  '/', -1, 2)+1)  cable, id dpid, cd from
			# (select max(since) as cd, alias from  cms_trk_dcs_pvss_cond.aliases group by alias ) md, cms_trk_dcs_pvss_cond.aliases lal
			# join cms_trk_dcs_pvss_cond.dp_name2id on dpe_name=concat(dpname,'.')
			# where md.alias=lal.alias and lal.since=cd
			# and (lal.alias like 'CMS_TRACKER/%PixelEndCap%%%%channel00%')
			# ),
			# it as (
			# select dpid, max(change_date) itime from cms_trk_dcs_pvss_cond.fwcaenchannel caen
			# WHERE change_date between to_timestamp(:the_start_time, '""" + oracleTimeMask + """') and to_timestamp(:the_end_time, '""" + oracleTimeMask + """')
			# AND actual_Imon is not NULL
			# group by dpid
			# ),
			# i_mon as (
			# select it.dpid, itime, actual_Imon, actual_Vmon from cms_trk_dcs_pvss_cond.fwcaenchannel caen
			# join it on (it.dpid = caen.dpid and change_date = itime)
			# and actual_Imon is not NULL
			# )
			# select cable, actual_Imon, actual_Vmon, itime from i_mon
			# join cables on (i_mon.dpid=cables.dpid)
			# order by itime
			# """
			# query2_iLeak="""select distinct substr(lal.alias,INSTR(lal.alias,  '/', -1, 2)+1), id from
	        # (select max(since) as cd, alias from  cms_trk_dcs_pvss_cond.aliases group by alias) md, cms_trk_dcs_pvss_cond.aliases lal
	        # join cms_trk_dcs_pvss_cond.dp_name2id on dpe_name=concat(dpname,'.')
	        # where md.alias=lal.alias and lal.since=cd
	        # and (lal.alias like '%PixelEndCap%%%%channel002%')
			# select actual_imon, change_date from cms_trk_dcs_pvss_cond.fwcaenchannel         where change_date between TO_TIMESTAMP('2017-05-24 01:04:38.706363', 'RRRR-MM-DD HH24:MI:SS.FF') and TO_TIMESTAMP('2017-05-24 05:05:30.088863', 'RRRR-MM-DD HH24:MI:SS.FF') and dpid='48629' and actual_imon is not NULL         order by change_date"""
	   #
		# """
		# with IDs as ( select id, alias, since, rtrim(dpe_name,'.') as dp, substr(alias,instr(alias,'/',-1)+1) as part, update_count, CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname as dpname from CMS_TRK_DCS_PVSS_COND.aliases, CMS_TRK_DCS_PVSS_COND.dp_name2id
		# where CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname like  '%Pixel%' and  rtrim(CMS_TRK_DCS_PVSS_COND.aliases.dpe_name,'.') = CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname)
		# select part, alias, since, update_count, value_converted, change_date , dpname from CMS_TRK_DCS_PVSS_COND.tkplcreadsensor, IDs where IDs.id = CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.DPID and CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date >= to_timestamp('""" + str(start_time) + """', 'RRRR-MM-DD HH24:MI:SS.FF') AND CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date < to_timestamp('""" + str(stop_time) + """', 'RRRR-MM-DD HH24:MI:SS.FF') order by part, CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date
		# """
			# print query2
			endtimeBetweenFills=begintime
			temps = []
			count2=0
			jjj=0
			lastTemp=float('nan')
			temps1=[]
			Tdiff=0
			prevTemp=0
			# ============== no beam ===========================
			if count != 0:
				begintime4=begintimeBetweenFills
				begintime2=begintimeBetweenFills
				endtime2=begintimeBetweenFills+datetime.timedelta(0,1200)
				begintime3=begintimeBetweenFills
				endtime3=begintimeBetweenFills
				fileCurrents = "/afs/cern.ch/user/d/dbrzhech/work/ServiceWork/RadDamage/pixelMonitor/CMSSW_9_4_0_pre1/src/PixelMonitoring/txt/"+str(fillNum)+"before"+ "_Tpipe.txt"
				# fcur = open(fileCurrents, "w+")
				if os.path.exists(fileCurrents):
					fcur=open(fileCurrents, "w+")
				else:
					fcur=open(fileCurrents, "w")
				# print query2
				while endtime2 < endtimeBetweenFills:
					# cursor.execute(query2, {"name": name, "start_time" : begintime2, "stop_time" : endtime2})
					# row = cursor.fetchall()

					temps=crp.create_plot(pcboard_name,[begintime2.strftime('%m-%d-%Y %H:%M:%S'),endtime2.strftime('%m-%d-%Y %H:%M:%S')])
					# cursor.execute(query2_iLeak, {"the_start_time" : begintime2, "the_end_time" : endtime2})
					# row_iLeak = cursor.fetchall()
					#
					#               there are some swaped aliases... correct offline in C++ script
					#
					temps1=temps
					# print 'temps1=%s'%temps1
					# for i in xrange(len(row)):
					# 	# sensorName=str(row[i][0])
					# 	sensorName=correctAlias(str(row[i][0]))
					# 	if method==1:
					# 		if layerTag in sensorName and row[i][1] is not None:
					# 			temps.append(row[i][1])
					# 			temps1.append(row[i][1])
					# 	elif method==2:
					# 		if any(substr in row[i][0] for substr in sensorMapOld_str):
					# 			if layerTag in sensorName and row[i][4] is not None:
					# 				temps.append(row[i][4])
					# 				temps1.append(row[i][4])
						# 	fcur.write(str(row[i][0]) + " " + str(row[i][1]) + " " + str(row[i][2])+ "\n")

					# averTemp1=np.array([temps1]).mean()
					averTemp1=temps1

					if averTemp1<-300.:
						Tdiff=0
					else:
						Tdiff=averTemp1-lastTemp
						lastTemp=averTemp1
					if (abs(Tdiff)>3. or (endtime2-begintime4) > datetime.timedelta(2,-1)) and temps > -300:
						if count2==0:
							begintime3=begintimeBetweenFills
						# print type(row[i][2])
						endtime3=endtime2
						averTemp=temps
						# print len(temps) > 0
						timeInterval=(endtime3-begintime3).total_seconds()
						iLeak = -99.
						diLeak = -99.
						proFile.write("%d\t%4.2f\t%4.2f\t%4.2f\t%6.2f\t%6.2f\n"%(timeInterval,averTemp+zeroCelsius,0.00,averTemp+zeroCelsius,iLeak,diLeak))#,begintime3,endtime3,fillNum))
						temps = []
						begintime3=endtime3
						# print "count2 = %s"%count2
						prevTemp=averTemp
						count2+=1
					temps1=[]
					if endtime2-begintime4 > datetime.timedelta(2,-1):
						# print "%s-%s"%(endtime2,begintime4)
						begintime4=endtime2
					begintime2 = endtime2
					endtime2=begintime2+datetime.timedelta(0,1200)
				fcur.write("begintime: %s\n  endtime: %s\n"%(begintimeBetweenFills, endtimeBetweenFills))
				fcur.write(str(endtimeBetweenFills-begintimeBetweenFills)+"\n")
				fcur.write((str(round((endtimeBetweenFills-begintimeBetweenFills).total_seconds()))).rstrip(".0"))
				fcur.close()

				# cursor.execute(query2, {"name": name, "start_time" : begintime2, "stop_time" : endtimeBetweenFills})
				# row = cursor.fetchall()
				# cursor.execute(query2_iLeak, {"the_start_time" : begintime2, "the_end_time" : endtimeBetweenFills})
				# row_iLeak = cursor.fetchall()
				# myArgs = args(layer=None, seconds=0, hours=0, stoptime=begintime2, starttime=endtime2, digital=False, ring='2', disk=None, minutes=10, analog=False, quantity='imon')
				# print(query2_iLeak)
				temps=crp.create_plot(pcboard_name,[begintime2.strftime('%m-%d-%Y %H:%M:%S'),endtimeBetweenFills.strftime('%m-%d-%Y %H:%M:%S')])
				temps1=temps
				# for i in xrange(len(row)):
				# 	sensorName=correctAlias(str(row[i][0]))
				# 	if method == 1:
				# 		if layerTag in sensorName and row[i][1] is not None:
				# 			temps.append(row[i][1])
				# 	elif method == 2:
				# 		if any(substr in row[i][0] for substr in sensorMapOld_str):
				# 			if layerTag in sensorName and row[i][4] is not None:
				# 				temps.append(row[i][4])

				if temps > -300:
					averTemp=temps
					trueTemp=temps
					prevTemp=trueTemp
				else:
					averTemp=25
					trueTemp=-274.15 #means no reading
					trueTemp=prevTemp
				timeInterval=(endtimeBetweenFills-begintime3).total_seconds()
				iLeak = -99.
				diLeak = -99.
				proFile.write("%d\t%4.2f\t%10d\t%4.2f\t%6.2f\t%6.2f\n"%(timeInterval,averTemp+zeroCelsius,0,trueTemp+zeroCelsius,iLeak,diLeak))#,begintime3,endtimeBetweenFills,fillNum))
				# prevTemp=np.array([temps]).mean()

			fileCurrents = "/afs/cern.ch/user/d/dbrzhech/work/ServiceWork/RadDamage/pixelMonitor/CMSSW_9_4_0_pre1/src/PixelMonitoring/txt/"+str(fillNum) + "_Tpipe.txt"
			if os.path.exists(fileCurrents):
				fcur=open(fileCurrents, "w+")
			else:
				# os.system("touch %s"%fileCurrents)
				fcur=open(fileCurrents, "w")

			# ============== stable beam ===========================
			temps = []
			# print "begintime_str = %s"%(beginSTBtime.strftime( pythonTimeMask ))
			# print "endtime_str = %s"%(endSTBtime.strftime( pythonTimeMask ))
			# cursor.execute(query2_iLeak, {"the_start_time" : beginSTBtime.strftime( pythonTimeMask ), "the_end_time" : endSTBtime.strftime( pythonTimeMask )})
			# row_iLeak = cursor.fetchall()
			# row_iLeak=open("%s_Barrel.txt"%fillNum,"r")
			# row_iLeak=row_iLeak.readlines()
			# print row_iLeak
			# for i,l in enumerate(row_iLeak):
			# 	row_iLeak[i]=l.rstrip("\n").split("   ")
			# print row_iLeak
			# outFile=open("iLeak_test/%s_testRunProfile_iLeak.txt"%fillNum,"w")
			# iLeak=Ileak_per_module_data(row_iLeak,outFile)["mean"][layerTag]
			# diLeak=Ileak_per_module_data(row_iLeak,outFile)["sigma"][layerTag]
			# outFile.close()

			# while endtime < endSTBtime:
				# begintime.strftime('%m-%d-%Y %H:%M:%S')
				# temps=crp.create_plot([begintime.strftime('%m-%d-%Y %H:%M:%S'),endtime.strftime('%m-%d-%Y %H:%M:%S')])
				# temps1=temps
				# cursor.execute(query2, {"name": name, "start_time" : begintime, "stop_time" : endtime})
				# row = cursor.fetchall()
				#
				#                       there are some swaped aliases... correct offline in C++ script
				#
				# for i in xrange(len(row)):
				# 	# print "====> ", str(row[i][0]) + "   " + str(row[i][1]) + "   " + str(row[i][2])+   "\n"
				# 	sensorName=correctAlias(str(row[i][0]))
				# 	if method == 1:
				# 		if layerTag in sensorName and row[i][1] is not None:
				# 			temps.append(row[i][1])
				# 	elif method == 2:
				# 		if any(substr in row[i][0] for substr in sensorMapOld_str):
				# 			if layerTag in sensorName and row[i][4] is not None:
				# 				temps.append(row[i][4])
				# 	fcur.write(str(row[i][0]) + " " + str(row[i][1]) + " " + str(row[i][2])+ "\n")

				# begintime = endtime
				# endtime = begintime + datetime.timedelta(0,1200)
			fcur.write("begintime: %s\nendtime: %s\n"%(beginSTBtime,endSTBtime))
			fcur.write((str(round((endSTBtime-beginSTBtime).total_seconds()))).rstrip(".0"))
			fcur.close()
			# print 'brilcalc lumi --begin "%02d/%02d/%02d %02d:%02d:%02d" --end "%02d/%02d/%02d %02d:%02d:%02d" -u /nb --output-style csv'%(beginSTBtime.month, beginSTBtime.day,    beginSTBtime.year-2000,
			# 																												beginSTBtime.hour,  beginSTBtime.minute, beginSTBtime.second     ,
			# 																												endSTBtime.month,   endSTBtime.day,      endSTBtime.year-2000  ,
			# 																												endSTBtime.hour,    endSTBtime.minute,   endSTBtime.second        )
			

			#==== 20 mins after STB ====
			is_fill_mt20min = (begin20minSTB < endSTBtime) and options.min20
			if is_fill_mt20min:
			# if False:
				# brilcalc_out=os.popen('brilcalc lumi --begin "%02d/%02d/%02d %02d:%02d:%02d" --end "%02d/%02d/%02d %02d:%02d:%02d" -u /fb --output-style csv'%(beginSTBtime.month, beginSTBtime.day,    beginSTBtime.year-2000,
																																# beginSTBtime.hour,  beginSTBtime.minute, beginSTBtime.second     ,
																																# begin20minSTB.month,   begin20minSTB.day,      begin20minSTB.year-2000  ,
																																# begin20minSTB.hour,    begin20minSTB.minute,   begin20minSTB.second        ))
				
				# brilcalc_string=brilcalc_out.read()
				# brilcalc_arr_str=brilcalc_string.split("\n")
				# lumi=""
				# corrTemp=0
				# for substr_brilcalc in brilcalc_arr_str:
				# 	if substr_brilcalc.find("#1") == 0:
				# 		lumi=substr_brilcalc.split(",")[-2]
				# 		# if "L1" or "L2" or "L3" in str(row[i][0]):
				# 		# 	corrTemp=3
				# 		# else:
				# 		# 	corrTemp=4
				# 	elif substr_brilcalc.find("#0") == 0:
				# 		lumi="0"
				# 		# corrTemp=0
				lumi = fillLumi[fillNum]['20mins']
				print "lumi=%s\n"%lumi
				lumi *= 1e-6

				# cursor.execute(query2, {"name": name, "start_time" : begintime, "stop_time" : endSTBtime})
				# row = cursor.fetchall()
				# cursor.execute(query2_iLeak, {"the_start_time" : begintime, "the_end_time" : endSTBtime})
				# row_iLeak = cursor.fetchall()
				# print temps
				
				temps=crp.create_plot(pcboard_name,[beginSTBtime.strftime('%m-%d-%Y %H:%M:%S'),begin20minSTB.strftime('%m-%d-%Y %H:%M:%S')])
				# print 'temps = %s'%temps
				myArgs = args(layer=None, seconds=0, hours=0, starttime=beginSTBtime.strftime('%Y-%m-%d %H-%M-%S'), stoptime=begin20minSTB.strftime('%Y-%m-%d %H-%M-%S'), digital=False, ring='1', disk=None, minutes=10, analog=False, quantity='imon')
				temps1=temps
				iLeak=-99.
				diLeak=-99.
				iLeak=my_iLeak.get_ivmon(connection,myArgs,rog_channel)
				# for t in row:
				# 	temps.append(t[1])
				# 	temps1.append(t[1])
				# for i in xrange(len(row)):
				# 	sensorName=correctAlias(str(row[i][0]))
				# 	if method == 1:
				# 		if layerTag in sensorName and row[i][1] is not None:
				# 			temps.append(row[i][1])
				# 	elif method == 2:
				# 		if any(substr in row[i][0] for substr in sensorMapOld_str):
				# 			if layerTag in sensorName and row[i][4] is not None:
				# 				temps.append(row[i][4])
				# print temps
				# for l in row:
					# print l[0]
					# if l[0][16:25] in sensorMapOld_str:
						# sensor_name=correctAlias(l[0])
						# if l[0] == sensor_name:
						# print "%40s\t%4.2f\n"%(l[0],l[4])

				if temps > -300:
					# averTemp=np.array([temps]).mean()
					# trueTemp=np.array([temps]).mean()
					averTemp=temps
					trueTemp=temps
					prevTemp=trueTemp
				else:
					averTemp=-8.5
					# trueTemp=-274.15 #means no reading
					trueTemp=prevTemp
				timeInterval=(begin20minSTB-beginSTBtime).total_seconds()
				totLumi+=float(lumi)
				# proFile.write("%d\t%4.2f\t%10d\t%4.2f\t%6.2f\t%6.2f\n"%(timeInterval,averTemp+zeroCelsius+corrTemp,float(lumi)/float(timeInterval),trueTemp+zeroCelsius,iLeak,diLeak))#,beginSTBtime,endSTBtime,fillNum))
				proFile.write("%d\t%4.2f\t%10d\t%4.2f\t%6.2f\t%6.2f\n"%(timeInterval,averTemp+zeroCelsius+corrTemp,float(lumi),trueTemp+zeroCelsius,iLeak,diLeak))#,beginSTBtime,endSTBtime,fillNum))
			else:
				begin20minSTB = beginSTBtime
				# lumi = fillLumi[fillNum]['20mins'] + fillLumi[fillNum]['after20mins']


			#==== beginSTB+20 mins to endSTB ====

			# brilcalc_out=os.popen('brilcalc lumi --begin "%02d/%02d/%02d %02d:%02d:%02d" --end "%02d/%02d/%02d %02d:%02d:%02d" -u /fb --output-style csv'%(begin20minSTB.month, begin20minSTB.day,    begin20minSTB.year-2000,
			# 																												begin20minSTB.hour,  begin20minSTB.minute, begin20minSTB.second     ,
			# 																												endSTBtime.month,   endSTBtime.day,      endSTBtime.year-2000  ,
			# 																												endSTBtime.hour,    endSTBtime.minute,   endSTBtime.second        ))
			# brilcalc_string=brilcalc_out.read()
			# brilcalc_arr_str=brilcalc_string.split("\n")
			# lumi=""
			# corrTemp=0
			# for substr_brilcalc in brilcalc_arr_str:
			# 	if substr_brilcalc.find("#1") == 0:
			# 		lumi=substr_brilcalc.split(",")[-2]
			# 		# if "L1" or "L2" or "L3" in str(row[i][0]):
			# 		# 	corrTemp=3
			# 		# else:
			# 		# 	corrTemp=4
			# 	elif substr_brilcalc.find("#0") == 0:
			# 		lumi="0"
					# corrTemp=0
			if options.min20: lumi = fillLumi[fillNum]['after20mins']
			else:
				if begin20minSTB < endSTBtime:
					lumi = fillLumi[fillNum]['20mins'] + fillLumi[fillNum]['after20mins']
				else:
					lumi = fillLumi[fillNum]['after20mins']

			print "lumi=%s\n"%lumi
			lumi *= 1e-6
			# cursor.execute(query2, {"name": name, "start_time" : begintime, "stop_time" : endSTBtime})
			# row = cursor.fetchall()
			# cursor.execute(query2_iLeak, {"the_start_time" : begintime, "the_end_time" : endSTBtime})
			# row_iLeak = cursor.fetchall()
			# print temps
			temps=crp.create_plot(pcboard_name, [begin20minSTB.strftime('%m-%d-%Y %H:%M:%S'),endSTBtime.strftime('%m-%d-%Y %H:%M:%S')])
			# print 'temps = %s'%temps
			myArgs = args(layer=None, seconds=0, hours=0, starttime=begin20minSTB.strftime('%Y-%m-%d %H-%M-%S'), stoptime=endSTBtime.strftime('%Y-%m-%d %H-%M-%S'), digital=False, ring='1', disk=None, minutes=10, analog=False, quantity='imon')
			temps1=temps
			iLeak=-99.
			diLeak=-99.
			iLeak=my_iLeak.get_ivmon(connection,myArgs,rog_channel)
			# for t in row:
			# 	temps.append(t[1])
			# 	temps1.append(t[1])
			# for i in xrange(len(row)):
			# 	sensorName=correctAlias(str(row[i][0]))
			# 	if method == 1:
			# 		if layerTag in sensorName and row[i][1] is not None:
			# 			temps.append(row[i][1])
			# 	elif method == 2:
			# 		if any(substr in row[i][0] for substr in sensorMapOld_str):
			# 			if layerTag in sensorName and row[i][4] is not None:
			# 				temps.append(row[i][4])
			# print temps
			# for l in row:
				# print l[0]
				# if l[0][16:25] in sensorMapOld_str:
					# sensor_name=correctAlias(l[0])
					# if l[0] == sensor_name:
					# print "%40s\t%4.2f\n"%(l[0],l[4])

			if temps > -300:
				# averTemp=np.array([temps]).mean()
				# trueTemp=np.array([temps]).mean()
				averTemp=temps
				trueTemp=temps
				prevTemp=trueTemp
			else:
				averTemp=-8.5
				# trueTemp=-274.15 #means no reading
				trueTemp=prevTemp
			timeInterval=(endSTBtime-begin20minSTB).total_seconds()
			totLumi+=float(lumi)
			# proFile.write("%d\t%4.2f\t%4.2f\t%4.2f\t%6.2f\t%6.2f\n"%(timeInterval,averTemp+zeroCelsius+corrTemp,float(lumi)/float(timeInterval),trueTemp+zeroCelsius,iLeak,diLeak))#,beginSTBtime,endSTBtime,fillNum))
			proFile.write("%d\t%4.2f\t%4.2f\t%4.2f\t%6.2f\t%6.2f\n"%(timeInterval,averTemp+zeroCelsius+corrTemp,float(lumi),trueTemp+zeroCelsius,iLeak,diLeak))#,beginSTBtime,endSTBtime,fillNum))
			
			begintime2=endSTBtime
			begintimeBetweenFills=endSTBtime
			count +=1
			connection.close()
	fillNum = fillNum + 1
proFile.write("TOTAL LUMI: %s fb-1"%totLumi)
proFile.close()
