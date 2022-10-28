import cx_Oracle
import datetime
import argparse


def vmon_imon(starttime, stoptime, channel='', layers='', disk='', ring='', quantity='vmon'):
    """
    Query database to get vmon and imon between starttime and stoptime.
    BPix channel can be:
        0: digital current
        1: analog current
        2: layer 3 for L23 or layer 1 for L14
        3: layer 2 for L23 or layer 4 for L14
    BPix layers can be
        14: layers 1 and 4
        23: layers 2 and 3
    FPix disks can be
        1: disk 1
        2: disk 2
        3: disk 3
    FPix channel can be:
        0: digital current
        1: analog current
        2: ring 2
        3: ring 1
    """
    ### Opening connection
    connection = cx_Oracle.connect('cms_trk_r/1A3C5E7G:FIN@cms_omds_adg') # offline
    # connection = cx_Oracle.connect('cms_trk_r/1A3C5E7G:FIN@cms_omds_lb') # online
    cursor = connection.cursor()
    cursor.arraysize=50
    layerdisk = ''
    barrelendcap = ''
    if disk != '' or ring != '':
        barrelendcap = 'EndCap'
        layerdisk = ''
        layers = disk
    elif layers != '':
        layerdisk = 'LAY'

    options = """'%Pixel""" + str(barrelendcap) + """%%""" + layerdisk + str(layers) + """%%channel00""" + str(channel) + """%'"""
    # Each pixel LAYER/ROG has a unique dpid. Using dpid directly in the query of currents can save plenty of time!
    dpid_rows_query = """select distinct substr(lal.alias,INSTR(lal.alias,  '/', -1, 2)+1), id from
    (select max(since) as cd, alias from  cms_trk_dcs_pvss_cond.aliases group by alias) md, cms_trk_dcs_pvss_cond.aliases lal
    join cms_trk_dcs_pvss_cond.dp_name2id on dpe_name=concat(dpname,'.')
    where md.alias=lal.alias and lal.since=cd
    and (lal.alias like """ + options + """)"""
    #dpid_rows_query ="""select dpe_name, alias, id from cms_trk_dcs_pvss_cond.aliases join cms_trk_dcs_pvss_cond.dp_name2id on (dpname || '.' = dpe_name) where alias like """ + options
    print("executing:")
    print(dpid_rows_query)

    cursor.execute(dpid_rows_query)
    dpid_rows = cursor.fetchall()
    rows = {}
    #quantity = quantity[0].upper() + quantity[1:].lower()

    ### Define query to get temperatures for Barrel Pixels
    for k in range(len(dpid_rows))[:]:
        moduleName = str(dpid_rows[k][0])
        moduleName = moduleName# [59:]
        dpidname = dpid_rows[k][1]
        query = """select """ + quantity + """, change_date from cms_trk_dcs_pvss_cond.fwcaenchannel         where change_date between TO_TIMESTAMP('""" + starttime + """', 'RRRR-MM-DD HH24:MI:SS.FF') and TO_TIMESTAMP('""" + stoptime + """', 'RRRR-MM-DD HH24:MI:SS.FF') and dpid='""" + str(dpidname) + """' and """ + quantity + """ is not NULL         order by change_date"""

        print("executing:")
        print(query)
        cursor.execute(query)
        rows[moduleName] = cursor.fetchall()
    connection.close()

    return rows


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Get currents and voltages from database.')
    parser.add_argument('--minutes', '-m', dest='minutes', default=10, help='Number of minutes to go back.')
    parser.add_argument('--hours', '-o', dest='hours', default=0, help='Number of hours to go back.')
    parser.add_argument('--seconds', '-s', dest='seconds', default=0, help='Number of seconds to go back.')
    parser.add_argument('--starttime', '-i', dest='starttime', help='Set start time for query, e.g. --starttime "2018-04-18 18:00:00.0".')
    parser.add_argument('--stoptime', '-f', dest='stoptime', help='Set stop time for query, e.g. --stoptime "2018-04-18 18:00:00.0".')
    parser.add_argument('--layer', '-l', dest='layer', help='Select a layer, e.g. 1, 2, 3, 4.')
    parser.add_argument('--disk', '-d', dest='disk', help='Select a disk, e.g. 1, 2, 3.')
    parser.add_argument('--ring', '-r', dest='ring', help='Select a ring, e.g. 1, 2.')
    parser.add_argument('--analog', '-a', dest='analog', action='store_true', help='Get low voltage analog current current.')
    parser.add_argument('--digital', '-g', dest='digital', action='store_true', help='Get low voltage digital current current.')
    parser.add_argument('--quantity', '-q', dest='quantity', help='Select a quantity, e.g. vmon, imon.')
    args = parser.parse_args()
    showlast = False #True

    db = "currents.db"
    tb = "currents"
    amtseconds = 0
    amtminutes = 10
    amthours = 0
    quantity = 'vmon'
    if args.hours != None: amthours = int(args.hours)
    if args.seconds != None: amtseconds = int(args.seconds)
    if args.minutes != None: amtminutes = int(args.minutes)
    powersupply = {1: '14', 2: '23', 3: '23', 4: '14'}
    hvchannel = {1: '1', 2: '2', 3: '1', 4: '2'}
    fpixhvchannel = {1: '3', 2: '2'}
    channel = ''
    layers = ''
    disk = ''
    if args.layer != None:
        layers = int(powersupply[int(args.layer)])
        channel = int(hvchannel[int(args.layer)]) + 1
    if args.disk != None:
        disk = int(args.disk)
    if args.ring != None:
        ring = int(args.ring)
        channel = int(fpixhvchannel[int(args.ring)])
    if args.quantity != None: quantity = args.quantity
    if args.analog:
        channel = 1
        quantity = 'imon'
    if args.digital:
        channel = 0
        quantity = 'imon'
    quantityname = quantity
    if quantity in ['vmon', 'imon']:
        quantity = 'actual_' + quantity



    stoptime = datetime.datetime.isoformat(datetime.datetime.utcnow()).replace('T', ' ')
    starttime = datetime.datetime.isoformat(datetime.datetime.utcnow() - datetime.timedelta(minutes=amtminutes, seconds=amtseconds, hours=amthours)).replace('T', ' ')
    if args.starttime != None: starttime = args.starttime
    if args.stoptime != None:
        stoptime = args.stoptime
    else:
        print("getting data for last", amthours, "hour(s)", amtminutes, "minute(s) and ", amtseconds, "second(s)")



    headers = [quantityname, 'change_date' ]
    print(starttime)
    print(stoptime)



    currents_voltages = vmon_imon(starttime, stoptime, layers=layers, disk=disk, channel=channel, ring=ring, quantity=quantity)
    for modname in currents_voltages:
        if currents_voltages[modname] != []:
            print('sector:', modname)
        else:
            continue
        if showlast: currents_voltages[modname] = [currents_voltages[modname][-1]]
        for vals in currents_voltages[modname]:

            #print vals
            values = {}
            for i in range(len(headers)):
                #print vals
                #if type(vals[i]) == str:
                #    values[headers[i]] =  vals[i].strip('cms_trk_dcs_4:')
                #else:
                #    values[headers[i]] =  vals[i]
                values[headers[i]] = vals[i]
            if values[quantityname] != None:
                print(quantityname, values[quantityname], 'found at', datetime.datetime.isoformat(values['change_date']), "for", modname)
            # sql.dict_to_db(values, db, tb)








