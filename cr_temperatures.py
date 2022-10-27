#!/bin/env python

import query_database
from dashboard import *
import numpy
import cx_Oracle
import dateutil.parser
from cr_mapping import dpename_dict

BPIX_ALIASES = ("Loop", "BPix", "BPI", "BMI", "BPIX", "BOX")
FPIX_ALIASES = ("BOX", "Box", "FPix", "Disk", "DCDC", "_SF")
FPIX_NOT_TEMPS = ("Flow", "Air", "Box%%RH", "Vaisala", "PC ", "Comet", "BOX temp")
NOT_INCLUDE = ("Omega", "not connected")
BPIX_NOT_TEMPS = ("Flow", "BPix A RH", "BPix B RH", "Comet", "Passive", "Active")
DEWPOINT = ("DP", "Dewpoint")
FLOW = ["Flow"]
RH = ["RH"]

def add_to_graph(cursor, new_plot, obs_part, stop_time_date):
    temps = {}
    for item in cursor:
        if temps.get(item[0]) is None:
            temps[item[0]] = {}
            temps[item[0]]["float"] = [[],[]]
        temps[item[0]]["name"] = dpename_dict[obs_part][item[1]]
        temps[item[0]]["float"][0].append(item[2])
        temps[item[0]]["float"][1].append(item[3])
    
    for temp in sorted(temps):
        xvals = temps[temp]["float"][0]
        yvals = temps[temp]["float"][1]
        if (temps[temp]["float"][0][-1] is not None):
            xvals += [stop_time_date]
            yvals += [temps[temp]["float"][1][-1]]
        new_plot.add_graph(temps[temp]["name"], xvals, yvals, drawstyle = "lines") 

def create_plot(run_numbers, start_stop_time, options = ""):
    
    options_split = options.split(".")
    
    clean_clause = ""
    if len(options_split) > 1 and options_split[1] == "clean":
        clean_clause = " and abs(value_converted) < 300 "
    
    obs_part = options_split[0]
    (obs, part) = obs_part.split(':')
    
    db = None

    if part == "BPIX":
        db = "CMS_TKCR_PVSS_BPIX_COND"
    else:
        db = "CMS_TKCR_PVSS_FPIX_COND"
    
    new_plot = plot()
    
    if len(run_numbers)>0:
        start_time = query_database.get_timestamps(run_numbers[0])[0]
        stop_time = query_database.get_timestamps(run_numbers[-1])[-1]
    elif len(start_stop_time)>0:
        start_time = start_stop_time[0]
        stop_time = start_stop_time[-1] 
    stop_time_date=dateutil.parser.parse(stop_time)
    
    dpe_names_clause = " and dpname in (" + ",".join(["'" + k + "'" for k in dpename_dict[obs_part].keys()]) + ") "
    
    query_temp = """select dpid, dpname, change_date, value_converted from """ + db + """.tkplcreadsensor, """ + db + """.dp_name2id
                where """ + db + """.tkplcreadsensor.dpid = """ + db + """.dp_name2id.id
                and value_converted IS NOT NULL dpe_names_clause """ + clean_clause + """
                and change_date between to_timestamp('""" + str(start_time) + """', 'RRRR-MM-DD HH24:MI:SS.FF')
                and to_timestamp('""" + str(stop_time) + """', 'RRRR-MM-DD HH24:MI:SS.FF')
                union
                SELECT m.dpid, dpname, to_timestamp('""" + str(start_time) + """', 'RRRR-MM-DD HH24:MI:SS.FF'), m.value_converted
                from (
                select dpid, change_date, value_converted, rank() over (partition by dpid order by change_date desc) as rnk from """ + db + """.tkplcreadsensor
                where value_converted IS NOT NULL and change_date < to_timestamp('""" + str(start_time) + """', 'RRRR-MM-DD HH24:MI:SS.FF')""" + clean_clause + """
                order by rnk) m, """ + db + """.dp_name2id
                where m.dpid = """ + db + """.dp_name2id.id dpe_names_clause """ + clean_clause + """
                and value_converted IS NOT NULL
                and rnk = 1
                """
    query = query_temp.replace("dpe_names_clause", dpe_names_clause)
    
    connection = None
    
    #connection = cx_Oracle.connect('cms_trkcr_pvss_r/boba-babu5@int2r')
    connection = cx_Oracle.connect('CMS_TKCR_PVSS_R/echo-zulu1@CMSR')
    cursor = connection.cursor()
    cursor.execute(query)   
    
    add_to_graph(cursor, new_plot, obs_part, stop_time_date)
    
    if obs == "DEWPOINT":
        dpe_names_clause = " and dpname in (" + ",".join(["'" + k + "'" for k in dpename_dict[obs_part + "_2"].keys()]) + ") "
        query = query_temp.replace("tkplcreadsensor", "TKPLCDEWPOINT").replace("value_converted", "value").replace("dpe_names_clause", dpe_names_clause)
        cursor = connection.cursor()
        cursor.execute(query)
        #print query
        add_to_graph(cursor, new_plot, obs_part + "_2", stop_time_date)
        
    connection.close() 
    
    if obs == "TEMP" or obs == "TEMP_A" or obs == "TEMP_B" or obs == "DEWPOINT":
        new_plot.yaxis_title = "Temperature [degC]"
    elif obs == "RH" or obs == "RH_ROOM":
        new_plot.yaxis_title = "Percent [%]"
    elif obs == "FLOW":
        new_plot.yaxis_title = "Flow [l/min]"
    elif obs == "PRESSURE":
        new_plot.yaxis_title = "Pressure [bar]"
    
    return new_plot
    
def get_description():
    return """This probe displays temperatures of the clean room.<br/>
Arguments accepted are either BPIX or FPIX.<br/>
"""

#create_plot("", ["2018-01-15","2018-02-01"],"BPIX")
#create_plot("", ["2019-02-19 15:24:16","2019-02-27 18:24:16"],"TEMP_A:BPIX,clean")

