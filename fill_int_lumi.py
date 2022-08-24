import cx_Oracle
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import os

def intLumi(output_file_name):
    # startFillRaw = 5698 #options.beginFill
    # endFillRaw = 7492   # options.endFill

    startFill = 5698 #int(startFillRaw)
    endFill   = 7492 #int(endFillRaw)

    fillNum = startFill
    connection = cx_Oracle.connect('cms_trk_r/1A3C5E7G:FIN@cms_omds_adg')
    cursor = connection.cursor()
    cursor.arraysize=50
    output_file = open(output_file_name, "w+")
    output_file.write("fillLumi = {\n")
    while fillNum <= endFill:
        goodFillsFile = open('FillInfo_TotLumi.txt', 'r+')
        for row in goodFillsFile.readlines():
            if str(fillNum) + "  " in row:
                print("Fill: %s"%fillNum)
                query= """
                select lhcfill, begintime, endtime
                from CMS_RUNTIME_LOGGER.RUNTIME_SUMMARY
                where  BEGINTIME IS NOT NULL and lhcfill is not null and lhcfill = :fillNum
                """
                cursor.execute(query, {"fillNum" : fillNum})

                fillTime = cursor.fetchall()
                begintime = fillTime[0][1]
                beginSTBtime = fillTime[0][1]
                endSTBtime = fillTime[0][2]
                begin20minSTB =  begintime + datetime.timedelta(0,1200) # 20 min into stable beam
                output_file.write("%s: {" % fillNum)
                is_fill_mt20min = begin20minSTB < endSTBtime
                if is_fill_mt20min:
                    brilcalc_out=os.popen('brilcalc lumi --begin \
                        "%02d/%02d/%02d %02d:%02d:%02d" --end "%02d/%02d/%02d %02d:%02d:%02d" \
                            -u /fb --output-style csv'%(beginSTBtime.month, beginSTBtime.day, beginSTBtime.year-2000,
                                                        beginSTBtime.hour,  beginSTBtime.minute, beginSTBtime.second,
                                                        begin20minSTB.month,   begin20minSTB.day,      begin20minSTB.year-2000,
                                                        begin20minSTB.hour,    begin20minSTB.minute,   begin20minSTB.second))
                    brilcalc_string = brilcalc_out.read()
                    brilcalc_arr_str = brilcalc_string.split("\n")
                    lumi = ""
                    for substr_brilcalc in brilcalc_arr_str:
                        if substr_brilcalc.find("#1") == 0:
                            lumi = substr_brilcalc.split(",")[-2]
                        elif substr_brilcalc.find("#0") == 0:
                            lumi = "0"
                    output_file.write("'20mins': %s," % lumi)
                else:
                    begin20minSTB = beginSTBtime
                brilcalc_out = os.popen('brilcalc lumi --begin \
                        "%02d/%02d/%02d %02d:%02d:%02d" --end "%02d/%02d/%02d %02d:%02d:%02d" \
                            -u /fb --output-style csv' % (begin20minSTB.month, begin20minSTB.day, begin20minSTB.year-2000,
                                                          begin20minSTB.hour,  begin20minSTB.minute, begin20minSTB.second,
                                                          endSTBtime.month,   endSTBtime.day,      endSTBtime.year-2000,
                                                          endSTBtime.hour,    endSTBtime.minute,   endSTBtime.second))
                brilcalc_string = brilcalc_out.read()
                brilcalc_arr_str = brilcalc_string.split("\n")
                lumi = ""
                for substr_brilcalc in brilcalc_arr_str:
                    if substr_brilcalc.find("#1") == 0:
                        lumi = substr_brilcalc.split(",")[-2]
                    elif substr_brilcalc.find("#0") == 0:
                        lumi = "0"
                output_file.write("'after20mins': %s," % lumi)
                output_file.write("'dates': [%s, %s, %s]},\n" % (beginSTBtime, begin20minSTB, endSTBtime))
        fillNum += 1
    output_file.write("}")

intLumi("fillIntLumi.py")