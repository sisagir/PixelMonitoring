import re
import csv

def rogchannel_pc():
    fin = open("Cabling_Map_for_FPix_Phase_1_Detector.csv")
    csv_reader = csv.DictReader(fin)
    ret_dict = {}
    # for 
    for row in csv_reader:
        if row["HV group"] == '':
            continue
        else:
            channel_str = "channel00%s"%str(channel(row["HV group"]))
        try:
            ret_dict[pc_name_to_rogchannel(row["PC name"])+"/"+channel_str].append(row["Official name of position"])
        except KeyError:
            ret_dict[pc_name_to_rogchannel(row["PC name"])+"/"+channel_str] = [row["Official name of position"]]
    return ret_dict


def rogchannel_pc_write(out_write):
    fout = open(out_write,"w+")
    ret_dict = rogchannel_pc()
    fout.write("rogchannel_pc = {\n")
    for k, r in ret_dict.iteritems():
        fout.write("'%s': %s,\n"%(k,str(r)))
    fout.write("}")
    fout.close()

def channel(HV_group):
    ret = None
    if "HV2" in HV_group:
        ret = 3
    elif "HV1" in HV_group:
        ret = 2
    return ret


def pc_name_to_pc(pc_name):
    ret = "Pixel"
    parts = pc_name.split('_')
    if "FPix" in pc_name:
        ret += "Endcap_"
    ret = ret+"_"+parts[2]+"_PC_"+parts[3][1]+str(ord('A')-ord('@'))
    return ret


def pc_name_to_rogchannel(pc_name):
    ret = "Pixel"
    parts = pc_name.split('_')
    if "FPix" in pc_name:
        ret += "EndCap_"
    ret = ret+parts[2]+"_"+parts[3]+"_ROG"+parts[-1][-1]
    return ret

def rogchannel_to_pcboard(rogchannel):
    ret = "PixelEndcap_"
    rog,channel = rogchannel.split('/')
    rog_list = rog.split('_')
    print rog_list
    abcd = 'ABCD'
    ret = ret + rog_list[1] + "_PC_" + rog_list[2][-1] + abcd[int(rog_list[3][-1])-1]
    return ret

def part_disk_rog_ring_to_rogchannel_pcboardtemp(part,disk,rog,ring,mytype):
    ret_dict={'rogchannel':'','pcboard':''}
    ret_dict['rogchannel'] = "%s_%s_D%s_ROG%s/channel00%s"%('PixelEndCap',part,disk,rog,[3,2][ring-1])
    ret_dict['pcboard'] = "%s_%s_PC_%s%s" % (
        'PixelEndcap', part, disk, 'ABCD'[rog-1])
    return ret_dict[mytype]

# PixelEndcap_BmI_PC_1B
# portcard_FPix_BmI_D1_PRT1
# PixelEndCap_BmI_D3_ROG2/channel003
# FPix_BpI_D1_BLD6_PNL2_RNG1
