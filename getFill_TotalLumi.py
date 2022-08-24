import cx_Oracle
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
#from numberOfROCs import numberOfRocs
from .numberOfROCs import numberOfRocsBarrelPhase1

from . import utils as utl


password = utl.get_database_password()
database_name = "cms_omds_adg"
user_name = "cms_trk_r"
connection = cx_Oracle.connect('%s/%s@%s' % (user_name, password, database_name))


cursor = connection.cursor()
cursor.arraysize=50

# and integratedlumi is not null and integratedlumi > 0 
# and integratedlumi is not null and integratedlumi > 0 
query= """
with i_lumi as (
  select fillnum fn from CMSRUNSUMMARY
  where STARTTIME IS NOT NULL and fillnum is not null and (fillnum < 3474 or fillnum > 3564)
  order by fillnum
),
with i_lumi as (
  select fillnum fn from CMSRUNSUMMARY
  where STARTTIME IS NOT NULL and fillnum is not null and (fillnum < 3474 or fillnum > 3564)
  order by fillnum
),

good_fills as (
  select fillnum, starttime, stoptime from CMS_RUNTIME_LOGGER
  where STARTTIME IS NOT NULL and fillnum is not null  and (fillnum < 3474 or fillnum > 3564)
  order by fillnum
)

select good_fills.fillnum, starttime, stoptime, sum(il) totlumi from good_fills, i_lumi
 where good_fills.fillnum>fn
 group by good_fills.fillnum, good_fills.starttime, good_fills.stoptime
 order by good_fills.fillnum
"""

cursor.execute(query)

fillrow = cursor.fetchall()

print("Fill    BeginTime        EndTime       TotLumi")

outfileName = "FillInfo_TotLumi.txt"
ofile = open(outfileName, "w+")

for i in range(len(fillrow)):
    print(fillrow[i][0],"   ", fillrow[i][1],"   ",fillrow[i][2],"    ",fillrow[i][3])
    ofile.write( str(fillrow[i][0])+ "  " + str(fillrow[i][1]) + " " + str(fillrow[i][2]) + " TotLumi: " + str(fillrow[i][3]) + "\n")

ofile.close()
    
