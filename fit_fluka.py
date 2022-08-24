import ROOT as rt
import array
import argparse
import numpy

class Chi2ParMinimizer(object):
    def __init__(self, npars, nsize, pars_min, pars_max, include_pars_max = True):
        self.npars = npars
        self.nsize = nsize
        self.pars_step = list()
        self.pars_min = pars_min
        self.pars_max = pars_max
        if include_pars_max:
            for p_i in range(0,npars):
                self.pars_step.append((self.pars_max[p_i]-self.pars_min[p_i])/float(self.nsize-1))
        else:
            for p_i in range(0,npars):
                self.pars_step.append((self.pars_max[p_i]-self.pars_min[p_i])/float(self.nsize))
        shape = [self.nsize]*self.npars
        self.chi2_par_array = numpy.ndarray(shape)
        shape.append(self.npars)
        self.final_par_array = numpy.ndarray(shape)
        self.final_par_error_array = numpy.ndarray(shape)
    
    def get_par_value(self, indecies):
        pars_ret = list()
        for p_i in range(0,self.npars):
            pars_ret.append(self.pars_min[p_i]+indecies[p_i]*self.pars_step[p_i])
        return pars_ret
    
    def get_par_indecies(self, pars):
        indecies_ret = list()
        for p_i in range(0,self.npars):
            indecies_ret.append(int((pars[p_i]-self.pars_min[p_i])/self.pars_step[p_i]+0.1))
        return indecies_ret
    
    def set_chi2_values(self, par_values, chi2):
        indecies = tuple(self.get_par_indecies(par_values))
        self.chi2_par_array[indecies] = chi2
    
    def get_chi2_values(self, par_values):
        indecies = tuple(self.get_par_indecies(par_values))
        return self.chi2_par_array[indecies]
    
    def set_final_pars_values(self, par_values, final_pars, final_par_errors):
        indecies_for_chi2 = self.get_par_indecies(par_values)
        indecies_list = indecies_for_chi2[:]
        indecies_list.append(0)
        for i,final_par in enumerate(final_pars):
            indecies_list[-1] = i
            indecies = tuple(indecies_list)
            self.final_par_array[indecies] = final_par
            self.final_par_error_array[indecies] = final_par_errors[i]
    
    def get_final_pars_values(self, par_values):
        indecies_for_chi2 = self.get_par_indecies(par_values)
        indecies_list = indecies_for_chi2[:]
        indecies_list.append(0)
        final_pars = list()
        final_par_errors = list()
        for i in range(0,self.npars):
            indecies_list[-1] = i
            indecies = tuple(indecies_list)
            final_pars.append(self.final_par_array[indecies])
            final_par_errors.append(self.final_par_error_array[indecies])
        return [final_pars, final_par_errors]
    
    def minimize(self):
        index_min = self.chi2_par_array.argmin()
        indecies_min = numpy.unravel_index(index_min, self.chi2_par_array.shape)
        pars_min = self.get_par_value(indecies_min)
        chi2_min = self.chi2_par_array.min()
        final_pars = self.get_final_pars_values(pars_min)
        return {"pars": pars_min, "chi2": chi2_min, "final_pars": final_pars[0], "final_par_errors": final_pars[1]}
    
def fit_fl_proj(directory, fluka_proj, function, xmin, xmax, set_pars = [], set_par_limits = []):
    fit_func = rt.TF1("fit_func", function["expr"], 
            fluka_proj.GetXaxis().GetXmin(), fluka_proj.GetXaxis().GetXmax())
    if len(set_pars) > 0:
        fit_func.SetParameters(array.array('d',set_pars))
    if len(set_par_limits) > 0:
        for i,pl in enumerate(set_par_limits):
            fit_func.SetParLimits(i,pl[0],pl[1])
    fit_func.SetNpx(10000)
    c1 = rt.TCanvas("c1","c1",1000,800)
    c1.Draw()
    rt.gStyle.SetOptStat(00000)
    fluka_proj.GetXaxis().SetRangeUser(xmin,xmax)
    for i in range(0,1): fluka_proj.Fit(fit_func, "", "", xmin, xmax)
    range_val = "z" if "r" in fluka_proj.GetName() else "r"
    filename = "%s_%s_%s_range_%smm_%smm"%(fluka_proj.GetName(), 
            function["name"], range_val, int(xmin*10), int(xmax*10))
    filename = filename.replace('-','minus')
    c1.SaveAs("%s/%s.pdf"%(directory,filename))
    fout = open("%s/%s.txt"%(directory,filename), "w+")
    fout.write(str(function)+'\n')
    for i in range(0,fit_func.GetNpar()):
        fout.write('p%s = %4.4e\n'%(i, fit_func.GetParameter(i)))
    if fit_func.GetNDF() > 0.:
        fout.write("chi2 = %4.4f"%(fit_func.GetChisquare()/fit_func.GetNDF()))
    else:
        fout.write("chi2 = Nan")
    return [fluka_proj, fit_func]

def get_proj(fluka_th2d, x_val, proj_direction = "r"):
    if proj_direction == "r":
        bin_x = fluka_th2d.GetYaxis().FindBin(x_val)
        return fluka_th2d.ProjectionX("fluka_z_%s_mm"%int(x_val*10), bin_x, bin_x)
    else:
        bin_x = fluka_th2d.GetXaxis().FindBin(x_val)
        return fluka_th2d.ProjectionY("fluka_r_%s_mm"%int(x_val*10), bin_x, bin_x)

def get_fluka_field():
    f = rt.TFile.Open("FLUKA/fluence_field.root")
    in_hist = f.Get('fluence_allpart_6500GeV_phase1')
    h = in_hist.Clone()
    h.SetDirectory(0)
    return h

def get_tf2_fluka_fit(expr, pars, rmin, rmax, zmin, zmax):
    tf2 = rt.TF2("fluka_field_fit", expr, rmin, rmax, zmin, zmax)
    for i in range(0, tf2.GetNpar()):
        tf2.SetParameter(i,pars[i])
    return tf2

def get_fluka_field_value(fluka_field, r, z):
    bin_x = fluka_field.GetXaxis().FindBin(r)
    bin_y = fluka_field.GetYaxis().FindBin(z)
    val = fluka_field.GetBinContent(bin_x, bin_y)
    print("FLUKA(r=%4.2f,z=%4.2f) = %s"%(r,z,val))
    return val

def get_tf2_fluka_fit_value(tf2_fluka_field, r, z):
    val = tf2_fluka_field.Eval(r,z)
    print("FLUKA_FIT(r=%4.2f,z=%4.2f) = %s"%(r,z,val))
    return val

def get_fluka_value_diff(fluka_field, tf2_fluka_field, r, z):
    val = get_fluka_field_value(fluka_field, r, z) - get_tf2_fluka_fit_value(tf2_fluka_field, r, z)
    print("FLUKA - FLUKA_FIT (r=%4.2f,z=%4.2f) = %s"%(r,z,val))
    return val

def fit_fluence(directory, fluka_th2d, function, xmin, xmax, set_opts = "QN",set_pars = [], set_par_limits = []):
    fit_func = rt.TF2("fit_func", function["expr"], xmin[0], xmax[0], xmin[1], xmax[1])
    if len(set_pars) > 0:
        fit_func.SetParameters(array.array('d',set_pars))
    if len(set_pars) > 0:
        fit_func.SetParameters(array.array('d',set_pars))
    if len(set_par_limits) > 0:
        for i,pl in enumerate(set_par_limits):
            fit_func.SetParLimits(i,pl[0],pl[1])
    fit_func.SetNpx(10000)
    c1 = rt.TCanvas("c1","c1",1000,800)
    # c1.Draw()
    rt.gStyle.SetOptStat(00000)
    fluka_th2d.GetXaxis().SetRangeUser(xmin[0], xmax[0])
    fluka_th2d.GetYaxis().SetRangeUser(xmin[1], xmax[1])
    for i in range (0,1): fluka_th2d.Fit(fit_func, set_opts, "colz")
    filename = "%s_%s_ranges_r_%smm_%smm_z_%smm_%smm"%(fluka_th2d.GetName(), 
            function["name"], int(xmin[0]*10), int(xmax[0]*10), int(xmin[1]*10), int(xmax[1]*10))
    filename = filename.replace('-','minus')
    # c1.SaveAs("%s/%s.pdf"%(directory, filename))
    fout = open("%s/%s.txt"%(directory, filename), "w+")
    fout.write(str(function)+'\n')
    for i in range(0,fit_func.GetNpar()):
        fout.write('p%s = %4.4e\n'%(i, fit_func.GetParameter(i)))
    if fit_func.GetNDF() > 0.:
        fout.write("chi2 = %4.4f"%(fit_func.GetChisquare()))
    else:
        fout.write("chi2 = Nan")
    
    return [fluka_th2d, fit_func]

def main(args):
    fl_2d_histo = get_fluka_field()

    if args.noargs:
        # function = {"name": "radius", "expr": "[0]*pow(x,-[1])*exp(-[2]*x)"}
        # directory = "fit_fluka/rvals"
        # xvals = [(-30.0 + i) for i in range(0,60)]
        # pars = "16,-1.7,-0.01"
        # for xval in xvals:
        #     fl_proj = get_proj(fl_2d_histo, xval, proj_direction = "r")
        #     fit_fl_proj(directory, fl_proj, function, 0.2, 16.0, set_pars = [float(par) for par in pars.split(',')])
        # function = {"name": "zcoord", "expr": "[0]*exp(-x*x/(2*[1]*[1]))+[2]"}
        # [0]/([2]*sqrt([3]*TMath::Pi())*TMath::Gamma(([3]+1)/2.)/TMath::Gamma([3]/2.)*exp(-([3]+1)/2.*TMath::Log(1+1/[3]*(x-[1])/[2]*(x-[1])/[2]))+[4]
        expr = "[0]/([2]*sqrt([3]*TMath::Pi()))*TMath::Gamma(([3]+1)/2.)/TMath::Gamma([3]/2.)*exp(-([3]+1)/2.*TMath::Log(1+1/[3]*(y-[1])/[2]*(x-[1])/[2]))*pow(x,-[4])*exp(-[5]*x)+[6]"
        # form = rt.TFormula()
        # form.Compile(expr)
        # exit()
        function = {"name": "zcoord", "expr": expr}
        # function = {"name": "zcoord_laplace", "expr": "[0]*exp(-abs(x-[1])/[2])/(2*[2])+[2]"}
        directory = "fit_fluka/zvals"
        xvals = [(0.2 + i/10.) for i in range(0,160)]
        pars = "100,0,30,0.2,0"
        # par_limits = [[0,1000],[-10,10],[-1e10,1e10],[0,10]]
        par_limits = []
        # p0 = 9.8491e+02
        # p1 = -2.7553e-01
        # p2 = -1.5705e+01
        # p3 = 4.1872e+00
        for xval in xvals:
            fl_proj = get_proj(fl_2d_histo, xval, proj_direction = "z")
            fit_fl_proj(directory, fl_proj, function, -50, 50, set_pars = [float(par) for par in pars.split(',')], set_par_limits = par_limits)
        # xvals = [2.0 + i/10. for i in range(0,160)]
    
    else:
        if args.full:
            if args.pars == "minimize":
                floatter = lambda x: float(x.lstrip('\'').rstrip('\''))
                integrator = lambda x: int(x)
                pars_range_min = list(map(floatter, args.pars_range_min.split(',')))
                pars_range_max = list(map(floatter, args.pars_range_max.split(',')))
                pars_step = list()
                npars = int(args.npars)
                nsize = 2
                for p_i in range(0, npars):
                    pars_step.append((pars_range_max[p_i]-pars_range_min[p_i])/float(nsize-1))
                pars = pars_range_min[:]
                chi2_minimizer = Chi2ParMinimizer(npars, nsize, pars_range_min, pars_range_max)
                counter1 = 0
                while pars[npars-1] <= pars_range_max[npars-1] + 0.1*pars_step[npars-1]:
                    for p_i in range(1,npars):
                        if pars[p_i-1] > pars_range_max[p_i-1]:
                            pars[p_i] += pars_step[p_i]
                            pars[p_i-1] = pars_range_min[p_i-1]
                    if pars[npars-1] > pars_range_max[npars-1] + 0.1*pars_step[npars-1]:
                        continue
                    fit_output = fit_fluence(args.dir, fl_2d_histo, {"name": args.f_name, "expr": args.f_expr}, 
                            [float(args.xmin.split(',')[0]), float(args.xmin.split(',')[1])], 
                            [float(args.xmax.split(',')[0]) ,float(args.xmax.split(',')[1])], "QN", set_pars = pars)
                    chi2 = fit_output[1].GetChisquare()
                    final_pars = [fit_output[1].GetParameter(i) for i in range(0,npars)]
                    final_par_errors = [fit_output[1].GetParError(i) for i in range(0,npars)]
                    chi2_minimizer.set_chi2_values(pars, chi2)
                    chi2_minimizer.set_final_pars_values(pars, final_pars, final_par_errors)
                    # if counter1<80000: print("COUNTER: %s, PARS: %s"%(counter1, pars))
                    final_pars = [round(f,5) for f in final_pars]
                    print(("COUNTER:  %s -> CHI2: %s\nINITPARS: %s\nPARS:     %s"%(counter1, chi2, pars, final_pars)))
                    pars[0] += pars_step[0]
                    counter1 += 1
                chi2_pars_dict = chi2_minimizer.minimize()
                fit_fluence(args.dir, fl_2d_histo, {"name": args.f_name, "expr": args.f_expr}, [float(args.xmin.split(',')[0]), float(args.xmin.split(',')[1])], 
                            [float(args.xmax.split(',')[0]),float(args.xmax.split(',')[1])], "N" , set_pars = chi2_pars_dict["pars"])
                print(("CHI2: %s\nINITPARS: %s\nPARS: %s\nERRORS: %s"%(chi2_pars_dict["chi2"],chi2_pars_dict["pars"],chi2_pars_dict["final_pars"], chi2_pars_dict["final_par_errors"])))
            else:
                fit_fluence(args.dir, fl_2d_histo, {"name": args.f_name, "expr": args.f_expr}, [float(args.xmin.split(',')[0]), float(args.xmin.split(',')[1])], 
                    [float(args.xmax.split(',')[0]), float(args.xmax.split(',')[1])], set_pars = [float(par) for par in args.pars.split(',')])
        else:
            fl_proj = get_proj(fl_2d_histo, float(args.xval), proj_direction = args.proj_direction)
            par_limits = []
            fit_fl_proj(args.dir, fl_proj, {"name": args.f_name, "expr": args.f_expr}, float(args.xmin), float(args.xmax), set_pars = [float(par) for par in args.pars.split(',')], set_par_limits = par_limits)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--function-name', dest='f_name', action='store', help='function name')
    parser.add_argument('-e', '--function-expr', dest='f_expr', action='store', help='function expression', 
                        default="([0]*x+[1])/(1+y*y/([2]*x+[3])/([2]*x+[3]))+[4]*pow(x,[5])+[6]")
    parser.add_argument('--xmin',            dest='xmin',   action='store', help='xmin')
    parser.add_argument('--xmax',            dest='xmax',   action='store', help='xmax')
    parser.add_argument('-p', '--pars',          dest='pars',   action='store', help='pars')
    parser.add_argument('--pars-range-min',          dest='pars_range_min',   action='store', help='pars')
    parser.add_argument('--pars-range-max',          dest='pars_range_max',   action='store', help='pars')
    parser.add_argument('--npars',          dest='npars',   action='store', help='pars')
    parser.add_argument('-d', '--proj-dir',      dest='proj_direction',   action='store', help='proj direction')
    parser.add_argument('-x', '--xval',      dest='xval',   action='store', help='xval')
    parser.add_argument('-f', '--full',      dest='full',   action='store_true', help='full')
    parser.add_argument('-b', '--batch',dest='batch', action='store_true', help='batch')
    parser.add_argument('--dir',dest='dir', action='store', help='directory')
    parser.add_argument('--no-args',dest='noargs', action='store_true', help='batch')
    parser.add_argument('--check',dest='check', action='store_true', help='check')

    args = parser.parse_args()
    main(args)


# python fit_fluka.py -n "simult" -e "[0]/([2]*sqrt([3]*TMath::Pi()))*TMath::Gamma(([3]+1)/2.)/TMath::Gamma([3]/2.)*exp(-([3]+1)/2.*TMath::Log(1+1/[3]*(x-[1])/[2]*(x-[1])/[2]))*pow(x,-[4])*exp(-[5]*x)+[6]" --xmin '0,-30' --xmax '16,30' -p '100,0,30,0.2,-1.7,-0.01,0.1' --dir fit_fluka/simult -b -f
# python fit_fluka.py -n "simult" -e "[0]/([2]*sqrt([3]*TMath::Pi()))*TMath::Gamma(([3]+1)/2.)/TMath::Gamma([3]/2.)*exp(-([3]+1)/2.*TMath::Log(1+1/[3]*(y-[1])/[2]*(x-[1])/[2]))*pow(x,-[4])*exp(-[5]*x)+[6]" --xmin '0,-30' --xmax '16,30' -p '100,0,30,0.2,-1.7,-0.01,0.1' --dir fit_fluka/simult -b -f
# python fit_fluka.py -n "simult" -e "[0]/([2]*sqrt([3]*TMath::Pi()))*TMath::Gamma(([3]+1)/2.)/TMath::Gamma([3]/2.)*exp(-([3]+1)/2.*TMath::Log(1+1/[3]*(y-[1])/[2]*(x-[1])/[2]))*pow(x,-[4])*exp(-[5]*x)+[6]" --xmin '0,-30' --xmax '16,30' -p '10,0,30,0.2,-1.7,-0.01,0.1' --dir fit_fluka/simult -b -f
# python fit_fluka.py -n "simult" -e "[0]/([2]*sqrt([3]*TMath::Pi()))*TMath::Gamma(([3]+1)/2.)/TMath::Gamma([3]/2.)*exp(-([3]+1)/2.*TMath::Log(1+1/[3]*(y-[1])/[2]*(x-[1])/[2]))*pow(x,-[4])*exp(-[5]*x)+[6]" --xmin '0,-30' --xmax '16,30' -p '10,0,3,0.02,-1.7,-0.01,0.1' --dir fit_fluka/simult -b -f
# python fit_fluka.py -n "simult" -e "[0]/([2]*sqrt([3]*TMath::Pi()))*TMath::Gamma(([3]+1)/2.)/TMath::Gamma([3]/2.)*exp(-([3]+1)/2.*TMath::Log(1+1/[3]*(y-[1])/[2]*(x-[1])/[2]))*pow(x,-[4])*exp(-[5]*x)+[6]" --xmin '0,-30' --xmax '16,30' -p '10,0.1,3,0.02,-1.7,-0.01,0.1' --dir fit_fluk/simult -b -f
# python fit_fluka.py -n "simult" -e "[0]/([2]*sqrt([3]*TMath::Pi()))*TMath::Gamma(([3]+1)/2.)/TMath::Gamma([3]/2.)*exp(-([3]+1)/2.*TMath::Log(1+1/[3]*(y-[1])/[2]*(x-[1])/[2]))*pow(x,-[4])*exp(-[5]*x)+[6]" --xmin '0,-30' --xmax '16,30' -p '160,0.0,15,0.02,-1.7,-0.01,0.01' --dir fit_fluka/simult -b -f
# python fit_fluka.py -n "simult" -e "[0]/([2]*sqrt([3]*TMath::Pi()))*TMath::Gamma(([3]+1)/2.)/TMath::Gamma([3]/2.)*exp(-([3]+1)/2.*TMath::Log(1+1/[3]*(y-[1])/[2]*(x-[1])/[2]))*pow(x,-[4])*exp(-[5]*x)+[6]" --xmin '2.5,-30' --xmax '3.5,30' --dir fit_fluka/simult -b -f --npars 7 --pars-range-min '20,0,10,0,-3,-0.1,0.1' --pars-range-max '200,5,30,5,3,0.1,0.5'