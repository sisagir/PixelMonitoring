import cx_Oracle
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
###from numberOfROCs import numberOfRocs


startFillRaw = input("Enter start fill number: ")
endFillRaw = input("Enter end fill number: ")

startFill = int(startFillRaw)
endFill = int(endFillRaw)

fillNum = startFill

while fillNum <= endFill:
	goodFillsFile = open('FillInfo_TotLumi.txt', 'r+')

	for row in goodFillsFile.readlines():
		#print "Fill numbers: ", row
		if str(fillNum) + "  " in row:
			print("If condition is satisfied")
			### Opening connection
			connection = cx_Oracle.connect('cms_trk_r/1A3C5E7G:FIN@cms_omds_adg')
			cursor = connection.cursor()
			cursor.arraysize=50

### Define query to get begin and end time of stable beam for fillnumber specified in input
			query= """
select lhcfill, begintime, endtime
from CMS_RUNTIME_LOGGER.RUNTIME_SUMMARY
where  BEGINTIME IS NOT NULL and lhcfill is not null and lhcfill = :fillNum
"""
### Execute query
			cursor.execute(query, {"fillNum" : fillNum})

			fillTime = cursor.fetchall()

			print("Fill Number: ", fillNum)
			begintime = fillTime[0][1]
			endSTBtime= fillTime[0][2]
			print("Begin Time: ", begintime)
                        #endtime = endSTBtime
			endtime =  begintime + datetime.timedelta(0,600)
			print("End Time: ", endtime)
    
	
	### Define query to get currents for Barrel Pixels
       	

			query2="""
with IDs as (select id, rtrim(dpe_name,'.') as dp, substr(alias,instr(alias,'/',-1)+1) as part from CMS_TRK_DCS_PVSS_COND.aliases, CMS_TRK_DCS_PVSS_COND.dp_name2id
where alias like '%Pixel%Air' and rtrim(CMS_TRK_DCS_PVSS_COND.aliases.dpe_name,'.') = CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname)

select part, value_converted, change_date from CMS_TRK_DCS_PVSS_COND.tkplcreadsensor, IDs
where IDs.id = CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.DPID and
CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date >= :the_start_time
AND CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date < :the_end_time
order by part, CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date

"""

			print(query2)
			print(begintime)
			print(endtime)
			cursor.execute(query2, {"the_start_time" : begintime, "the_end_time" : endtime})
			row = cursor.fetchall()
#			
			fileCurrents = "txt/"+str(fillNum) + "_TAIR.txt"
			fcur = open(fileCurrents, "w+")
			
			for i in range(len(row)):
				print("====> ", str(row[i][0]) + "   " + str(row[i][1]) + "   " + str(row[i][2])+ "\n")
				fcur.write(str(row[i][0]) + "   " + str(row[i][1]) + "   " + str(row[i][2])+ "\n")
				
			fcur.close()
	
	    
			connection.close()
	
			
	fillNum = fillNum + 1


