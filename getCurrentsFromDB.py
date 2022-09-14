from inspect import cleandoc as multi_line_str
from pathlib import Path
import argparse 

import cx_Oracle
import datetime as dt

from utils import generalUtils as gUtl
from utils import eraUtils as eraUtl
from utils import pixelDesignUtils as designUtl


password = gUtl.get_database_password()
database_name = "cms_omds_adg"
user_name = "cms_trk_r"

schema = "cms_lumi_prod"


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_fills_file_name",
        help="Luminosity file",
        required=False,
        default="fills_info/fills.csv",
    )
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory name",
        required=False,
        default="./currents/from_database",
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

    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    python_time_mask = "%d-%b-%Y %H.%M.%S.%f"
    oracle_time_mask = "DD-Mon-YYYY HH24.MI.SS.FF"
    
    connection = cx_Oracle.connect('%s/%s@%s' % (user_name, password, database_name))
    cursor = connection.cursor()
    cursor.arraysize=50


    fills_info = gUtl.get_fill_info(args.input_fills_file_name)
    good_fills = fills_info.fill_number.to_list()

    for fill in range(args.first_fill, args.last_fill+1):
        
        if not fill in good_fills: continue
    
        phase = eraUtl.get_phase_from_fill(fill)
        allowed_layers = designUtl.get_layer_names(phase) + designUtl.get_disk_names(phase)

        fill_info = fills_info[fills_info.fill_number == fill]
        if len(fill_info) != 1:
            print("Error!")
            exit(0)

        begin_time = dt.datetime.fromisoformat(fill_info.start_stable_beam.to_list()[0])
        # The end_time has to be begin_time + 10 minutes (or 20?) because the 
        # currents that will be read are the last within the begin_time to
        # end_time time window, such that it is after thermal equilibrium.
        # The time window has to be large enough to get data
        end_time =  begin_time + dt.timedelta(0, 600)
        begin_time = begin_time.strftime(python_time_mask)
        end_time = end_time.strftime(python_time_mask)

        query = multi_line_str("""
            WITH cables AS (
                SELECT DISTINCT SUBSTR(lal.alias,INSTR(lal.alias,  '/', -1, 2)+1) cable, id dpid, cd
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
                          BETWEEN TO_TIMESTAMP('{start_time}', '{oracle_time_mask}')
                          AND TO_TIMESTAMP('{end_time}', '{oracle_time_mask}')
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
        for row in output:
            cable, i_mon, v_mon, time  = row
            layer = designUtl.get_layer_name_from_cable_name(cable)
            if layer not in allowed_layers:
                continue
            if not args.sub_detector in cable:
                continue
            else:
                line = "%s   %s   %s   %s\n" % (cable, i_mon, v_mon, time)
                output_file.write(line)
    
        output_file.close()
        print("%s saved." % currents_file_name)
    
    connection.close()
    

if __name__ == "__main__":

    args = __get_arguments()
    main(args)
