import os
from utils import generalUtils as gUtl

fill_csv_file = "../../fills_info/data/fills_info/fills.csv"
os.system("cp "+fill_csv_file+" .")
fills_info = gUtl.get_fill_info(fill_csv_file)
good_fills = fills_info.fill_number.tolist()

ind=0
for fill in good_fills: 
	ind+=1
	if fill<6053: continue
	print(ind,"/",len(good_fills))
	os.system("root -l -b -q 'convertDCU.C++(\""+str(fill)+"_DCU_raw.txt\")'")
