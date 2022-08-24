import query_database
# import datetime
import pprint
from collections import OrderedDict
from datetime import datetime, timedelta
import time

# SET 'FROM' AND 'TO' DATES HERE
# time will only be relevant for output file time (12:00:00 mid-day for plotting later)
# RUN  python query_database_avgperdaytemp.py

# startdate = datetime(2017, 5, 22, 12, 00, 00, 00); # first day noon
startdate = datetime(2018, 10, 15, 12, 00, 00, 00); # first day noon
# enddate = datetime(2018, 10, 15, 12, 00, 00, 00); # last day noon (output will be including end date)
enddate = datetime(2019, 1, 15, 12, 00, 00, 00); # last day noon (output will be including end date)
startdate_str = str(startdate.date());
enddate_str = str(enddate.date());

#sensornames = ['PixelBarrel_BmI_1I_L4D2MN'] # of these, the average temperature per day will be returned by get_temperatures()
# broken: "PixelBarrel_BmO_6I_L4D3MF.txt", "PixelBarrel_BpI_6I_L4D3PN.txt"
# BmO_6M_L4D3MF outlier, see https://indico.cern.ch/event/749648/contributions/3106061/attachments/1701424/2740212/update.pdf
sensorfiles = ["PixelBarrel_BmI_1I_L4D2MN.txt", "PixelBarrel_BmI_1M_L4D2MN.txt", "PixelBarrel_BmI_1R_L4D2MN.txt", "PixelBarrel_BmI_2I_L3D1MN.txt", "PixelBarrel_BmI_2R_L3D1MN.txt", "PixelBarrel_BmI_3I_L2D1MN.txt", "PixelBarrel_BmI_3M_L2D1MN.txt", "PixelBarrel_BmI_3R_L2D1MN.txt", "PixelBarrel_BmI_4I_L1D2MN.txt", "PixelBarrel_BmI_4M_L1D2MN.txt", "PixelBarrel_BmI_4R_L1D2MN.txt", "PixelBarrel_BmI_5I_L3D3MN.txt", "PixelBarrel_BmI_5M_L3D3MN.txt", "PixelBarrel_BmI_5R_L3D3MN.txt", "PixelBarrel_BmI_6I_L4D4MN.txt", "PixelBarrel_BmI_6M_L4D4MN.txt", "PixelBarrel_BmI_6R_L4D4MN.txt", "PixelBarrel_BmO_1I_L4D1MF.txt", "PixelBarrel_BmO_1M_L4D1MF.txt", "PixelBarrel_BmO_1R_L4D1MF.txt", "PixelBarrel_BmO_2I_L3D2MF.txt", "PixelBarrel_BmO_2M_L3D2MF.txt", "PixelBarrel_BmO_2R_L3D2MF.txt", "PixelBarrel_BmO_3I_L1D1MF.txt", "PixelBarrel_BmO_3M_L1D1MF.txt", "PixelBarrel_BmO_3R_L1D1MF.txt", "PixelBarrel_BmO_4I_L2D2MF.txt", "PixelBarrel_BmO_4M_L2D2MF.txt", "PixelBarrel_BmO_4R_L2D2MF.txt", "PixelBarrel_BmO_5I_L3D4MF.txt", "PixelBarrel_BmO_5M_L3D4MF.txt", "PixelBarrel_BmO_5R_L3D4MF.txt", "PixelBarrel_BmO_6R_L4D3MF.txt", "PixelBarrel_BpI_1I_L4D1PN.txt", "PixelBarrel_BpI_1M_L4D1PN.txt", "PixelBarrel_BpI_1R_L4D1PN.txt", "PixelBarrel_BpI_2I_L3D2PN.txt", "PixelBarrel_BpI_2M_L3D2PN.txt", "PixelBarrel_BpI_2R_L3D2PN.txt", "PixelBarrel_BpI_3I_L1D1PN.txt", "PixelBarrel_BpI_3R_L1D1PN.txt", "PixelBarrel_BpI_4I_L2D2PN.txt", "PixelBarrel_BpI_4M_L2D2PN.txt", "PixelBarrel_BpI_4R_L2D2PN.txt", "PixelBarrel_BpI_5M_L3D4PN.txt", "PixelBarrel_BpI_5R_L3D4PN.txt", "PixelBarrel_BpI_6M_L4D3PN.txt", "PixelBarrel_BpI_6R_L4D3PN.txt", "PixelBarrel_BpO_1I_L4D2PF.txt","PixelBarrel_BpO_1M_L4D2PF.txt","PixelBarrel_BpO_1R_L4D2PF.txt","PixelBarrel_BpO_2I_L3D1PF.txt","PixelBarrel_BpO_2M_L3D1PF.txt","PixelBarrel_BpO_2R_L3D1PF.txt","PixelBarrel_BpO_3I_L2D1PF.txt","PixelBarrel_BpO_3M_L2D1PF.txt","PixelBarrel_BpO_3R_L2D1PF.txt","PixelBarrel_BpO_4I_L1D2PF.txt","PixelBarrel_BpO_4R_L1D2PF.txt","PixelBarrel_BpO_5I_L3D3PF.txt","PixelBarrel_BpO_5M_L3D3PF.txt","PixelBarrel_BpO_5R_L3D3PF.txt","PixelBarrel_BpO_6I_L4D4PF.txt","PixelBarrel_BpO_6M_L4D4PF.txt","PixelBarrel_BpO_6R_L4D4PF.txt"];


def daterange(startdate, day_i):
    yield startdate + timedelta(day_i)

## call with
##     python query_database_avgperdaytemp.py > log_query.txt


def get_temperatures(run_numbers, start_stop_time):

    hours = 0.;
    prevhours = 0;
    prevtemp = 0;
    avgtemp = 0;
    restofday = 0.;
    averaging = False;

    if len(run_numbers)>0:
        start_time = query_database.get_timestamps(run_numbers[0])[0]
        stop_time = query_database.get_timestamps(run_numbers[-1])[-1]
    elif len(start_stop_time)>0:
        start_time = start_stop_time[0]
        stop_time = start_stop_time[-1]

    rows = query_database.fetch("""
    with IDs as ( select id, alias, since, rtrim(dpe_name,'.') as dp, substr(alias,instr(alias,'/',-1)+1) as part, update_count, CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname as dpname from CMS_TRK_DCS_PVSS_COND.aliases, CMS_TRK_DCS_PVSS_COND.dp_name2id where CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname like  '%Pixel%' and  rtrim(CMS_TRK_DCS_PVSS_COND.aliases.dpe_name,'.') = CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname)
    select part, alias, since, update_count, value_converted, change_date , dpname from CMS_TRK_DCS_PVSS_COND.tkplcreadsensor, IDs where IDs.id = CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.DPID and CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date >= to_timestamp('""" + str(start_time) + """', 'RRRR-MM-DD HH24:MI:SS.FF') AND CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date < to_timestamp('""" + str(stop_time) + """', 'RRRR-MM-DD HH24:MI:SS.FF') order by part, CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date
    """, user = "cms_trk_r")

    temperatures = {}
    avgtemperatures = {} # Julia

    for i, item in enumerate(rows):
        moduleName = item[0]
        temp = item[4]
        date_changed = format(item[5]) # format: Julia

        if moduleName not in temperatures:
            temperatures[moduleName] = [ [], [] ]


        temperatures[moduleName][0].append( date_changed )
        temperatures[moduleName][1].append( temp )

#######################
# avgtemperatures.py
######################

    d = temperatures
    pp = pprint.PrettyPrinter(indent=4)
#    pp.pprint(temperatures)
    # access datetimes and temperatures
    for sensorfile in sensorfiles:
        print("NEXT SENSOR");
        sensorname = sensorfile[:-4]
        print(sensorname);
        DBentry_i = 0;
        times = d[sensorname][0]
        temps = d[sensorname][1]
        if (len(times) != len(temps)) :
            print("DB file: Number of temperature entries and date entries do not match");
            continue;
        while DBentry_i < len(temps):
            print("In temperature while loop");
            print(str(times[0]))
            # pp.pprint(times)
            print(str(temps[0]))
            prevtemp = temps[0]
            # pp.pprint(temps)
            ## construct one temperature entry per day:
            ## average according to hours in case of multiple entries
            ## continue last valid value for days without entry
            #with open(sensorfile, "w") as outfile:
            with open(sensorfile, "a") as outfile:
                date_i = startdate;
                day_i = 0;
                while (date_i.date() <= enddate.date()):
                    if ((averaging == False) and (DBentry_i < len(temps))):
                        try:
                            currentdatetime = datetime.strptime(times[DBentry_i], '%Y-%m-%d %H:%M:%S.%f')
                        except:
                            print("Format of " + str(times[DBentry_i]) + " does not match %Y-%m-%d %H:%M:%S.%f - try without %f:")
                            currentdatetime = datetime.strptime(times[DBentry_i], '%Y-%m-%d %H:%M:%S')
                        finally:
                            if (date_i.date() < currentdatetime.date()):
                                print("No new entry for " + str(date_i.date()) + ", write prevtemp to file. ");
                                if (day_i > 0): # write from 23 May onwards
                                    if (day_i == 1):
                                        print("Start writing from this date onwards: " + str(date_i.date()))
                                    outfile.write(str(int(time.mktime(date_i.timetuple()))) + '000\t' + str(prevtemp) + '\n');
                                day_i += 1;
                                date_i = startdate + timedelta(day_i);
                                avgtemp = 0;
                            else :
                                print("-----------------");
                                print("Found an entry for " + str(date_i.date()) + ". Going to check whether there are more. ");
                                averaging = True;
#                                try:
 #                                   currentdatetime = datetime.strptime(times[DBentry_i], '%Y-%m-%d %H:%M:%S.%f').date()
  #                              except:
   #                                 print "Format of " + str(times[DBentry_i]) + " does not match %Y-%m-%d %H:%M:%S.%f - try without %f:"
    #                                currentdatetime = datetime.strptime(times[DBentry_i], '%Y-%m-%d %H:%M:%S').date()
     #                           finally:
                                prevhours = float(currentdatetime.hour) + float(currentdatetime.minute)/60 + float(currentdatetime.second/3600); # until the new entrytime prevtemp is valid
                                print("Set prevhours to " + str(prevhours));
                                print("Prevtemp is " + str(prevtemp));
                                try:
                                  avgtemp = prevhours * prevtemp;
                                except:
                                  print("prevtemp is NoneType")
                                finally:
                                  print("and avgtemp is now " + str(avgtemp));
                                  prevtemp = temps[DBentry_i];
                                  DBentry_i += 1; # next entry
                    elif (averaging == True) and (DBentry_i < len(temps)):
                         try:
                             currentdatetime = datetime.strptime(times[DBentry_i], '%Y-%m-%d %H:%M:%S.%f')
                         except:
                             print("Format of " + str(times[DBentry_i]) + " does not match %Y-%m-%d %H:%M:%S.%f - try without %f:")
                             currentdatetime = datetime.strptime(times[DBentry_i], '%Y-%m-%d %H:%M:%S')
                         finally:
                             if (date_i.date() < currentdatetime.date()):
                                 print("No more entry for " + str(date_i.date()) + ". Last entry was " + times[DBentry_i-1])
                                 try :
                                     prevminutes =  int((float(prevhours) % int(prevhours))*60.0);
                                 except :
                                     prevminutes = 0;
                                 try :
                                     prevseconds = int(((float(prevhours) % int(prevhours))*60.0 %  int((float(prevhours) % int(prevhours))*60.0))*60.0);
                                 except :
                                     prevseconds = 0;
                                 try :
                                     restofday = float((datetime(date_i.year, date_i.month, date_i.day, 23, 59, 59, 999999) - datetime(date_i.year, date_i.month, date_i.day, int(prevhours), prevminutes, prevseconds, 0)).seconds / 3600.);
                                     print(" restofday is " + str(restofday));
                                 except :
                                     print("ERROR")
                                     print("No more entry for " + str(date_i))
                                     print("Previous valid entry for current day was " + str(times[DBentry_i-1]))
                                     print("Next entry at " + str(times[DBentry_i]))
                                     print(prevhours)
                                     print("ZeroDivisionError? float modulo...")

                                 #   restofday = float((datetime(date_i.year, date_i.month, date_i.day, 23, 59, 59, 999999) - datetime(date_i.year, date_i.month, date_i.day, 0, prevminutes,  int((float(prevminutes) % int(prevminutes))*60.0), 0)).seconds / 3600.);
                                #print "restofday " + str(restofday);
                                 try:
                                     avgtemp += prevtemp * restofday;
                                     prevhours += restofday;
                                 except:
                                     print("exception: Skip NoneType entry in DB")
                                     print(prevtemp)
                                 finally:
                                     DBentry_i+=1;
#                                 prevtemp = avgtemp/prevhours;
                                 avgtemp = avgtemp/prevhours;
                                 print(str(date_i) +  " final avg temp " + str(avgtemp));
                                 if (day_i > 0):
                                     if (day_i == 1):
                                         print("Start writing from this date onwards: " + str(date_i.date()))
                                     outfile.write(str(int(time.mktime(date_i.timetuple()))) + '000\t' + str(avgtemp) + '\n');
                                 averaging = False;
                                 day_i += 1;
                                 date_i = startdate + timedelta(day_i);
                             elif (date_i.date() == currentdatetime.date()):
                                 #                            print "Another entry for the same date. Collecting for average... "
                                 try:
                                     hours = (float(currentdatetime.hour) + float(currentdatetime.minute)/60. + float(currentdatetime.second/3600.))  - prevhours;
                                     prevhours = float(currentdatetime.hour) + float(currentdatetime.minute)/60. + float(currentdatetime.second/3600.);
                                     prevtemp = temps[DBentry_i];
                                     avgtemp += prevtemp * hours;
                                 except:
                                     print("exception: Skip NoneType entry in DB")
                                 finally:
                                     DBentry_i += 1;
                             else :
                                 print("Startdate after first DBentry?")
                    else:
                        print(" No more DB entries ")
                        if (day_i > 0):
                            if (day_i == 1):
                                print("Start writing from this date onwards: " + str(date_i.date()))
                            outfile.write(str(int(time.mktime(date_i.timetuple()))) + '000\t' + str(prevtemp) + '\n');
                        day_i += 1;
                        date_i = startdate + timedelta(day_i);
                print("NEXT SENSOR " + " resetting ...");
                date_i = startdate + timedelta(day_i);
                avgtemp = 0;
                print(" End ")





#######################
   # return temperatures
    return "Wrote average temperatures per day to file"

print("start now");
print(startdate_str);
print(enddate_str);

pp = pprint.PrettyPrinter(indent=4)
#print (get_temperatures([], [startdate_str, enddate_str])) # excluding enddate
pp.pprint(get_temperatures([], [startdate_str, enddate_str])) # excluding enddate
#print (get_temperatures([], ["2017-11-01", "2017-11-10"]))
