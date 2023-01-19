import datetime as dt
from inspect import cleandoc as multi_line_str

import cx_Oracle

from utils import databaseUtils as dbUtl
from utils import pixelDesignUtils as designUtl
from utils.modules import ReadoutGroup


USER_NAME, PASSWORD, DATABASE_NAME = dbUtl.get_oms_database_user_password_and_name()


def get_sensor_hv(begin_time, end_time, readout_group=None):
    """Return HV in volts for given readout group.
    
    If no readout group given, just returns HV of BPix_BpI_SEC1_LYR1.
    Can be used to check if the Pixel is ON HV or not.

    If no data in between begin_time and end_time, past times are checked till
    a value is found.

    Args:
        begin_time (datetime.datetime)
        end_time (datetime.datetime)
        readout_group (utils.modules.ReadoutGroup)
    """

    connection = cx_Oracle.connect('%s/%s@%s' % (USER_NAME, PASSWORD, DATABASE_NAME))
    cursor = connection.cursor()
    cursor.arraysize = 50

    python_time_mask = "%d-%b-%Y %H.%M.%S.%f"
    oracle_time_mask = "DD-Mon-YYYY HH24.MI.SS.FF"

    if readout_group is None:
        readout_group = ReadoutGroup("BPix_BpI_SEC1_LYR1")
    cable_name = designUtl.get_omds_hv_cable_name_from_readout_group_name(readout_group.name)

    query = multi_line_str("""
        SELECT *
        FROM v_voltages
        WHERE change_date>TO_TIMESTAMP('{begin_time}', '{oracle_time_mask}')
              AND change_date<TO_TIMESTAMP('{end_time}', '{oracle_time_mask}')
              AND cable LIKE '{cable_name}'
        ORDER BY change_date DESC
        """.format(
            begin_time=begin_time.strftime(python_time_mask),
            end_time=end_time.strftime(python_time_mask),
            cable_name=cable_name,
            oracle_time_mask=oracle_time_mask,
        )
    )

    cursor.execute(query)
    output = cursor.fetchall()
    connection.close()

    if len(output) == 0:
        time_window_extension = 5 * dt.timedelta(0, 3600)
        return get_sensor_hv(
            begin_time=begin_time-time_window_extension,
            end_time=begin_time,
            readout_group=readout_group,
        )

    return output[0][2]


def is_hv_on(begin_time, end_time, readout_group=None):
    hv = get_sensor_hv(begin_time, end_time, readout_group)
    return hv > 0