import argparse
from run3_profile import Run3Sim
# def main(args):
    # line_number = args.line_number
    # print_line = args.print_line
    # file_name = args.input_file
    # begin_time = datetime.datetime.strptime(args.begin_time,datetime_type)
    # mydate = get_datetime(line_number, print_line, file_name, begin_time)
    # print("date/time for line %s: %s"%(line_number,datetime.datetime.strftime(mydate, datetime_type)))

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
    # parser.add_argument("-b","--begin-time", dest='begin_time', type=str, default='2017-05-23 14:32:22.210863')
    # parser.add_argument("-i","--input-file", dest='input_file', type=str)
    # parser.add_argument("-l","--line-number", dest='line_number', type=int)
    # parser.add_argument("-p","--print-line", dest='print_line', action='store_true')
    # args = parser.parse_args()
    # main(args)

def main(args):
    my_run3sim = Run3Sim(args.input_file,args.output_file)
    wp_end = '2021-06-01 00:00:00'
    wp_start = {#"1m":'2020-12-01 00:00:00',
                   "2m":'2021-04-01 00:00:00',
                   "3m":'2021-03-01 00:00:00',
                   "4m":'2021-02-01 00:00:00'}
    my_run3sim.set_scenario(wp_afterLS2=[wp_start[args.wp_dur], wp_end],
                            run3_years=[2021,args.run3_end_year], 
                            run3_lumi=args.lumi, 
                            prof_end_date = '2019-11-20 00:00:00')
    my_run3sim.add_to_profile(args.part,args.disk,args.rog,args.ring)
    print "INST_LUMI: %s"%my_run3sim.instlumi

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input-file", dest='input_file', type=str)
    parser.add_argument("-o","--output-file", dest='output_file', type=str)
    parser.add_argument("-e","--end-year", dest='run3_end_year', type=int)
    parser.add_argument("-w","--wp-dur", dest='wp_dur', type=str)
    parser.add_argument("-l","--lumi", dest='lumi', type=str)
    parser.add_argument("-p", "--part", type=str, dest="part")
    parser.add_argument("-g", "--rog", type=int, dest="rog")
    parser.add_argument("-r", "--ring", type=int, dest="ring")
    parser.add_argument("-d", "--disk", type=int, dest="disk")
    args = parser.parse_args()
    main(args)
