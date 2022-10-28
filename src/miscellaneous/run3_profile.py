import datetime
import ROOT as rt

from utils.modules_geom import ROG
from utils.rogring_pc import *
from data.fills_info.fillIntLumi import *
from utils.rogchannel_modules import *
from utils.SiPixelDetsUpdatedAfterFlippedChange import *


datetime_type = "%Y-%m-%d %H:%M:%S"

class Run3Sim(object):
    def __init__(self, input_profile, output_profile):
        self.inprof = open(input_profile,"r")
        self.outprof = open(output_profile,"w+")
        self.prof_lines = self.inprof.readlines()
    
    def set_scenario(self, wp_afterLS2, run3_years, run3_lumi, prof_end_date = '2019-11-20 00:00:00'):
        self.prof_end_date  = datetime.datetime.strptime(prof_end_date,datetime_type)
        self.wp_start = datetime.datetime.strptime(wp_afterLS2[0],datetime_type)
        self.wp_end = datetime.datetime.strptime(wp_afterLS2[1],datetime_type)
        self.dtime = datetime.timedelta(days=1)
        self.begin_Run3 = datetime.datetime(year=run3_years[0],month=6,day=1)
        self.end_Run3 = datetime.datetime(year=run3_years[-1],month=12,day=31)
        run3_duration = (self.end_Run3-self.begin_Run3).total_seconds()
        print("run3_duration(before) = %s"%run3_duration)
        self.warm_periods_run3 = [
            [datetime.datetime(year=2021,month=11,day=24),datetime.datetime(year=2021,month=12,day=1)],
            [datetime.datetime(year=2022,month=11,day=24),datetime.datetime(year=2022,month=12,day=1)],
        ]
        if run3_years[-1] == 2024:
            self.warm_periods_run3.append([datetime.datetime(year=2023,month=11,day=24),datetime.datetime(year=2023,month=12,day=1)],)
        
        self.storage_date_run3 = [
            [datetime.datetime(year=2021, month=12, day=1),
             datetime.datetime(year=2022, month=1, day=31)],
            [datetime.datetime(year=2022, month=12, day=1),
             datetime.datetime(year=2023, month=1, day=31)],
        ]
        if run3_years[-1] == 2024:
            self.storage_date_run3.append([datetime.datetime(
                year=2023, month=12, day=1), datetime.datetime(year=2024, month=1, day=31)],)
        for i,wp3 in enumerate(self.warm_periods_run3):
            run3_duration -= (wp3[1]-wp3[0]).total_seconds()
            run3_duration -= (self.storage_date_run3[i][1]-self.storage_date_run3[i][0]).total_seconds()
        print("run3_duration(after) = %s"%run3_duration)
        self.instlumi = float(run3_lumi)/float(run3_duration)
        
    def add_to_profile(self, part, disk, rog, ring):
        fluence_file=rt.TFile.Open("data/fluence/fluence_field_phase1_6500GeV.root")
        th2f_fluence = fluence_file.Get("fluence_allpart")
        rog_channel = part_disk_rog_ring_to_rogchannel_pcboardtemp(part, disk, rog, ring, 'rogchannel')
        my_rog = ROG(rog_channel)
        # prof_lines = []
        dt = self.prof_end_date
        while dt < self.wp_start:
            self.prof_lines.append('%s\t273.15\t0\t%s\t-99.00\t-99.00\n'%(int(self.dtime.total_seconds()),275.15))
            dt = dt + self.dtime
        while dt < self.wp_end:
            self.prof_lines.append('%s\t273.15\t0\t%s\t-99.00\t-99.00\n'%(int(self.dtime.total_seconds()),293.15))
            dt = dt + self.dtime
        for i,wp3 in enumerate(self.warm_periods_run3):
            while dt<wp3[0]:
                flux=int(my_rog.getAverageFluenceSum(th2f_fluence,float(self.instlumi)))
                self.prof_lines.append('%s\t273.15\t%s\t%s\t-99.00\t-99.00\n'%(int(self.dtime.total_seconds()),int(flux),263.15))
                dt = dt + self.dtime
            while dt<wp3[1]:
                self.prof_lines.append('%s\t273.15\t0\t%s\t-99.00\t-99.00\n'%(int(self.dtime.total_seconds()),293.15))
                dt = dt + self.dtime
            while dt<self.storage_date_run3[i][1]:
                self.prof_lines.append('%s\t273.15\t0\t%s\t-99.00\t-99.00\n'%(int(self.dtime.total_seconds()),278.15))
                dt = dt + self.dtime
        while dt < self.end_Run3:
            flux=int(my_rog.getAverageFluenceSum(th2f_fluence,float(self.instlumi)))
            # print("%s -> %s"%(self.instlumi,flux))
            self.prof_lines.append('%s\t273.15\t%s\t%s\t-99.00\t-99.00\n'%(int(self.dtime.total_seconds()),int(flux),263.15))
            dt = dt + self.dtime
        for l in self.prof_lines:
            self.outprof.write(l)

    def close_files(self):
        self.inprof.close()
        self.outprof.close()

