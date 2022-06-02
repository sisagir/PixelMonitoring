import cx_Oracle
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import optparse 




usage = 'usage: %prog -br BarrelOrEndCap'
parser = optparse.OptionParser(usage)
#parser.add_option('-r', '--run', dest='run', type='int', help='Number of the run to analyze')
parser.add_option("","--BarrelOrEndCap",dest="BarrelOrEndCap",type="string",default="Barrel",help="Indicate if you wish to access current informations for BPix or FPix. Allowed choices: Barrel, EndCap.")

(opt, args) = parser.parse_args()


BarrelOrEndCap = opt.BarrelOrEndCap

startFillRaw = raw_input("Enter start fill number: ")
endFillRaw = raw_input("Enter end fill number: ")

startFill = int(startFillRaw)
endFill = int(endFillRaw)

fillNum = startFill

pythonTimeMask = "%d-%b-%Y %H.%M.%S.%f"
oracleTimeMask = "DD-Mon-YYYY HH24.MI.SS.FF"

while fillNum <= endFill:
    
        #print "==> Loop begin: FillNumber: ", fillNum
        goodFillsFile = open('FillInfo_TotLumi.txt', 'r+')
        for row in goodFillsFile:
          if str(fillNum) + "  " in row:
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

              print "Fill Number: ", fillNum
              begintime = fillTime[0][1]
              endSTBtime = fillTime[0][2]
              print "Begin Time: ", begintime
              endtime =  begintime + datetime.timedelta(0,600)
              print "End Time: ", endtime
              begintime_str = begintime.strftime( pythonTimeMask )
              endtime_str = endtime.strftime( pythonTimeMask )

### Define query to get currents for Barrel Pixels

              query2="""
with cables as (
  select distinct substr(lal.alias,INSTR(lal.alias,  '/', -1, 2)+1)  cable, id dpid, cd from
    (select max(since) as cd, alias from  cms_trk_dcs_pvss_cond.aliases group by alias ) md, cms_trk_dcs_pvss_cond.aliases lal
  join cms_trk_dcs_pvss_cond.dp_name2id on dpe_name=concat(dpname,'.')
  where md.alias=lal.alias and lal.since=cd
  and (lal.alias like 'CMS_TRACKER/%Pixel%/channel00%')
),
it as (
  select dpid, max(change_date) itime from cms_trk_dcs_pvss_cond.fwcaenchannel caen
  WHERE change_date between to_timestamp(:the_start_time, '""" + oracleTimeMask + """') and to_timestamp(:the_end_time, '""" + oracleTimeMask + """')
  AND actual_Imon is not NULL
  group by dpid
),
i_mon as (
  select it.dpid, itime, actual_Imon, actual_Vmon from cms_trk_dcs_pvss_cond.fwcaenchannel caen
  join it on (it.dpid = caen.dpid and change_date = itime)
  and actual_Imon is not NULL
)
select cable, actual_Imon, actual_Vmon, itime from i_mon
join cables on (i_mon.dpid=cables.dpid)
order by itime
"""

              cursor.execute(query2, {"the_start_time" : begintime_str, "the_end_time" : endtime_str})
              row = cursor.fetchall()

              fileCurrents = str(fillNum) + "_" + BarrelOrEndCap + ".txt"
              fcur = open(fileCurrents, "w+")
              for i in xrange(len(row)):

                      if not BarrelOrEndCap in row[i][0]:
                              continue
                      else:
                              fcur.write(str(row[i][0]) + "   " + str(row[i][1]) + "   " + str(row[i][2]) + "   " + str(row[i][3])+ "\n")

              fcur.close()

    
              connection.close()

              print "==> FillNumber: ", fillNum
        fillNum += 1


