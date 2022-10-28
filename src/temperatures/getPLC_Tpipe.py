import argparse
from pathlib import Path
import cx_Oracle
import datetime as dt
import datetime
import os
from inspect import cleandoc as multi_line_str
import numpy as np
from numberOfROCs import *
import collections
import ROOT as rt

from utils import generalUtils as gUtl
from modules_geom import ROG
from rogring_pc import *
from fillIntLumi import *
from rogchannel_modules import *
from SiPixelDetsUpdatedAfterFlippedChange import *
import show_vmon as ivmon
import cr_temperatures as crp


def __get_arguments():
    parser = argparse.ArgumentParser()

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
        '-f',
        help='Input fluence ROOT file',
        default="fluence/fluence_field_phase1_6500GeV.root",
    )
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory name",
        required=False,
        default="./temperatures/pipe/",
    )
    parser.add_argument(
        "-l", "--layer-tag",
        dest="layerTag",
    )
    parser.add_argument(
        "-t", "--temperature",
        dest="temp",
        default='',
    )
    parser.add_argument(
        "-p", "--part",
    )
    parser.add_argument(
        "-g", "--rog",
        type=int,
    )
    parser.add_argument(
        "-r", "--ring",
        type=int,
    )
    parser.add_argument(
        "-d", "--disk",
        type=int,
    )
    parser.add_argument(
        "--min20",
        action="store_true"
    )

    return parser.parse_args()


# TODO: Function used only in commented out code, to remove after dealing with commented out code
# def correctAlias(sensorName):
#     # get substrings
#     part1 = sensorName[0:16] # PixelBarrel_BmO_ -- part 16
#     part2 = sensorName[16:25] # 4I_L1D2MN        -- part

#     changed = 0 # change only once

#     # change the wrong substring
#     # rebuild sensor name
#     if part2 in sensorMapNew:
#             part2=sensorMapNew[part2]
#     newSensorName = part1 + part2

#     # print "post correction %s"%newSensorName

#     return newSensorName


def main():
    args = __get_arguments()

    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    sensorMapOld_str=["4I_L1D2MN","4M_L1D2MN","4R_L1D2MN","3I_L2D1MN","3M_L2D1MN","3R_L2D1MN","4I_L2D2PN","4M_L2D2PN","4R_L2D2PN","2I_L3D1MN","2R_L3D1MN","5I_L3D3MN","5R_L3D3MN","1I_L4D2MN","1M_L4D2MN","1R_L4D2MN","6M_L4D3PN","6R_L4D3PN","6I_L4D4MN","6R_L4D4MN","3M_L1D1MF","3I_L1D1MF","3I_L2D1PF","3M_L2D1PF","3R_L2D1PF","2I_L3D1PF","2M_L3D1PF","2R_L3D2MF","2I_L3D2MF","1I_L4D2PF","1M_L4D2PF","1R_L4D2PF","6M_L4D3MF","6R_L4D3MF","4I_L2D2MF","4M_L2D2MF","4R_L2D2MF","6I_L4D4PF","6R_L4D4PF"]
    sensorMapNew_str=["4R_L1D2MN","4I_L1D2MN","4M_L1D2MN","1I_L4D2MN","1M_L4D2MN","1R_L4D2MN","6R_L4D3PN","6M_L4D3PN","6I_L4D3PN","2R_L3D1MN","2I_L3D1MN","5R_L3D3MN","5I_L3D3MN","3I_L2D1MN","3M_L2D1MN","3R_L2D1MN","4M_L2D2PN","4R_L2D2PN","6R_L4D4MN","6I_L4D4MN","3I_L1D1MF","3M_L1D1MF","1I_L4D2PF","1M_L4D2PF","1R_L4D2PF","2M_L3D1PF","2I_L3D1PF","2I_L3D2MF","2R_L3D2MF","3I_L2D1PF","3M_L2D1PF","3R_L2D1PF","4M_L2D2MF","4R_L2D2MF","6I_L4D3MF","6M_L4D3MF","6R_L4D3MF","6R_L4D4PF","6I_L4D4PF"]
    sensorMapNew=dict(list(zip(sensorMapOld_str, sensorMapNew_str)))
    good_sectors = ["BmO", "BmI", "BpO", "BpI"]
    broken_sectors = ["PixelBarrel_BpI_S3_LAY3", "PixelBarrel_BpI_S3_LAY4", "PixelBarrel_BpI_S5_LAY4"]
    oracleTimeMask = "DD-Mon-YYYY HH24.MI.SS.FF"
    pythonTimeMask = "%d-%b-%Y %H.%M.%S.%f"
    method=1
    layer="layer1"

    # pcboard_name="PixelEndcap_BmI_PC_1B"
    # rog_channel="PixelEndCap_BmI_D3_ROG2/channel003"

    # TODO: This seems to be obsolete, to delete after finishing to clean
    # if args.ring == '1':
    #     channel = "channel003"
    # elif args.ring == '2':
    #     channel = "channel002"
    # else:
    #     raise ValueError("Ring number should be 1 or 2!")

    part = args.part
    disk = args.disk
    rog = args.rog
    ring = args.ring

    rog_channel = part_disk_rog_ring_to_rogchannel_pcboardtemp(part, disk, rog, ring, 'rogchannel')
    if args.temp == '':
        pcboard_name = part_disk_rog_ring_to_rogchannel_pcboardtemp(part, disk, rog, ring, 'pcboard')
    else:
        pcboard_name = args.temp
    print(("%s: %s"%("rog_channel",rog_channel)))
    print(("%s: %s"%("pcboard_name",pcboard_name)))
    # "%s/%s"%(args.rog,channel)
    # pcboard_name = rogchannel_to_pcboard(rog_channel)

    count=0
    proFile = open(args.output_directory + "/profile.txt", "w")
    zeroCelsius=273.15
    corrTemp=3.

    # TODO: This stuff relates to commented out code, to get rid off if getting rid off the commented out code
    option = "PixelBarrel"
    layerTag = args.layerTag

    totLumi=0.
    fluence_file=rt.TFile.Open(args.f)
    th2f_fluence = fluence_file.Get("fluence_allpart")

    my_rog = ROG(rog_channel)

    args_tuple = collections.namedtuple('args', 'minutes hours seconds starttime stoptime layer disk ring analog digital quantity')
    my_iLeak = ivmon.leakageCurrentData()

    fills_info = gUtl.get_fill_info(args.input_fills_file_name)
    good_fills = fills_info.fill_number.to_list()

    for fill in range(args.first_fill, args.last_fill+1):
        if not fill in good_fills: continue

        ### Opening connection
        # connection = cx_Oracle.connect('cms_trk_r/1A3C5E7G:FIN@cms_omds_adg')
        # cursor = connection.cursor()
        # cursor.arraysize = 50

        fill_info = fills_info[fills_info.fill_number == fill]
        if len(fill_info) != 1:
            print("Error!")
            exit(0)

        begin_time = dt.datetime.fromisoformat(fill_info.start_stable_beam.to_list()[0])
        # The end_time has to be begin_time + 10 minutes (or 20?) because the 
        # currents that will be read are the last within the begin_time to
        # end_time time window, such that it is after thermal equilibrium.
        # The time window has to be large enough to get data
        end_time =  begin_time + dt.timedelta(0, 1200)
        # begin_time = begin_time.strftime(python_time_mask)
        # end_time = end_time.strftime(python_time_mask)

        begin_stable_beam_time = begin_time
        end_stable_beam_time = end_time

        if count == 0:
            proFile.write("BEGINTIME: %s\n"%begin_stable_beam_time)
            proFile.write("delta t\tcorr T\tFl_n\t\tT\tI_leak\tstd I_leak\n")

        print("Start  Time: ", begin_time)
        #end_time =  begin_time + datetime.timedelta(0,600) # 10 min into stable beam
        end_time =  begin_time + datetime.timedelta(0,1200) # 20 min into stable beam
        begin20minSTB =  begin_time + datetime.timedelta(0,1200) # 20 min into stable beam
        # end_time = end_stable_beam_time
        # print("Sta+10 Time: ", end_time)
        # print("EndSTB Time: ", end_stable_beam_time)

        end_time_between_fills=begin_time
        temps = []
        count2=0
        jjj=0
        lastTemp=float('nan')
        temps1=[]
        Tdiff=0
        prevTemp=0
        # ============== no beam ===========================
        if count != 0:
            begin_time_4=begin_time_between_fills
            begin_time_2=begin_time_between_fills
            end_time_2=begin_time_between_fills+datetime.timedelta(0,1200)
            begin_time_3=begin_time_between_fills
            end_time_3=begin_time_between_fills


            temperature_file_name = args.output_directory + "/" + str(fill) + "_before.txt"
            if os.path.exists(temperature_file_name):
                fcur=open(temperature_file_name, "w+")
            else:
                fcur=open(temperature_file_name, "w")
            # print query2
            while end_time_2 < end_time_between_fills:
                temps=crp.create_plot(pcboard_name,[begin_time_2.strftime('%m-%d-%Y %H:%M:%S'),end_time_2.strftime('%m-%d-%Y %H:%M:%S')])
                #
                # there are some swaped aliases... correct offline in C++ script
                #
                temps1=temps
                # print 'temps1=%s'%temps1
                # for i in xrange(len(row)):
                #     # sensorName=str(row[i][0])
                #     sensorName=correctAlias(str(row[i][0]))
                #     if method==1:
                #         if layerTag in sensorName and row[i][1] is not None:
                #             temps.append(row[i][1])
                #             temps1.append(row[i][1])
                #     elif method==2:
                #         if any(substr in row[i][0] for substr in sensorMapOld_str):
                #             if layerTag in sensorName and row[i][4] is not None:
                #                 temps.append(row[i][4])
                #                 temps1.append(row[i][4])
                #         fcur.write(str(row[i][0]) + " " + str(row[i][1]) + " " + str(row[i][2])+ "\n")

                # averTemp1=np.array([temps1]).mean()
                averTemp1=temps1

                if averTemp1<-300.:
                    Tdiff=0
                else:
                    Tdiff=averTemp1-lastTemp
                    lastTemp=averTemp1
                if (abs(Tdiff)>3. or (end_time_2-begin_time_4) > datetime.timedelta(2,-1)) and temps > -300:
                    if count2==0:
                        begin_time_3=begin_time_between_fills
                    # print type(row[i][2])
                    end_time_3=end_time_2
                    averTemp=temps
                    # print len(temps) > 0
                    timeInterval=(end_time_3-begin_time_3).total_seconds()
                    iLeak = -99.
                    diLeak = -99.
                    proFile.write("%d\t%4.2f\t%10d\t%4.2f\t%6.2f\t%6.2f\n"%(timeInterval,averTemp+zeroCelsius,0,averTemp+zeroCelsius,iLeak,diLeak))#,begin_time_3,end_time_3,fill))
                    temps = []
                    begin_time_3=end_time_3
                    # print "count2 = %s"%count2
                    prevTemp=averTemp
                    count2+=1
                temps1=[]
                if end_time_2-begin_time_4 > datetime.timedelta(2,-1):
                    # print "%s-%s"%(end_time_2,begin_time_4)
                    begin_time_4=end_time_2
                begin_time_2 = end_time_2
                end_time_2=begin_time_2+datetime.timedelta(0,1200)
            fcur.write("begin_time: %s\n  end_time: %s\n"%(begin_time_between_fills, end_time_between_fills))
            fcur.write(str(end_time_between_fills-begin_time_between_fills)+"\n")
            fcur.write((str(round((end_time_between_fills-begin_time_between_fills).total_seconds()))).rstrip(".0"))
            fcur.close()

            temps=crp.create_plot(pcboard_name,[begin_time_2.strftime('%m-%d-%Y %H:%M:%S'),end_time_between_fills.strftime('%m-%d-%Y %H:%M:%S')])
            temps1=temps
            # for i in xrange(len(row)):
            #     sensorName=correctAlias(str(row[i][0]))
            #     if method == 1:
            #         if layerTag in sensorName and row[i][1] is not None:
            #             temps.append(row[i][1])
            #       elif method == 2:
            #           if any(substr in row[i][0] for substr in sensorMapOld_str):
            #               if layerTag in sensorName and row[i][4] is not None:
            #                   temps.append(row[i][4])

            if temps > -300:
                averTemp=temps
                trueTemp=temps
                prevTemp=trueTemp
            else:
                averTemp=25
                trueTemp=-274.15 #means no reading
                trueTemp=prevTemp
            timeInterval=(end_time_between_fills-begin_time_3).total_seconds()
            iLeak = -99.
            diLeak = -99.
            proFile.write("%d\t%4.2f\t%10d\t%4.2f\t%6.2f\t%6.2f\n"%(timeInterval,averTemp+zeroCelsius,0,trueTemp+zeroCelsius,iLeak,diLeak))#,begin_time_3,end_time_between_fills,fill))
            # prevTemp=np.array([temps]).mean()

        temperature_file_name = args.output_directory + "/" + str(fill) + ".txt"
        if os.path.exists(temperature_file_name):
            fcur=open(temperature_file_name, "w+")
        else:
            fcur=open(temperature_file_name, "w")

        # ============== stable beam ===========================
        temps = []
        fcur.write("begin_time: %s\nend_time: %s\n"%(begin_stable_beam_time,end_stable_beam_time))
        fcur.write((str(round((end_stable_beam_time-begin_stable_beam_time).total_seconds()))).rstrip(".0"))
        fcur.close()

        #==== 20 mins after STB ====
        is_fill_mt20min = (begin20minSTB < end_stable_beam_time) and args.min20
        if is_fill_mt20min:
            lumi = fillLumi[fill]['20mins']
            print("lumi=%s\n"%lumi)
            lumi *= 1e-6

            temps=crp.create_plot(pcboard_name,[begin_stable_beam_time.strftime('%m-%d-%Y %H:%M:%S'),begin20minSTB.strftime('%m-%d-%Y %H:%M:%S')])
            # print 'temps = %s'%temps
            myArgs = args_tuple(layer=None, seconds=0, hours=0, starttime=begin_stable_beam_time.strftime('%Y-%m-%d %H-%M-%S'), stoptime=begin20minSTB.strftime('%Y-%m-%d %H-%M-%S'), digital=False, ring='1', disk=None, minutes=10, analog=False, quantity='imon')
            temps1=temps
            iLeak=-99.
            diLeak=-99.
            iLeak=my_iLeak.get_ivmon(connection,myArgs,rog_channel)
            # for t in row:
            #       temps.append(t[1])
            #       temps1.append(t[1])
            # for i in xrange(len(row)):
            #       sensorName=correctAlias(str(row[i][0]))
            #       if method == 1:
            #               if layerTag in sensorName and row[i][1] is not None:
            #                       temps.append(row[i][1])
            #       elif method == 2:
            #               if any(substr in row[i][0] for substr in sensorMapOld_str):
            #                       if layerTag in sensorName and row[i][4] is not None:
            #                               temps.append(row[i][4])
            # print temps
            # for l in row:
            #     print l[0]
            #     if l[0][16:25] in sensorMapOld_str:
            #         sensor_name=correctAlias(l[0])
            #         if l[0] == sensor_name:
            #         print "%40s\t%4.2f\n"%(l[0],l[4])

            if temps > -300:
                # averTemp=np.array([temps]).mean()
                # trueTemp=np.array([temps]).mean()
                averTemp=temps
                trueTemp=temps
                prevTemp=trueTemp
            else:
                averTemp=-8.5
                # trueTemp=-274.15 #means no reading
                trueTemp=prevTemp
            timeInterval=(begin20minSTB-begin_stable_beam_time).total_seconds()
            totLumi+=float(lumi)
            proFile.write("%d\t%4.2f\t%10d\t%4.2f\t%6.2f\t%6.2f\n"%(timeInterval,averTemp+zeroCelsius+corrTemp,int(my_rog.getAverageFluenceSum(th2f_fluence,float(lumi))/float(timeInterval)),trueTemp+zeroCelsius,iLeak,diLeak))#,begin_stable_beam_time,end_stable_beam_time,fill))
        else:
            begin20minSTB = begin_stable_beam_time
            # lumi = fillLumi[fill]['20mins'] + fillLumi[fill]['after20mins']


        #==== beginSTB+20 mins to endSTB ====

        if args.min20:
            lumi = fillLumi[fill]['after20mins']
        else:
            if begin20minSTB < end_stable_beam_time:
                lumi = fillLumi[fill]['20mins'] + fillLumi[fill]['after20mins']
            else:
                lumi = fillLumi[fill]['after20mins']

        print("lumi=%s\n"%lumi)
        lumi *= 1e-6
        temps=crp.create_plot(pcboard_name, [begin20minSTB.strftime('%m-%d-%Y %H:%M:%S'),end_stable_beam_time.strftime('%m-%d-%Y %H:%M:%S')])
        myArgs = args_tuple(layer=None, seconds=0, hours=0, starttime=begin20minSTB.strftime('%Y-%m-%d %H-%M-%S'), stoptime=end_stable_beam_time.strftime('%Y-%m-%d %H-%M-%S'), digital=False, ring='1', disk=None, minutes=10, analog=False, quantity='imon')
        temps1=temps
        iLeak=-99.
        diLeak=-99.
        iLeak=my_iLeak.get_ivmon(connection,myArgs,rog_channel)
        # for t in row:
        #     temps.append(t[1])
        #     temps1.append(t[1])
        # for i in xrange(len(row)):
        #     sensorName=correctAlias(str(row[i][0]))
        #     if method == 1:
        #         if layerTag in sensorName and row[i][1] is not None:
        #             temps.append(row[i][1])
        #         elif method == 2:
        #             if any(substr in row[i][0] for substr in sensorMapOld_str):
        #                 if layerTag in sensorName and row[i][4] is not None:
        #                     temps.append(row[i][4])
        # print temps
        # for l in row:
        #         print l[0]
        #         if l[0][16:25] in sensorMapOld_str:
        #                 sensor_name=correctAlias(l[0])
        #                 if l[0] == sensor_name:
        #                 print "%40s\t%4.2f\n"%(l[0],l[4])

        if temps > -300:
            # averTemp=np.array([temps]).mean()
            # trueTemp=np.array([temps]).mean()
            averTemp=temps
            trueTemp=temps
            prevTemp=trueTemp
        else:
            averTemp=-8.5
            # trueTemp=-274.15 #means no reading
            trueTemp=prevTemp
        timeInterval=(end_stable_beam_time-begin20minSTB).total_seconds()
        totLumi+=float(lumi)
        proFile.write("%d\t%4.2f\t%10d\t%4.2f\t%6.2f\t%6.2f\n"%(timeInterval,averTemp+zeroCelsius+corrTemp,int(my_rog.getAverageFluenceSum(th2f_fluence,float(lumi))/float(timeInterval)),trueTemp+zeroCelsius,iLeak,diLeak))#,begin_stable_beam_time,end_stable_beam_time,fill))
        
        begin_time_2=end_stable_beam_time
        begin_time_between_fills=end_stable_beam_time
        count +=1
        connection.close()

    proFile.write("TOTAL LUMI: %s fb-1"%totLumi)
    proFile.close()


if __name__ == "__main__":
    main()