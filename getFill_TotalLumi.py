import cx_Oracle
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
#from numberOfROCs import numberOfRocs
from numberOfROCs import numberOfRocsBarrelPhase1



connection = cx_Oracle.connect('cms_trk_r/1A3C5E7G:FIN@cms_omds_adg')


cursor = connection.cursor()
cursor.arraysize=50

query= """
with i_lumi as (
  select lhcfill fn, integratedlumi il from CMS_RUNTIME_LOGGER.RUNTIME_SUMMARY
  where BEGINTIME IS NOT NULL and lhcfill is not null and (lhcfill < 3474 or lhcfill > 3564) and integratedlumi is not null and integratedlumi > 0 
  order by lhcfill
),

good_fills as (
  select lhcfill, begintime, endtime, integratedlumi from CMS_RUNTIME_LOGGER.RUNTIME_SUMMARY
  where BEGINTIME IS NOT NULL and lhcfill is not null  and (lhcfill < 3474 or lhcfill > 3564) and integratedlumi is not null and integratedlumi > 0 
  order by lhcfill
)

select good_fills.lhcfill, begintime, endtime, sum(il) totlumi from good_fills, i_lumi
 where good_fills.lhcfill>fn
 group by good_fills.lhcfill, good_fills.begintime, good_fills.endtime
 order by good_fills.lhcfill
"""

cursor.execute(query)

fillrow = cursor.fetchall()

print "Fill    BeginTime        EndTime       TotLumi"

outfileName = "FillInfo_TotLumi.txt"
ofile = open(outfileName, "w+")

for i in xrange(len(fillrow)):
    print fillrow[i][0],"   ", fillrow[i][1],"   ",fillrow[i][2],"    ",fillrow[i][3]
    ofile.write( str(fillrow[i][0])+ "  " + str(fillrow[i][1]) + " " + str(fillrow[i][2]) + " TotLumi: " + str(fillrow[i][3]) + "\n")

ofile.close()
    
