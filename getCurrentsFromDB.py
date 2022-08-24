import os
from inspect import cleandoc as multi_line_str
import cx_Oracle
import datetime
import argparse 

import datetime as dt
import pandas as pd 

import utils as utl

password = utl.get_database_password()
database_name = "cms_omds_adg"
user_name = "cms_trk_r"

schema = "cms_lumi_prod"


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_fills_file_name",
        help="Luminosity file",
        required=False,
        default="fills_info/fills.txt",
    )
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory name",
        required=False,
        default="./currents/",
    )
    parser.add_argument(
        "-ff", "--first_fill",
        help="First fill number to analyse",
        type=int,
        required=True,
    )
    parser.add_argument(
        "-lf", "--last_fill",
        help="Last fill number to analyse",
        type=int,
        required=True,
    )
    parser.add_argument(
        "-s", "--sub_detector",
        help="Sub-detector to analyse",
        choices=["Barrel", "EndCap"],
        required=True,
    )

    return parser.parse_args()


def main(args):

    if not os.path.exists(args.output_directory):
        os.makedirs(args.output_directory)

    python_time_mask = "%d-%b-%Y %H.%M.%S.%f"
    oracle_time_mask = "DD-Mon-YYYY HH24.MI.SS.FF"
    
    connection = cx_Oracle.connect('%s/%s@%s' % (user_name, password, database_name))
    cursor = connection.cursor()
    cursor.arraysize=50

    fills_info = pd.read_csv(args.input_fills_file_name)
    good_fills = fills_info.fill_number.to_list()

    for fill in range(args.first_fill, args.last_fill+1):
        
        if not fill in good_fills: continue
    
        fill_info = fills_info[fills_info.fill_number == fill]
        if len(fill_info) != 1:
            print("Error!")
            exit(0)

        print(fill)
        begin_time = fill_info.start_time.to_list()[0]
        begin_time = dt.datetime.fromisoformat(begin_time.replace("Z", "+00:00"))
        print(begin_time)
        end_time = fill_info.end_time.to_list()[0]
        end_time = dt.datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        print(end_time)
        end_time =  begin_time + datetime.timedelta(0, 600)
        begin_time = begin_time.strftime(python_time_mask)
        end_time = end_time.strftime(python_time_mask)
        # print "Fill Number: ", fill
        # print "Begin Time: ", begin_time
        # print "End Time: ", end_time

        query = multi_line_str(
            """
            SELECT fillnum, starttime, stoptime
            FROM {schema}.cmsrunsummary
            WHERE starttime IS NOT NULL
                  AND fillnum IS NOT NULL
                  AND fillnum = {fill}
            """.format(
                schema=schema,
                fill=fill,
            )
        )
        cursor.execute(query)
    
        output = cursor.fetchall()
    
        begin_time = output[0][1]
        end_time = output[0][2]
        print(begin_time)
        print(end_time)
        print("")
        exit(0)


    
        query = multi_line_str("""
            WITH cables AS (
                SELECT DISTINCT substr(lal.alias,INSTR(lal.alias,  '/', -1, 2)+1) cable, id dpid, cd
                    FROM (
                        SELECT max(since) AS cd, alias
                        FROM cms_trk_dcs_pvss_cond.aliases
                        GROUP BY alias
                    ) md, cms_trk_dcs_pvss_cond.aliases lal
                    JOIN cms_trk_dcs_pvss_cond.dp_name2id ON dpe_name=concat(dpname,'.')
                    WHERE md.alias=lal.alias
                          AND lal.since=cd
                          AND (lal.alias LIKE 'CMS_TRACKER/%Pixel%/channel00%')
            ),
            it AS (
                SELECT dpid, max(change_date) itime
                FROM cms_trk_dcs_pvss_cond.fwcaenchannel caen
                WHERE change_date
                          BETWEEN to_timestamp('{start_time}', '{oracle_time_mask}')
                          AND to_timestamp('{end_time}', '{oracle_time_mask}')
                      AND actual_Imon is not NULL
                GROUP BY dpid
            ),
            i_mon AS (
                SELECT it.dpid, itime, actual_Imon, actual_Vmon
                FROM cms_trk_dcs_pvss_cond.fwcaenchannel caen
                JOIN it ON (it.dpid = caen.dpid AND change_date = itime)
                AND actual_Imon is not NULL
            )
            SELECT cable, actual_Imon, actual_Vmon, itime
            FROM i_mon
            JOIN cables ON (i_mon.dpid=cables.dpid)
            ORDER BY itime
            """.format(
                start_time=begin_time,
                end_time=end_time,
                oracle_time_mask=oracle_time_mask,
            )
        )

        cursor.execute(query)
        output = cursor.fetchall()
    
        currents_file_name = args.output_directory + "/" + str(fill) + "_" + args.sub_detector + ".txt"
        output_file = open(currents_file_name, "w+")
        for i in range(len(output)):
            if not args.sub_detector in output[i][0]:
                continue
            else:
                output_file.write(str(output[i][0]) + "   " + str(output[i][1]) + "   " + str(output[i][2]) + "   " + str(output[i][3])+ "\n")
    
        output_file.close()
        print("%s saved." % currents_file_name)
    
    connection.close()
    

if __name__ == "__main__":

    args = __get_arguments()
    main(args)
