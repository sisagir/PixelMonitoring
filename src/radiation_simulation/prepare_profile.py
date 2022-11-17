import os
import re
import argparse
from pathlib import Path
from inspect import cleandoc as multi_line_str

import cx_Oracle
import datetime as dt
import ROOT

from utils import generalUtils as gUtl
from utils import pythonUtils as pyUtl
from utils import databaseUtils as dbUtl
from utils import eraUtils as eraUtl
from utils import pixelDesignUtils as designUtl
from utils.Module import ReadoutGroup
from config.cooling.omds_dcs_aliases import omds_to_dcs_alias


PROFILE_FORMAT = "%d\t%d\t\t%4.2f\t\t%10d\t\t%6.2f"
USER_NAME, PASSWORD, DATABASE_NAME = dbUtl.get_oms_database_user_password_and_name()
NA_VALUE = -999
CELSIUS_TO_KELVIN = 273.15


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_fills_file_name",
        help="Luminosity file",
        required=False,
        default="data/fills_info/fills.csv",
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
        '-rog', "--readout_group",
        help='Read out group name, e.g. BPix_BmI_SEC4_LYR1',
    )
    parser.add_argument(
        "-f", "--fluence_file",
        help='Input fluence ROOT file',
        default="data/fluence/fluence_field_phase1_6500GeV.root",
    )
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory name",
        required=False,
        default="data/radiation_simulation/",
    )
    parser.add_argument(
        "-p", "--profile",
        help="Output profile file name",
        required=False,
        default="profile.csv",
    )
    parser.add_argument(
        "-tsi", "--interfill_time_step",
        help="Time step during interfill in seconds",
        type=int,
        required=False,
        default=1200,
    )
    parser.add_argument(
        "-tsf", "--fill_time_step",
        help="Time step during fill in seconds",
        type=int,
        required=False,
        default=1200,
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Print out lines written to profile",
        required=False,
        action="store_true",
    )

    return parser.parse_args()

# TODO: Many of the functions here are a duplicate/variant of some already
#       existing functions. They should go to some helper/utility scripts
#       and be used by other scripts.

def __get_leakage_current(readout_group, begin_time, end_time):

    connection = cx_Oracle.connect('%s/%s@%s' % (USER_NAME, PASSWORD, DATABASE_NAME))
    cursor = connection.cursor()
    cursor.arraysize = 50

    python_time_mask = "%d-%b-%Y %H.%M.%S.%f"
    oracle_time_mask = "DD-Mon-YYYY HH24.MI.SS.FF"
    phase = eraUtl.get_phase_from_time(begin_time)

    channel_name = designUtl.get_omds_channel_name_from_readout_group_name(readout_group.name, phase=phase)

    if phase == 1:
        sub_system = channel_name.split("_")[0]
        channel_name = channel_name.replace(sub_system, sub_system + "%")
        cable_condition = f"lal.alias LIKE 'CMS_TRACKER/{channel_name}'"
    else:
        raise NotImplementedError

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
                      AND {cable_condition}
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
        SELECT actual_Imon
        FROM i_mon
        JOIN cables ON (i_mon.dpid=cables.dpid)
        ORDER BY itime
        """.format(
            cable_condition=cable_condition,
            channel_name=channel_name,
            start_time=begin_time.strftime(python_time_mask),
            end_time=end_time.strftime(python_time_mask),
            oracle_time_mask=oracle_time_mask,
        )
    )

    cursor.execute(query)
    output = cursor.fetchall()
    if len(output) == 1:
        leakage_current = output[0][0]
    elif len(output) == 0:
        leakage_current = NA_VALUE
    else:
        print("Error: Leakage current query returned %d rows, but should return at most 1 only!" % (len(output)))

    return leakage_current


def __get_number_of_sensors_in_cooling_loop(cooling_loop_sensor_name):
    """Get number of working sensors in the given cooling pipe.

    Args:
        cooling_loop_sensor_name (str): OMDS database cooling pipe name, e.g. PixelBarrel_BmI_1I_L4D2MN

    Returns:
        int
    """

    if ("L1D1" in cooling_loop_sensor_name):
        n_sensors = 3 if "F" in cooling_loop_sensor_name else 2

    if ("L1D2" in cooling_loop_sensor_name):
        n_sensors = 2 if "F" in cooling_loop_sensor_name else 3

    if ("L2D1" in cooling_loop_sensor_name):
        n_sensors = 3

    if ("L2D2" in cooling_loop_sensor_name):
        n_sensors = 2

    if ("L3D1" in cooling_loop_sensor_name):
        n_sensors = 3 if "F" in cooling_loop_sensor_name else 2

    if ("L3D2" in cooling_loop_sensor_name):
        n_sensors = 3

    if ("L3D3" in cooling_loop_sensor_name):
        n_sensors = 3

    if ("L3D4" in cooling_loop_sensor_name):
        n_sensors = 3

    if ("L4D" in cooling_loop_sensor_name):
        n_sensors = 3

    return n_sensors


def __get_sectors_regex_from_cooling_loop_sensor_name(cooling_loop_sensor_name):
    """Get regex of the BPix sectors cooled down by a cooling pipe.

    Args:
        cooling_loop_sensor_name (str): OMDS database cooling pipe name, e.g. PixelBarrel_BmI_1I_L4D2MN

    Returns:
        str
    """

    def __make_regex(cooling_loop_sensor_name, suffix):
    
        if ("N" in cooling_loop_sensor_name): # Near
            sectors_regex = cooling_loop_sensor_name[:5] + "B[mp]I_" + suffix
    
        if ("F" in cooling_loop_sensor_name): # Far
            sectors_regex = cooling_loop_sensor_name[:5] + "B[mp]O_" + suffix
    
        return sectors_regex


    cooling_loop_sensor_name = cooling_loop_sensor_name.replace("PixelBarrel", "BPix")
    cooling_loop_sensor_name = cooling_loop_sensor_name.replace("PixelEndcap", "FPix")

    if ("L1D1" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[1234]_LYR1")

    if ("L1D2" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[5678]_LYR1")

    if ("L2D1" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[1234]_LYR2")

    if ("L2D2" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[5678]_LYR2")

    if ("L3D1" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[12]_LYR3")

    if ("L3D2" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[34]_LYR3")

    if ("L3D3" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[56]_LYR3")

    if ("L3D4" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[78]_LYR3")

    if ("L4D1" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[12]_LYR4")

    if ("L4D2" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[34]_LYR4")

    if ("L4D3" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[56]_LYR4")

    if ("L4D4" in cooling_loop_sensor_name):
        sectors_regex = __make_regex(cooling_loop_sensor_name, "SEC[78]_LYR4")

    return sectors_regex


def __get_module_cooling_loop_temperature(readout_group, begin_time, end_time):
    """Get cooling loop temperature corresponding to a BPix read out group."""

    connection = cx_Oracle.connect('%s/%s@%s' % (USER_NAME, PASSWORD, DATABASE_NAME))
    cursor = connection.cursor()
    cursor.arraysize = 50

    name = "PixelBarrel(.*)(PF|PN|MF|MN)(.*)"
    
    query = multi_line_str("""
        WITH ids as (
            SELECT id, SUBSTR(alias, INSTR(alias,'/',-1)+1) AS part 
            FROM cms_trk_dcs_pvss_cond.aliases
            JOIN cms_trk_dcs_pvss_cond.dp_name2id 
            ON RTRIM(cms_trk_dcs_pvss_cond.aliases.dpe_name,'.') = cms_trk_dcs_pvss_cond.dp_name2id.dpname
            WHERE REGEXP_LIKE(substr(alias,instr(alias,'/',-1)+1), :name)
        )
        SELECT part, value_converted, change_date 
        FROM ids
        JOIN cms_trk_dcs_pvss_cond.tkplcreadsensor ON ids.id = cms_trk_dcs_pvss_cond.tkplcreadsensor.DPID 
        WHERE cms_trk_dcs_pvss_cond.tkplcreadsensor.change_date >= :start_time
        AND cms_trk_dcs_pvss_cond.tkplcreadsensor.change_date < :stop_time
        ORDER BY cms_trk_dcs_pvss_cond.tkplcreadsensor.change_date DESC
    """)

    cursor.execute(query, {'name': name, 'start_time': begin_time, 'stop_time': end_time})
    rows = cursor.fetchall()
    connection.close()

    n_sensors = None
    temperatures = {}

    for item in rows:
        cooling_loop_sensor_name = item[0]
        temperature = item[1]
        date_changed = item[2]

        if float(temperature) > 40:
            print("Warning: Faulty sensor for cooling loop sensor %s" % cooling_loop_sensor_name)
            continue # ignore the broken temperature sensors giving crazy values

        # Correct the cooling loop alias mismapping from OMDS to DCS
        omds_alias = pyUtl.list_to_str(cooling_loop_sensor_name.split("_")[-2:], "_")
        dcs_alias = omds_to_dcs_alias(omds_alias)
        cooling_loop_sensor_name = cooling_loop_sensor_name.replace(omds_alias, dcs_alias) 

        sectors_regex = __get_sectors_regex_from_cooling_loop_sensor_name(cooling_loop_sensor_name)

        if re.search(sectors_regex, readout_group.name):
            # We get the first occurence of the temperature, because
            # temperatures are ordered by decreasing time
            if cooling_loop_sensor_name not in temperatures.keys():
                temperatures[cooling_loop_sensor_name] = temperature
                
            if n_sensors is None:
                n_sensors = __get_number_of_sensors_in_cooling_loop(cooling_loop_sensor_name)

    if n_sensors is None or len(temperatures.keys()) < n_sensors:
        time_window_extension = 10 * dt.timedelta(0, 3600)
        return __get_module_cooling_loop_temperature(readout_group, begin_time - time_window_extension, end_time)

    else:
        temperatures_values = temperatures.values()
        temperatures_avg = sum(temperatures_values) / len(temperatures_values)
        return temperatures_avg + CELSIUS_TO_KELVIN


def __get_temperature(readout_group, begin_time, end_time, hv_on):
    """Get silicon temperature."""

    cooling_loop_temperature =  __get_module_cooling_loop_temperature(readout_group, begin_time, end_time)
    if hv_on:
        # Temperature difference between cooling carbon fiber support and silicon temperatures
        if "LYR4" in readout_group.name:
            temperature_difference = 4
        else:
            temperature_difference = 3
    else:
        temperature_difference = 0

    return cooling_loop_temperature + temperature_difference


def __get_lumi(begin_datetime, end_datetime):
    """Return luminosity for the given time window.
    
    Args:
        measurement_time (datetime.datetime): end 
    """

    time_format = "%02d/%02d/%02d %02d:%02d:%02d"
    begin_time = time_format % (
        begin_datetime.month,
        begin_datetime.day,
        begin_datetime.year-2000,
        begin_datetime.hour,
        begin_datetime.minute,
        begin_datetime.second,
    )
    end_time = time_format % (
        end_datetime.month,
        end_datetime.day,
        end_datetime.year-2000,
        end_datetime.hour,
        end_datetime.minute,
        end_datetime.second,
    )
    command_line = f'brilcalc lumi --begin "{begin_time}" --end "{end_time}" -u /fb --output-style csv'
    out = os.popen(command_line).read()
    lumi = float(out.split("\n")[-2].split(",")[-2])

    return lumi


def __get_fluence(readout_group, pp_cross_section, fluence_field, lumi):
    return readout_group.getAverageFluence(fluence_field, lumi, pp_cross_section)


def __get_interfill_data(readout_group, measurement_time, time_interval):
    """Return radiation simulation data for an interval during the interfill.

    Returned quantities are duration, leakage current, temperature and fluence.
    """

    begin_time = measurement_time - time_interval
    end_time = measurement_time

    duration = time_interval.total_seconds()
    temperature = __get_temperature(readout_group, begin_time, end_time, hv_on=False)
    leakage_current = NA_VALUE
    fluence = 0

    return duration, temperature, leakage_current, fluence


def __get_fill_data(readout_group, pp_cross_section, fluence_field, measurement_time, time_interval):
    """Return radiation simulation data for an interval during the fill.

    Returned quantities are duration, leakage current, temperature and fluence.
    """

    begin_time = measurement_time - time_interval
    end_time = measurement_time

    duration = time_interval.total_seconds()
    temperature = __get_temperature(readout_group, begin_time, end_time, hv_on=True)
    leakage_current = __get_leakage_current(readout_group, begin_time, end_time)
    lumi = __get_lumi(begin_time, end_time)
    fluence = __get_fluence(readout_group, pp_cross_section, fluence_field, lumi)

    return duration, temperature, leakage_current, fluence


def __add_interfill_to_profile(
        profile,
        readout_group,
        end_stable_beam_time_last_fill,
        begin_stable_beam_time,
        interfill_time_interval,
        verbose,
    ):

    measurement_time = end_stable_beam_time_last_fill + interfill_time_interval
    while measurement_time < begin_stable_beam_time:
        duration, temperature, leakage_current, fluence = __get_interfill_data(
            readout_group,
            measurement_time,
            interfill_time_interval,
        )
        line = PROFILE_FORMAT % (dt.datetime.timestamp(measurement_time),
            duration, temperature, fluence, leakage_current)
        if verbose: print(line)
        profile.write(line + "\n")
        measurement_time += interfill_time_interval

    last_measurement_time = measurement_time - interfill_time_interval
    duration, temperature, leakage_current, fluence = __get_interfill_data(
        readout_group,
        begin_stable_beam_time,
        begin_stable_beam_time - last_measurement_time,
    )
    line = PROFILE_FORMAT % (dt.datetime.timestamp(begin_stable_beam_time),
        duration, temperature, fluence, leakage_current)
    if verbose: print(line)
    profile.write(line + "\n")


def __add_fill_to_profile(
        profile,
        readout_group,
        fluence_field,
        pp_cross_section,
        begin_stable_beam_time,
        end_stable_beam_time,
        fill_time_interval,
        verbose,
    ):

    measurement_time = begin_stable_beam_time + fill_time_interval
    while measurement_time < end_stable_beam_time:
        duration, temperature, leakage_current, fluence = __get_fill_data(
            readout_group,
            pp_cross_section,
            fluence_field,
            measurement_time,
            fill_time_interval,
        )
        line = PROFILE_FORMAT % (dt.datetime.timestamp(measurement_time),
            duration, temperature, fluence, leakage_current)
        if verbose: print(line)
        profile.write(line + "\n")
        measurement_time += fill_time_interval

    last_measurement_time = measurement_time - fill_time_interval
    duration, temperature, leakage_current, fluence = __get_fill_data(
        readout_group,
        pp_cross_section,
        fluence_field,
        end_stable_beam_time,
        end_stable_beam_time - last_measurement_time,
    )
    line = PROFILE_FORMAT % (dt.datetime.timestamp(end_stable_beam_time),
        duration, temperature, fluence, leakage_current)
    if verbose: print(line)
    profile.write(line + "\n")


def main():
    args = __get_arguments()

    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    fills_info = gUtl.get_fill_info(args.input_fills_file_name)
    good_fills = fills_info.fill_number.to_list()
    fluence_root_file = ROOT.TFile.Open(args.fluence_file)
    fluence_field = fluence_root_file.Get("fluence_allpart")

    readout_group = ReadoutGroup(args.readout_group)

    end_stable_beam_datetime_last_fill = None
    interfill_time_interval = dt.timedelta(0, args.interfill_time_step)
    fill_time_interval = dt.timedelta(0, args.fill_time_step)

    profile_path = args.output_directory + args.profile
    profile = open(profile_path, "w")
    header_line = "Timestamp [s]\tDuration [s]\tTemperature [K]\tFluence [n_eq/cm2]\tLeakage_current [mA/cm2]"
    if args.verbose: print(header_line)
    profile.write(header_line + "\n")

    for fill in range(args.first_fill, args.last_fill+1):
        if not fill in good_fills: continue

        fill_info = fills_info[fills_info.fill_number == fill]
        if len(fill_info) != 1:
            print("Error!")
            exit(0)

        pp_cross_section = eraUtl.get_pp_cross_section(fill)

        begin_stable_beam_time = dt.datetime.fromisoformat(fill_info.start_stable_beam.to_list()[0])
        end_stable_beam_time = dt.datetime.fromisoformat(fill_info.end_stable_beam.to_list()[0])

        if end_stable_beam_datetime_last_fill is not None:
            __add_interfill_to_profile(
                profile,
                readout_group,
                end_stable_beam_datetime_last_fill,
                begin_stable_beam_time,
                interfill_time_interval,
                verbose=args.verbose,
            )

        fill_duration = end_stable_beam_time - begin_stable_beam_time
        if fill_duration < fill_time_interval:
            print("Warning: Short fill! Fill duration is %.1f [min]" % (fill_duration.total_seconds()/60))

        __add_fill_to_profile(
            profile,
            readout_group,
            fluence_field,
            pp_cross_section,
            begin_stable_beam_time,
            end_stable_beam_time,
            fill_time_interval,
            verbose=args.verbose,
        )

        end_stable_beam_datetime_last_fill = end_stable_beam_time


if __name__ == "__main__":
    main()
