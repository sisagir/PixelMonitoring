#!/bin/env python
import sqlite3 as sql
import cx_Oracle
import datetime
from datetime import date
from datetime import timedelta
import dateutil.parser

connection = cx_Oracle.connect('cms_trk_r/1A3C5E7G:FIN@cms_omds_adg')
cursor = connection.cursor()

#start_time = "2018-05-29 20:45:00"
#stop_time = "2018-06-15 22:30:00"

#start_time = "2018-04-27 00:00:00"
#stop_time = "2018-05-05 22:30:00"
#start_time = "2018-05-04 00:00:00"
#stop_time = "2018-06-09 00:00:00"
#start_time = "2018-05-02 09:42:29"
#stop_time = "2018-06-12 01:01:52"

start_time = "2018-10-29 05:00:00"
stop_time = "2018-11-01 15:00:00"

#stop_time = "2018-04-28 00:00:00"

#start_time = "2018-04-17 10:54:12"
#stop_time = "2018-07-12 11:52:00"

option = "Pixel"
# increase time range:
start_time = dateutil.parser.parse(start_time) - timedelta(hours=4)
stop_time = dateutil.parser.parse(stop_time) + timedelta(hours=4)

#start_time = dateutil.parser.parse(start_time) - timedelta(days=1)
#stop_time = dateutil.parser.parse(stop_time) + timedelta(days=1)

#query = """
#    with IDs as ( select id, substr(alias,instr(alias,'/',-1)+1) as part from CMS_TRK_DCS_PVSS_COND.aliases, CMS_TRK_DCS_PVSS_COND.dp_name2id
#    where (substr(alias,instr(alias,'/',-1)+1) like '""" + str(option + "%%" + "Disk" + "%%") + """')
#    and rtrim(CMS_TRK_DCS_PVSS_COND.aliases.dpe_name,'.') = CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname)
#    select part, value_converted, change_date from CMS_TRK_DCS_PVSS_COND.tkplcreadsensor, IDs where IDs.id = CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.DPID and CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date >= to_timestamp('""" + str(start_time) + """', 'RRRR-MM-DD HH24:MI:SS.FF') AND CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date < to_timestamp('""" + str(stop_time) + """', 'RRRR-MM-DD HH24:MI:SS.FF') order by part, CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date
#"""


query = """
    with IDs as ( select id, substr(alias,instr(alias,'/',-1)+1) as part from CMS_TRK_DCS_PVSS_COND.aliases, CMS_TRK_DCS_PVSS_COND.dp_name2id
    where (substr(alias,instr(alias,'/',-1)+1) like '""" + str(option + "%%" + "Disk" + "%%") + """'
    or substr(alias,instr(alias,'/',-1)+1) like '""" + str(option + "%%" + "PC" + "%%") + """'
    or substr(alias,instr(alias,'/',-1)+1) like '""" + str(option + "%%" + "DCDC" + "%%") + """')
    and rtrim(CMS_TRK_DCS_PVSS_COND.aliases.dpe_name,'.') = CMS_TRK_DCS_PVSS_COND.dp_name2id.dpname)
    select part, value_converted, change_date from CMS_TRK_DCS_PVSS_COND.tkplcreadsensor, 
    IDs where IDs.id = CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.DPID and CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date >= to_timestamp('""" + str(start_time) + """', 
    'RRRR-MM-DD HH24:MI:SS.FF') AND CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date < to_timestamp('""" + str(stop_time) + """', 
    'RRRR-MM-DD HH24:MI:SS.FF') order by part, CMS_TRK_DCS_PVSS_COND.tkplcreadsensor.change_date
"""



print("start executing query ...")
cursor.execute(query)
result = cursor.fetchall()
print("finish query execution!")

outputFile = "temperature.dat"
fcur = open(outputFile, "w+")

print("writing output...")


for i in range(len(result)):

    alias = result[i][0]
    
    alias = alias.replace("PixelBarrel", "BPix")
    alias = alias.replace("PixelEndcap", "FPix")

    if ("L1D1" in alias):
        alias = alias[:9] + "SEC1234_LYR1"

    if ("L1D2" in alias):
        alias = alias[:9] + "SEC5678_LYR1"

    if ("L2D1" in alias):
        alias = alias[:9] + "SEC1234_LYR2"

    if ("L2D2" in alias):
        alias = alias[:9] + "SEC5678_LYR2"

    if ("L3D1" in alias):
        alias = alias[:9] + "SEC12_LYR3"

    if ("L3D2" in alias):
        alias = alias[:9] + "SEC34_LYR3"

    if ("L3D3" in alias):
        alias = alias[:9] + "SEC56_LYR3"

    if ("L3D4" in alias):
        alias = alias[:9] + "SEC78_LYR3"

    if ("L4D1" in alias):
        alias = alias[:9] + "SEC12_LYR4"

    if ("L4D2" in alias):
        alias = alias[:9] + "SEC34_LYR4"

    if ("L4D3" in alias):
        alias = alias[:9] + "SEC5_LYR4"
        alias = alias[:9] + "SEC6_LYR4"

    if ("L4D4" in alias):
        alias = alias[:9] + "SEC78_LYR4"


    if ("I_L" in result[i][0]):
        alias = alias + "_begin"

    if ("M_L" in result[i][0]):
        alias = alias + "_middle"

    if ("R_L" in result[i][0]):
        alias = alias + "_end"

    if ("POH" in alias and "Inp" in alias):
        alias = alias[0:9] + "SEC" + alias[16:17] + "_POH_" + "input"

    if ("POH" in alias and "Detector" in alias):
        alias = alias[0:9] + "SEC" + alias[16:17] + "_POH_" + "detector"


    fcur.write(str(result[i][0]) + "   " + alias + "   " + str(result[i][1]) + "   " + str(result[i][2]) + "\n")

print("finish output!")

fcur.close()
connection.close()
