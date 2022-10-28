from inspect import cleandoc as multi_line_str
from pathlib import Path
import argparse

import cx_Oracle
import datetime as dt

from utils import generalUtils as gUtl
from utils import databaseUtils as dbUtl


user_name, password, database_name = dbUtl.get_oms_database_user_password_and_name()


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_fills_file_name",
        help="Luminosity file",
        required=False,
        default="data/fills_info/fills.csv",
    )
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory name",
        required=False,
        default="data/temperatures/air/",
    )
    parser.add_argument(
        "-suffix", "--output_file_name_suffix",
        help="Output file name",
        required=False,
        default="",
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

    return parser.parse_args()


def main(args):

    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    connection = cx_Oracle.connect('%s/%s@%s' % (user_name, password, database_name))
    python_time_mask = "%d-%b-%Y %H.%M.%S.%f"

    oracle_time_mask = "DD-Mon-YYYY HH24.MI.SS.FF"
    cursor = connection.cursor()
    cursor.arraysize=50

    fills_info = gUtl.get_fill_info(args.input_fills_file_name)
    good_fills = fills_info.fill_number.to_list()

    for fill in range(args.first_fill, args.last_fill+1):
        
        if not fill in good_fills: continue
    
        fill_info = fills_info[fills_info.fill_number == fill]
        if len(fill_info) != 1:
            print("Error!")
            exit(0)

        begin_time = fill_info.start_stable_beam.to_list()[0]
        begin_time = dt.datetime.fromisoformat(fill_info.start_stable_beam.to_list()[0])
        # TODO: Why not using the actual end time of the fill but start time + 10 minutes?
        # end_time = fill_info.end_time.to_list()[0]
        end_time =  begin_time + dt.timedelta(0, 600)
        begin_time = begin_time.strftime(python_time_mask)
        end_time = end_time.strftime(python_time_mask)

        query = multi_line_str("""
            WITH ids AS (
                SELECT id, RTRIM(dpe_name, '.') AS dp, SUBSTR(alias, INSTR(alias, '/', -1)+1) AS part
                FROM cms_trk_dcs_pvss_cond.aliases, cms_trk_dcs_pvss_cond.dp_name2id
                WHERE alias LIKE '%Pixel%Air'
                      AND RTRIM(cms_trk_dcs_pvss_cond.aliases.dpe_name, '.') = cms_trk_dcs_pvss_cond.dp_name2id.dpname
            )
            SELECT part, value_converted, change_date, dpid
            FROM cms_trk_dcs_pvss_cond.tkplcreadsensor, ids
            WHERE ids.id = dpid
                  AND change_date BETWEEN TO_TIMESTAMP('{start_time}', '{oracle_time_mask}')
                                          AND TO_TIMESTAMP('{end_time}', '{oracle_time_mask}')
            ORDER BY part, change_date
            """.format(
                start_time=begin_time,
                end_time=end_time,
                oracle_time_mask=oracle_time_mask,
            )
        )
    
        cursor.execute(query)
        output = cursor.fetchall()

        temperature_file_name = args.output_directory + "/" + str(fill) + ".txt"
        with open(temperature_file_name, "w+") as temperature_file:
            for row in output:
                temperature_file.write(str(row[0]) + "   " + str(row[1]) + "   " + str(row[2])+ "\n")
                
        print("%s has been written." % temperature_file_name)

    connection.close()
        

if __name__ == "__main__":

    args = __get_arguments()
    main(args)
