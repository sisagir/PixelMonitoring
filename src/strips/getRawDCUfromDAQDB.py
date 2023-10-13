import cx_Oracle
import datetime as dt
import time
from utils import generalUtils as gUtl
from inspect import cleandoc as multi_line_str
from pathlib import Path

startFillRaw = 9095#raw_input("Enter start fill number: ")
endFillRaw = 9248#raw_input("Enter end fill number: ")

output_directory = "data_DCU_raw"
Path(output_directory).mkdir(parents=True, exist_ok=True)

startFill = int(startFillRaw)
endFill = int(endFillRaw)

python_time_mask = "%d-%b-%Y %H.%M.%S.%f"
oracle_time_mask = "DD-Mon-YYYY HH24.MI.SS.FF"
### Opening connection
connection = cx_Oracle.connect('<TABLE_TO_CONNECT>')
cursor = connection.cursor()
cursor.arraysize=50

fills_info = gUtl.get_fill_info("../fills_info/data/fills_info/fills.csv")
good_fills = fills_info.fill_number.tolist()

for fill in range(startFill, endFill+1):
	if not fill in good_fills: continue
	fill_info = fills_info[fills_info.fill_number == fill]
	if len(fill_info) != 1:
		print("Error!")
		exit(0)
	begin_time = dt.datetime.fromisoformat(fill_info.start_stable_beam.tolist()[0])
	end_time = dt.datetime.fromisoformat(fill_info.end_stable_beam.tolist()[0])
	delay = dt.timedelta(0, 7200)
	if (end_time - begin_time) < delay:
		measurement_time = end_time
	else:
		measurement_time = begin_time + delay
	#begin_unix_timestamp=int(time.mktime(begin_time.timetuple()))
	#end_unix_timestamp=int(time.mktime(end_time.timetuple()))
	#measurement_unix_timestamp=int(time.mktime(measurement_time.timetuple()))
	begin_unix_timestamp = int( (begin_time - dt.datetime(1970, 1, 1, 0, 0, 0)).total_seconds() )
	end_unix_timestamp = int( (end_time - dt.datetime(1970, 1, 1, 0, 0, 0)).total_seconds() )
	measurement_unix_timestamp = int( (measurement_time - dt.datetime(1970, 1, 1, 0, 0, 0)).total_seconds() )
	
	# The end_time has to be begin_time + 10 minutes (or 20?) because the 
	# currents that will be read are the last within the begin_time to
	# end_time time window, such that it is after thermal equilibrium.
	# The time window has to be large enough to get data
	
	query=multi_line_str("""
		WITH CheckTime AS (
			SELECT dcuhardid, max(dcutimestamp) itime 
			FROM cms_trk_tkcc.dcuchanneldata dcud
			WHERE channel0 is not null
			AND dcud.dcutimestamp  >= '{the_start_time}'
			AND dcud.dcutimestamp  < '{the_end_time}'
			GROUP BY dcuhardid
		)
		SELECT DISTINCT dcui.detid, dcud.channel0, dcud.channel3
		FROM cms_trk_tkcc.dcuchanneldata dcud, cms_trk_tkcc.dcuinfo dcui, CheckTime
		WHERE dcud.dcuhardid=dcui.dcuhardid
		AND dcud.dcutimestamp = CheckTime.itime
		AND CheckTime.dcuhardid = dcud.dcuhardid
		AND dcud.dcutype = 'FEH'
		""".format(
				the_start_time=begin_unix_timestamp,
				the_end_time=end_unix_timestamp,
		)
	)
	
	print("fill:%s" % (fill) )
	print("begin_time:%s, end_time:%s, measurement_time:%s" % (begin_time,end_time,measurement_time) )
	print("begin_unix_timestamp:%s, end_unix_timestamp:%s, measurement_unix_timestamp:%s" % (begin_unix_timestamp,end_unix_timestamp,measurement_unix_timestamp) )
	cursor.execute(query)
	output = cursor.fetchall()
	
	currents_file_name = output_directory + "/" + str(fill) + "_DCU_raw.txt"
	output_file = open(currents_file_name, "w+")
	for row in output:
		cable, temp, i_mon  = row
		line = "%s   %s   %s\n" % (cable, temp, i_mon)
		output_file.write(line)
		
	output_file.close()
	print("%s saved." % currents_file_name)

connection.close()

