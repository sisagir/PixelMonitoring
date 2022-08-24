import re

def get_geometry(input_file, output_file, part):
    reg_exp = ''
    if part == 'fpix':
        reg_exp = 'FPix_B[m,p][I,O]_D.*_BLD.*_PNL.*_RNG.* r/phi/z = .*/.*/.* cmssw'
    elif part == 'bpix':
        reg_exp = 'BPix_B[m,p][I,O]_SEC[0-9]_LYR[0-9]_LDR.*_MOD[0-9] r/phi/z = .*/.*/.* cmssw'
    fin = open(input_file,"r")
    fout = open(output_file,"w")
    lines = fin.readlines()
    # map_name_pos = {}
    fout.write("######\n")
    fout.write("name_pos_map = {\n")
    for l in lines:
        s1 = re.findall(reg_exp,l)
        if len(s1) != 0:
            s1 = s1[0]
            s1 = s1.split(' ')
            name_m = s1[0]
            pos_m = list(map(float,s1[3].split('/')))
            fout.write("'%s': %s,\n"%(name_m,str(pos_m)))
            # map_name_pos[name_m] = pos_m
    fout.write("}")


input_file = "SiPixelDetsUpdatedAfterFlippedChange.txt"
output_file = "SiPixelDetsUpdatedAfterFlippedChange_BPIX.py"

get_geometry(input_file,output_file,'bpix')