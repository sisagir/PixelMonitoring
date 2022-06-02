import datetime
import numpy as np
import argparse
import out_temp_wp

datetime_type = "%Y-%m-%d %H:%M:%S.%f"

class WarmPeriod(object):
    def __init__(self,file_name,begin_time,print_line):
        self.fin = open(file_name, "r")
        self.lines_input = self.fin.readlines()
        self.begin_time = begin_time
        self.print_line = print_line

    def get_datetime(self,line_number):
        lines_times = []
        for l in self.lines_input[0:line_number]:
            lines_times.append(l.split('\t')[0])
        array_dtimes = map(int,lines_times)
        array_dtimes = np.array(array_dtimes)
        dtime = np.sum(array_dtimes)
        # if self.print_line:
            # print("LINE %s: %s"%(line_number,self.lines_input[line_number-1]))
        # print datetime.timedelta(seconds=dtime)
        return self.begin_time+datetime.timedelta(seconds=dtime)
    
    def rewrite_profile(self):
        profile_out_dt = open("%s_wp1718.txt"%(self.fin.name.split('.')[-2].split('/')[-1]),'w+')
        for i,l in enumerate(self.lines_input):
            profile_out_dt.write("%s\t%s\t%s\n"%(l.rstrip('\n'),self.get_datetime(i),self.get_datetime(i+1)))
        
    def get_warmperiod_dates(self,dt_begin, dt_end):
        return [datetime.datetime.strftime(dt_begin, datetime_type),
            datetime.datetime.strftime(dt_end, datetime_type)]

    def get_temps_dates(self,part):
        self.temps_dates = out_temp_wp.temps_wp[part]

    def prod_prof_warm_period(self, wp_line_begin, wp_line_end):
        out_lines=[]
        dt_before_wp = self.get_datetime(wp_line_begin-1)
        t0 = dt_before_wp
        for i,l in enumerate(self.temps_dates):
            if i != 0:
                out_lines.append('%s\t273.15\t0\t%s\t-99.00\t-99.00\n' %
                             (int(round((l[0]-t0).total_seconds())), round(l[1],2)))
            else:
                out_lines.append('%s\t273.15\t0\t%s\t-99.00\t-99.00\n' %
                             (int(round((l[0]-t0).total_seconds())), 293.15))
            # print "%s | t0 | t | dt : %s | %s | %s\n" % (wp_line_begin+i,
            #      t0, l[0], int(round((l[0]-t0).total_seconds())))
            t0 = l[0]
        
        dt_after_wp=self.get_datetime(wp_line_end)
        print ("dt_after_wp = %s"%(dt_after_wp))
        out_lines.append('%s\t273.15\t0\t%s\t-99.00\t-99.00\n' %
                                 (int(round((dt_after_wp-t0).total_seconds())), 293.15))
        # print "%s | t0 | t | dt : %s | %s | %s\n" % (wp_line_begin+i+1,
        #                                              t0, dt_after_wp, int(round((dt_after_wp-t0).total_seconds())))
        return out_lines

    def insert_warm_period(self, line_begin_wp, line_end_wp):
        lines_before_wp = self.lines_input[0:line_begin_wp-1]
        lines_after_wp = self.lines_input[line_end_wp:-1]
        # temp_end=lines_after_wp[0].split('\t')[3]
        # dt_begin = self.get_datetime(line_begin_wp-1)
        # dt_end = self.get_datetime(line_end_wp)
        self.lines_wp = self.prod_prof_warm_period(line_begin_wp, line_end_wp)
        self.lines_all = []
        for l in lines_before_wp:
            self.lines_all.append(l)
        for l in self.lines_wp:
            self.lines_all.append(l)
        for l in lines_after_wp:
            self.lines_all.append(l)
        return self.lines_all

    def get_timedelta(self,dt,dt0):
        # dt0 = datetime.datetime.strftime(dt0, datetime_type)
        return dt-dt0

    def write_new_profile(self, outfile_name):
        fout = open(outfile_name,'w+')
        for l in self.lines_all:
            fout.write(l)
        

def main(args):
    line_number = args.line_number
    print_line = args.print_line
    file_name = args.input_file
    begin_time = datetime.datetime.strptime(args.begin_time,datetime_type)
    myWP = WarmPeriod(file_name,begin_time,print_line)
    myWP.get_temps_dates(args.part)
    myWP.rewrite_profile()
    lis = myWP.insert_warm_period(args.start_line_number,args.end_line_number)
    # print lis
    if args.print_line_only:
        mydate = myWP.get_datetime(line_number)
        print("date/time for line %s: %s"%(line_number,datetime.datetime.strftime(mydate, datetime_type)))
    else:
        myWP.write_new_profile("%s_wp1718.txt"%file_name.split(".")[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-b","--begin-time", dest='begin_time', type=str, default='2017-05-23 14:32:22.210863')
    parser.add_argument("-i","--input-file", dest='input_file', type=str)
    parser.add_argument("-l","--line-number", dest='line_number', type=int)
    parser.add_argument("-s","--start-line-number", dest='start_line_number', type=int)
    parser.add_argument("-f","--end-line-number", dest='end_line_number', type=int)
    parser.add_argument("-p","--print-line", dest='print_line', action='store_true')
    parser.add_argument("--part", dest='part', action='store')
    parser.add_argument("--print-line-only", dest='print_line_only', action='store_true')
    args = parser.parse_args()
    main(args)
