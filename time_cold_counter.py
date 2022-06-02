#!/bin/env python

import datetime
from collections import OrderedDict
import csv
import matplotlib.pyplot as plt


def gettemperatures(file):
  return_list=[]
  with open(file, newline='') as csvfile:
    # reader = csv.DictReader(csvfile,delimiter=',', quotechar='"')
    reader = csv.reader(csvfile,delimiter=',', quotechar='"')
    for i in range(len(reader.__next__())):
      return_list.append([])
    for row in reader:
      if ("201" not in row[0]):
        continue
      time=datetime.datetime.strptime(row[0], "%Y/%m/%d %H:%M:%S.%f")
      return_list[0].append(time)
      for i,value in enumerate(row[1:]):
        if value=="" and len(return_list[i+1])>0:
          value=return_list[i+1][-1]
        elif value=="" and len(return_list[i+1])==0:
          value="0"
        return_list[i+1].append(float(value))
  return return_list
  
def getTimesBelow(temp,temp_list):
  cooltimes=[]
  cold=False
  tmptime=None
  for ix,iy in zip(temp_list[0],temp_list[1]):
    if iy<temp and not cold:
      cold=True
      tmptime=ix
    if iy>temp and cold:
      cold=False
      cooltimes.append(ix-tmptime)
  totaltime=datetime.timedelta(0)
  for i in cooltimes:
    totaltime+=i
  return totaltime
      
      
activeBox=gettemperatures("DetectorProbes_20_12_17_to_19_02_18.csv")
## use value 28 because it seems to get the lowest temperature
activeBox_xy=activeBox[0],activeBox[28]

parkedBox1=gettemperatures("ParkedBox1_input_16_01_18_to_19_02_18.csv")
# use value 1
parkedBox1_xy=parkedBox1[0],parkedBox1[4]

parkedBox2=gettemperatures("ParkedBox2_input_16_01_18_to_19_02_18.csv")
# use value 1
parkedBox2_xy=parkedBox2[0],parkedBox2[4]

parkedBox3=gettemperatures("ParkedBox3_input_16_01_18_to_19_02_18.csv")
# use value 1
parkedBox3_xy=parkedBox3[0],parkedBox3[4]

# print(parkedBox2_xy)

# plt.clf()
# # for i in range(len(parkedBox2)):
  # # print(i, max(parkedBox2[i]), min(parkedBox2[i]))
# for i,ivalues in enumerate(parkedBox2[1:]):
    # plt.plot(parkedBox2[0],ivalues,label="%d"%i)
    # plt.ylabel('T/$^oC$')
    # plt.xlabel('time')
    # # 
# plt.legend()
# plt.show()
      

testposition=OrderedDict()
testposition["BpO"]=[["21.12.17 17:30", "02.01.18 8:00"], ["15.01.18 10:00","18.01.18 9:50"], ["06.02.18 15:20","08.02.18 9:10"],["14.02.18 14:10","19.02.18 8:10"]]
testposition["BpI"]=[["02.01.18 12:30", "15.01.18 9:00"],["08.02.18 10:10","14.02.18 12:10" ]]
testposition["BmI"]=[["18.01.18 10:14", "26.01.18 9:50"],["02.02.18 11:00","06.02.18 14:55"]]
testposition["BmO"]=[["26.01.18 11:24", "02.02.18 10:28"]]


waterglycoleBox1=OrderedDict()
waterglycoleBox1["BpI"]=[["18.01.18 17:00","08.02.18 9:50"],["14.02.18 12:10",datetime.datetime.now()]]
waterglycoleBox1["BpO"]=["08.02.18 11:05","14.02.18 12:10"]

waterglycoleBox2=OrderedDict()
waterglycoleBox2["BpO"]=["19.01.18 19:00","06.02.18 14:55"]
waterglycoleBox2["BmI"]=[["19.01.18 19:00","02.02.18 11:00"],["06.02.18 15:10",datetime.datetime.now()]]


waterglycoleBox3=OrderedDict()
waterglycoleBox3["BmI"]=["31.01.18 16:30","02.02.18 11:00"]
waterglycoleBox3["BmO"]=["02.02.18 11:00",datetime.datetime.now()]


hcs=["BpO","BpI","BmI","BmO"]
hc_temperature={}
for hc in hcs:
  hc_temperature[hc]=[[],[]]
  if hc in testposition:
    for interval in testposition[hc]:
      start=datetime.datetime.strptime(interval[0],"%d.%m.%y %H:%M")
      if(type(interval[1])==str):
        end=datetime.datetime.strptime(interval[1],"%d.%m.%y %H:%M")
      else:
        end=interval[1]
      for itime,ivalue in zip(activeBox_xy[0],activeBox_xy[1]):
        # if start-itime<datetime.timedelta(seconds=1) and abs(ivalue)<30:
        if start-itime<datetime.timedelta(seconds=1):
          hc_temperature[hc][0].append(itime)
          hc_temperature[hc][1].append(ivalue)
        # print(end-itime,hc,end,itime)
        if end-itime<datetime.timedelta(seconds=1):
          # input()
          break
        
  if hc in waterglycoleBox1:
    if type(waterglycoleBox1[hc][0])==list:
      for interval in waterglycoleBox1[hc]:
        start=datetime.datetime.strptime(interval[0],"%d.%m.%y %H:%M")
        if(type(interval[1])==str):
          end=datetime.datetime.strptime(interval[1],"%d.%m.%y %H:%M")
        else:
          end=interval[1]
    else:
      start=datetime.datetime.strptime(waterglycoleBox1[hc][0],"%d.%m.%y %H:%M")
      if(type(waterglycoleBox1[hc][1])==str):
        end=datetime.datetime.strptime(waterglycoleBox1[hc][1],"%d.%m.%y %H:%M")
      else:
        end=waterglycoleBox1[hc][1]
    for itime,ivalue in zip(parkedBox1_xy[0],parkedBox1_xy[1]):
      # print(hc,itime,start)
      if start-itime<datetime.timedelta(seconds=1) and abs(ivalue)<30:
        hc_temperature[hc][0].append(itime)
        hc_temperature[hc][1].append(ivalue)
      if end-itime<datetime.timedelta(seconds=1):
          # print(end-itime,end,itime,datetime.timedelta(seconds=1))
          break
  if hc in waterglycoleBox2:
    if type(waterglycoleBox2[hc][0])==list:
      for interval in waterglycoleBox2[hc]:
        start=datetime.datetime.strptime(interval[0],"%d.%m.%y %H:%M")
        if(type(interval[1])==str):
          end=datetime.datetime.strptime(interval[1],"%d.%m.%y %H:%M")
        else:
          end=interval[1]
    else:
      start=datetime.datetime.strptime(waterglycoleBox2[hc][0],"%d.%m.%y %H:%M")
      if(type(waterglycoleBox2[hc][1])==str):
        end=datetime.datetime.strptime(waterglycoleBox2[hc][1],"%d.%m.%y %H:%M")
      else:
        end=waterglycoleBox2[hc][1]

    for itime,ivalue in zip(parkedBox2_xy[0],parkedBox2_xy[1]):
      if start-itime<datetime.timedelta(seconds=1) and abs(ivalue)<30:
        hc_temperature[hc][0].append(itime)
        hc_temperature[hc][1].append(ivalue)
      if end-itime<datetime.timedelta(seconds=1):
          break
  if hc in waterglycoleBox3:
    if type(waterglycoleBox3[hc][0])==list:
      for interval in waterglycoleBox3[hc]:
        start=datetime.datetime.strptime(interval[0],"%d.%m.%y %H:%M")
        if(type(interval[1])==str):
          end=datetime.datetime.strptime(interval[1],"%d.%m.%y %H:%M")
        else:
          end=interval[1]
    else:
      start=datetime.datetime.strptime(waterglycoleBox3[hc][0],"%d.%m.%y %H:%M")
      if(type(waterglycoleBox3[hc][1])==str):
        end=datetime.datetime.strptime(waterglycoleBox3[hc][1],"%d.%m.%y %H:%M")
      else:
        end=waterglycoleBox3[hc][1]
    for itime,ivalue in zip(parkedBox3_xy[0],parkedBox3_xy[1]):
      if start-itime<datetime.timedelta(seconds=1) and abs(ivalue)<30:
        hc_temperature[hc][0].append(itime)
        hc_temperature[hc][1].append(ivalue)
      if end-itime<datetime.timedelta(seconds=1):
          break


# print(hc_temperature["BpO"])

for hc in hc_temperature:
    # plt.plot(hc_temperature[hc][0],hc_temperature[hc][1],label=hc,marker=".",linestyle="-")
    hc_temperature[hc][1]=[x for _,x in sorted(zip(hc_temperature[hc][0],hc_temperature[hc][1]))]
    hc_temperature[hc][0]=sorted(hc_temperature[hc][0])
    plt.plot(hc_temperature[hc][0],hc_temperature[hc][1],label=hc,linestyle="-")
    plt.ylabel('T/$^oC$')
    plt.xlabel('date')
    
    # 
# plt.xticks(x,  time)
# locs, labels = plt.xticks()
# plt.setp(labels, rotation=90)
plt.xticks(rotation=45)

plt.legend()
plt.tight_layout()
plt.savefig("cooling_time_HC_summary.png",bbox_inches='tight')
plt.savefig("cooling_time_HC_summary.pdf",bbox_inches='tight')



for hc in hc_temperature:
  temp=10
  print("%s below %sC   %s"%(hc,temp, (getTimesBelow(temp,hc_temperature[hc]))))
  temp=5                
  print("%s below %sC   %s"%(hc,temp, (getTimesBelow(temp,hc_temperature[hc]))))
  temp=0                
  print("%s below %sC   %s"%(hc,temp, (getTimesBelow(temp,hc_temperature[hc]))))
  temp=-5               
  print("%s below %sC   %s"%(hc,temp, (getTimesBelow(temp,hc_temperature[hc]))))
  temp=-10              
  print("%s below %sC   %s"%(hc,temp, (getTimesBelow(temp,hc_temperature[hc]))))
  temp=-18              
  print("%s below %sC   %s"%(hc,temp, (getTimesBelow(temp,hc_temperature[hc]))))
# plt.show()

# for hc in hc_temperature:
  # print(hc)
  # print(hc_temperature[hc])






BpOcooltimes = [
["27.12.17 16:19",
"27.12.17 18:16"],

["16.01.18 15:44",
"17.01.18 09:23"],
]

BpIcooltimes=[
["05.01.18 15:21",
"05.01.18 17:33" ],

["10.01.18 20:04",
"11.01.18 16:18" ],

["12.01.18 10:31",
"14.01.18 18:38"],
]

BpIcooltimesWaterGlycol=[
[
#"18.01.18 19:00", not really cold
"20.01.18 14:00", # now at <-0 

"xxxxxxxxxxx" ],

]

BpOcooltimesWaterGlycol=[
[
#"19.01.18 20:00",
"20.01.18 15:00",  # now at <-0 
"xxxxxxxxxxx" ],

]


totaltime=datetime.timedelta()
for start,end in BpOcooltimes:
  starttime=datetime.datetime.strptime(start, "%d.%m.%y %H:%M")
  endtime=datetime.datetime.strptime(end, "%d.%m.%y %H:%M")
  totaltime+=(endtime-starttime)

print(totaltime)
totaltime=datetime.timedelta()
for start,end in BpIcooltimes:
  starttime=datetime.datetime.strptime(start, "%d.%m.%y %H:%M")
  endtime=datetime.datetime.strptime(end, "%d.%m.%y %H:%M")
  totaltime+=(endtime-starttime)

print(totaltime)
  
  


