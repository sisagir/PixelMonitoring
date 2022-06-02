


def remove_bad_fills(tag):
    filenames = {
        "r1d1": "run2_ls2_profiles/profile_r1d1rog1BpO_clean_wp1718_jul_anneal.txt",
        "r1d2": "clean_profiles/profile_r1d2rog2BmI_clean_wp1718_jul_anneal.txt",
        "r1d3": "run2_ls2_profiles/profile_r1d3rog1BpO_clean_wp1718_jul_anneal.txt",
        "r2d3": "run2_ls2_profiles/profile_r2d3rog1BmI_clean_wp1718_jul_anneal.txt",
        "r2d1": "run2_ls2_profiles/profile_r2d1rog2BmI_clean_wp1718_jul_anneal.txt",
        "r2d2": "run2_ls2_profiles/profile_r2d2rog2BmI_clean_wp1718_jul_anneal.txt",
    }
    filenames_out = {
        "r1d1": "run2_ls2_profiles/profile_r1d1rog1BpO_clean_wp1718_jul_anneal_nobadfills.txt",
        "r1d2": "run2_ls2_profiles/profile_r1d2rog2BmI_clean_wp1718_jul_anneal_nobadfills.txt",
        "r1d3": "run2_ls2_profiles/profile_r1d3rog1BpO_clean_wp1718_jul_anneal_nobadfills.txt",
        "r2d3": "run2_ls2_profiles/profile_r2d3rog1BmI_clean_wp1718_jul_anneal_nobadfills.txt",
        "r2d1": "run2_ls2_profiles/profile_r2d1rog2BmI_clean_wp1718_jul_anneal_nobadfills.txt",
        "r2d2": "run2_ls2_profiles/profile_r2d2rog2BmI_clean_wp1718_jul_anneal_nobadfills.txt",
    }
    prof = open(filenames[tag], "r")
    prof_out = open(filenames_out[tag], "w+")
    prof_lines=prof.readlines()
    fills=open("FillInfo_TotLumi.txt","r")
    bad_fills=open("badfills.txt","r")
    fills_lines=fills.readlines()
    bad_fills_lines = bad_fills.readlines()
    nofills = [6966,7188]
    fills_set=[]
    for f in fills_lines:
        if int(f[0:4]) > 5697 and int(f[0:4]) not in nofills:
            fills_set.append(f[0:4])
    
    bad_fills_set = []
    for f in bad_fills_lines:
        bad_fills_set.append(f[0:4])
    counter = 0
    flux0=0
    fout = open("profile_fills_%s.txt"%tag,"w+")
    zero_flux_fills = {"r1d1": [1381],
    "r1d2": [1382],
    "r1d3":[1370],
    "r2d3":[1227],
    "r2d1":[1240],
    "r2d2":[1251]}
    for i,l in enumerate(prof_lines):
        l_split = l.split('\t')
        t = int(l_split[0])
        flux = int(l_split[2])
        # ileak = int(l_split[5])
        if (t <= 1200 and flux > 0 and flux0 < 1) or i+1 in zero_flux_fills[tag]:
            fout.write("%s: %s -> %s\n"%(i+1,l.rstrip('\n'),fills_set[counter]))
            if fills_set[counter] in bad_fills_set:
                #1200	267.34	 136525535	264.34	678.50	-99.00
                # print 
                prof_out.write("%s\t%s\t%s\t%s\t%s\t%s\n"%(l_split[0],l_split[1],l_split[2],l_split[3],-99.00,l_split[5]))
            else:
                prof_out.write(l)
            counter += 1
        else:
            prof_out.write(l)
            fout.write("%s: %s\n" % (i+1, l.rstrip('\n')))
        flux0=flux
        # print("%s: counter = %s -> fills = %s"%(i, counter, len(fills_set)))
        
    print("all: counter = %s -> fills = %s"%(counter, len(fills_set)))
    # print fills_set

def main():
    # remove_bad_fills("r1d1")
    # remove_bad_fills("r1d3")
    # remove_bad_fills("r2d3")
    remove_bad_fills("r2d2")
    remove_bad_fills("r2d1")

main()
