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
select lhcfill, begintime, endtime from CMS_RUNTIME_LOGGER.RUNTIME_SUMMARY
 where  BEGINTIME IS NOT NULL and lhcfill is not null
 order by lhcfill
"""

cursor.execute(query)

fillrow = cursor.fetchall()

print "Fill    BeginTime        EndTime"

outfileName = "FillInfo.txt"
ofile = open(outfileName, "w+")

for i in xrange(len(fillrow)):
    print fillrow[i][0],"   ", fillrow[i][1],"   ",fillrow[i][2]
    ofile.write( str(fillrow[i][0])+ "  " + str(fillrow[i][1]) + " " + str(fillrow[i][1]) + "\n")

ofile.close()
    
