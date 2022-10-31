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
        default="data/temperatures/pipe/",
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
    parser.add_argument(
        "-s", "--sub_system",
        help="Sub-detector to analyse, default is both Barrel and EndCap.",
        choices=["Barrel", "EndCap", ""],
        default="",
        required=False,
    )

    return parser.parse_args()


def main():
    args = __get_arguments()

    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    connection = cx_Oracle.connect('%s/%s@%s' % (user_name, password, database_name))
    python_time_mask = "%d-%b-%Y %H.%M.%S.%f"

    oracle_time_mask = "DD-Mon-YYYY HH24.MI.SS.FF"
    cursor = connection.cursor()
    cursor.arraysize = 50


    fills_info = gUtl.get_fill_info(args.input_fills_file_name)
    good_fills = fills_info.fill_number.to_list()

    for fill in range(args.first_fill, args.last_fill+1):
        if not fill in good_fills: continue

        fill_info = fills_info[fills_info.fill_number == fill]
        if len(fill_info) != 1:
            print("Error!")
            exit(0)

        begin_time = dt.datetime.fromisoformat(fill_info.start_stable_beam.to_list()[0])
        # The end_time has to be begin_time + 20 minutes in order to
        # wait for thermal equilibrium.
        end_time =  begin_time + dt.timedelta(0, 1200)
        begin_time = begin_time.strftime(python_time_mask)
        end_time = end_time.strftime(python_time_mask)

        if args.sub_system == "Barrel":
            sub_system_database_name = "Pixel" + args.sub_system
            sub_system_condition = multi_line_str("""
                (  SUBSTR(alias,INSTR(alias,'/',-1)+1) LIKE '{sub_system}%%PF' 
                or SUBSTR(alias,INSTR(alias,'/',-1)+1) LIKE '{sub_system}%%PN' 
                or SUBSTR(alias,INSTR(alias,'/',-1)+1) LIKE '{sub_system}%%MF' 
                or SUBSTR(alias,INSTR(alias,'/',-1)+1) LIKE '{sub_system}%%MN') 
                """.format(
                    sub_system=sub_system_database_name
                )
            )
        elif args.sub_system == "EndCap":
            # For FPix, PixelEndcap_BmI_PC_[1-3][A-D] or PixelEndcap_BmO_[1-3][IO]_SF
            sub_system_database_name = "PixelEndcap"
            sub_system_condition = multi_line_str("""
                SUBSTR(alias,INSTR(alias,'/',-1)+1) LIKE '{sub_system}%%PC%%'
                """.format(
                    sub_system=sub_system_database_name
                )
            )

        query = multi_line_str("""
            WITH ids AS (
                SELECT id, SUBSTR(alias,INSTR(alias,'/',-1)+1) AS part, dpname
                FROM cms_trk_dcs_pvss_cond.aliases, cms_trk_dcs_pvss_cond.dp_name2id
                WHERE {sub_system_condition}
                      AND RTRIM(cms_trk_dcs_pvss_cond.aliases.dpe_name,'.') = dpname
            ),

            temperatures AS (
                SELECT part, max(change_date) AS itime
                FROM cms_trk_dcs_pvss_cond.tkplcreadsensor, ids
                WHERE ids.id = cms_trk_dcs_pvss_cond.tkplcreadsensor.dpid
                      AND change_date BETWEEN TO_TIMESTAMP('{start_time}', '{oracle_time_mask}')
                                          AND TO_TIMESTAMP('{end_time}', '{oracle_time_mask}')
                      AND value_converted IS NOT NULL
                GROUP BY part
            )

            SELECT ids.part, value_converted, change_date
            FROM cms_trk_dcs_pvss_cond.tkplcreadsensor, ids, temperatures
            WHERE ids.id = cms_trk_dcs_pvss_cond.tkplcreadsensor.dpid
                  AND change_date BETWEEN TO_TIMESTAMP('{start_time}', '{oracle_time_mask}')
                                      AND TO_TIMESTAMP('{end_time}', '{oracle_time_mask}')
                  AND change_date = temperatures.itime
                  AND ids.part = temperatures.part
            ORDER BY part, change_date
            """.format(
                sub_system_condition=sub_system_condition,
                start_time=begin_time,
                end_time=end_time,
                oracle_time_mask=oracle_time_mask,
            )
        )

        cursor.execute(query)
        output = cursor.fetchall()
        
        sub_system_string = "_" + args.sub_system if args.sub_system else ""
        temperature_file_name = args.output_directory + "/" + str(fill) + sub_system_string + ".txt"
        with open(temperature_file_name, "w+") as temperature_file:
            for row in output:
                temperature_file.write(str(row[0]) + "   " + str(row[1]) + "   " + str(row[2])+ "\n")
                
        print("%s has been written." % temperature_file_name)

    connection.close()
 

if __name__ == "__main__":
    main()