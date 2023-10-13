import cx_Oracle
import datetime
import time

import cx_Oracle
import datetime as dt
from utils import generalUtils as gUtl
from inspect import cleandoc as multi_line_str
from pathlib import Path

Partitions = {"TIBTID":"195978","TOB":"195980","TECminus":"195982","TECplus":"195984"}

output_directory = "data_tkstates"
Path(output_directory).mkdir(parents=True, exist_ok=True)

### Opening connection
connection = cx_Oracle.connect('<TABLE_TO_CONNECT>')
cursor = connection.cursor()
cursor.arraysize=50

query="""
SELECT CHANGE_DATE, FSM_CURRENTSTATE from "CMS_DCS_ENV_PVSS_COND"."_FWFSMOBJECT" where DPID = :the_partition and CHANGE_DATE > '01-SEP-2023'
"""
		      
print(query)
for Partition in Partitions.keys():

	print("Partition:%s" % (Partition) )
	cursor.execute(query, {"the_partition" : Partitions[Partition]})
	output = cursor.fetchall()
	
	states_file_name = output_directory + "/" + Partition + "_tkstates.txt"
	output_file = open(states_file_name, "w+")
	for row in output:
		time_, state  = row
		line = "%s   %s   %s\n" % (time_, int(time.mktime(time_.timetuple())), state)
		output_file.write(line)
		
	output_file.close()
	print("%s saved." % states_file_name)

connection.close()

