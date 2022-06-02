
def clean_profile(profile_name):
  fin_name = profile_name
  fin = open(fin_name, "r")
  finlines = fin.readlines()
  l0 = '265.90'
  for i in range(0,20):
    for i,l in enumerate(finlines):
      lsplit = l.split('\t')
      # print lsplit
      if lsplit[3] == '273.15':
        # print('before: '+finlines[i])
        finlines[i] = lsplit[0]+'\t'+lsplit[1]+'\t'+lsplit[2]+'\t'+l0+'\t'+lsplit[4]+'\t'+lsplit[5]
        # print('after: '+finlines[i])
      l0 = lsplit[3]
  fout = open("clean_profiles/"+fin_name.split('.')[0]+'_clean.txt', "w+")
  for l in finlines:
    fout.write(l)
  return finlines

def addLS2(profile_name,LS2_filename):
  fin_name = profile_name
  fls2in_name = "../pixel-annealing/workdir/"+LS2_filename
  fls2in = open(fls2in_name, "r")
  fls2in_lines = fls2in.readlines()
  fin = open("clean_profiles/"+fin_name, "r")
  finlines = fin.readlines()
  fout = open("run2_ls2_profiles/"+fin_name.split('.')[0]+'_ls2.txt', "w+")
  for l in finlines:
    fout.write(l)
  fout.write('\n')
  for l in fls2in_lines:
    fout.write(l)
  fout.close()
  fin.close()
  return fls2in_lines

def main():
  # list_profile = ["profile_r1d1rog1BpO.txt","profile_r1d3rog1BpO.txt","profile_r2d3rog3BmI.txt"]
  # list_profile_clean = ["profile_r1d1rog1BpO_clean.txt","profile_r1d3rog1BpO_clean.txt","profile_r2d3rog3BmI_clean.txt"]
  # ls2_input = ["LS2_bpo_1.txt","LS2_bpo_1.txt","LS2_bmi_1.txt"]

  # list_profile = ["profile_r1d2rog2BmI.txt"]
  list_profile = [
                  # "profile_r2d3rog1BmI.txt",
                  "profile_r2d1rog2BmI.txt",
                  "profile_r2d2rog2BmI.txt",
                  # "profile_r1d2rog1BpO.txt",
                  # "profile_r2d1rog2BmI.txt",
                  # "profile_r2d2rog2BmI.txt"
                  ]
  list_profile_clean = ["profile_r2d1rog2BmI_clean.txt",
                        "profile_r2d2rog2BmI_clean.txt",]
  ls2_input = ["LS2_bmi_1.txt", "LS2_bmi_1.txt"]

  for i,pf in enumerate(list_profile):
    clean_profile(pf)
    # addLS2(list_profile_clean[i], ls2_input[i])

if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-p","--profile", dest='profile', type=str)
    # parser.add_argument("-l","--ls2-file", dest='ls2_file', type=str)
    # args = parser.parse_args()
    main()
