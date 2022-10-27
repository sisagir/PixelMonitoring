import ROOT as rt
import math
from FLUKA.fluka_l1 import *

class FlukaField(object):
    
    def __init__(self):
        self.fluka_field_file = "FLUKA/fluence_field.root"
        self.get_fluka_field()
    
    def change_fluka_field(self, fluka_field_file):
        self.fluka_field_file = fluka_field_file
        self.get_fluka_field()
    
    def get_bin_widths(self, dim):
        return {"r": self.fluka_field.GetXaxis().GetBinWidth(1), "z": self.fluka_field.GetYaxis().GetBinWidth(1)}[dim]
    
    def get_fluka_field(self):
        f = rt.TFile.Open(self.fluka_field_file)
        in_hist = f.Get('fluence_allpart_6500GeV_phase1')
        self.fluka_field = in_hist.Clone()
        self.fluka_field.SetDirectory(0)
        return self.fluka_field
    
    def Eval(self, r, z):
        bin_x = self.fluka_field.GetXaxis().FindBin(r)
        bin_y = self.fluka_field.GetYaxis().FindBin(z)
        val = self.fluka_field.GetBinContent(bin_x, bin_y)
        return val
    
    def Eval_error(self, r, z):
        bin_x = self.fluka_field.GetXaxis().FindBin(r)
        bin_y = self.fluka_field.GetYaxis().FindBin(z)
        val = self.fluka_field.GetBinError(self.fluka_field.GetBin(bin_x, bin_y))
        return val


class Fluka2DFit(object):

    def __init__(self):
        self.expr = "([0]*x+[1])/(1+y*y/([2]*x+[3])/([2]*x+[3]))+[4]*pow(x,[5])+[6]"
        self.rmin = 2.
        self.rmax = 4.
        self.zmin = -30.
        self.zmax = 30.
        self.part_derivs_tf1 = None
        self.get_tf2()
    
    def change_tf2(self, new_expr):
        self.expr = new_expr
        self.get_tf2()

    def tf2_r_to_l(self, r0 = 2.):
        new_fluka2dfit = Fluka2DFit()
        old_pars = self.pars
        old_par_errors = self.par_errors
        new_expr = self.expr.replace("x","TMath::Sqrt([%i]*[%i]+x*x)"%(self.get_npars(), self.get_npars()))
        new_pars = old_pars[:]
        new_pars.append(r0)
        new_par_errors = old_par_errors[:]
        new_par_errors.append(0.)
        new_fluka2dfit.change_tf2(new_expr)
        new_fluka2dfit.set_pars(new_pars)
        new_fluka2dfit.set_par_errors(new_par_errors)
        new_fluka2dfit.part_derivs_tf1 = self.part_derivs_tf1
        return new_fluka2dfit

    def set_pars(self, pars):
        self.pars = pars[:]
        self.par_errors = [0]*self.get_npars()
        for i in range(0, self.get_npars()):
            self.tf2.SetParameter(i,self.pars[i])
            self.tf2.SetParError(i,0.)
    
    def get_npars(self):
        return self.tf2.GetNpar()

    def set_par_errors(self, par_errors):
        self.par_errors = par_errors[:]
        for i in range(0, self.tf2.GetNpar()):
            self.tf2.SetParError(i,par_errors[i])
    
    def get_tf2(self):
        self.tf2 = rt.TF2("fluka_field_fit", self.expr, self.rmin, self.rmax, self.zmin, self.zmax)
        return self.tf2
    
    def Eval(self, r, z):
        val = self.tf2.Eval(r,z)
        return val
    
    def eval_integral(self, xmin, xmax, ymin, ymax):
        return self.tf2.Integral(xmin,xmax,ymin,ymax)
    
    def fluence_per_area(self, xmin, xmax, ymin, ymax):
        return self.eval_integral(xmin, xmax, ymin, ymax)/(xmax-xmin)/(ymax-ymin)
    
    def set_partial_derivatives(self, partial_derivs_expr, part_derivs_pars):
        self.part_derivs_tf1 = list()
        for i,pd_expr in enumerate(partial_derivs_expr):
            self.part_derivs_tf1.append(Fluka2DFit())
            self.part_derivs_tf1[i].change_tf2(pd_expr)
            self.part_derivs_tf1[i].set_pars(part_derivs_pars[i])
            self.part_derivs_tf1[i].set_par_errors([0]*len(part_derivs_pars[i]))
        return self.part_derivs_tf1

    def get_part_derivs_integrals(self, xmin, xmax, ymin, ymax, r0):
        part_derivs_tf1_integrals = list()
        part_derivs_tf1_change = list()
        for i,part_deriv in enumerate(self.part_derivs_tf1):
            part_derivs_tf1_change.append(part_deriv.tf2_r_to_l(r0))
            part_derivs_tf1_integrals.append(part_derivs_tf1_change[i].fluence_per_area(xmin, xmax, ymin, ymax))
        return part_derivs_tf1_integrals
    
    def get_integral_error(self, xmin, xmax, ymin, ymax, r0):
        var = 0.
        integrals = self.get_part_derivs_integrals(xmin, xmax, ymin, ymax, r0)
        for i,pd_integr in enumerate(integrals):
            var += (pd_integr*self.par_errors[i])*(pd_integr*self.par_errors[i])
        return math.sqrt(var)


class Check2DFit(object):

    def __init__(self, fluka_field, tf2_2d_fit):
        self.fluka_field = fluka_field
        self.tf2_2d_fit = tf2_2d_fit
    
    def diff(self, r, z):
        return self.fluka_field.Eval(r,z) - self.tf2_2d_fit.Eval(r,z)
    
    def weighted_diff(self, r, z):
        return self.diff(r,z)/self.fluka_field.Eval_error(r,z)

    def diff_matrix(self):
        pass

def get_aver_fluka(mod_number, layer, tf1_fit, mods_set = "all"):
    Lphi = 1.62
    Lz = 6.48
    aver_fluka = 0.
    aver_fluka_err = 0.
    n = 0.
    tf1_fit_changed = Fluka2DFit()
    mods_dict = {}
    if mods_set == "all":
        mods_dict = fl_pos_dict
    else:
        for m in mods_set:
            mods_dict[m] = fl_pos_dict[m]
    for mod_name in mods_dict:
        mod_position = mods_dict[mod_name]
        z0 = mod_position.z
        r0 = mod_position.r
        if "MOD%s"%mod_number in mod_name and "LYR%s"%layer in mod_name:
            tf1_fit_changed = tf1_fit.tf2_r_to_l(r0)
            aver_fluka += tf1_fit_changed.fluence_per_area(-Lphi/2., Lphi/2., z0-Lz/2., z0+Lz/2.)
            aver_fluka_err += tf1_fit_changed.get_integral_error(-Lphi/2., Lphi/2., z0-Lz/2., z0+Lz/2., r0)*tf1_fit.get_integral_error(-Lphi/2., Lphi/2., z0-Lz/2., z0+Lz/2., r0)
            n += 1.

    return (aver_fluka/n, math.sqrt(aver_fluka_err)/n)

def main():
    fl_field = FlukaField()
    fl_fit = Fluka2DFit()
    "a c k d b beta f"
    r0 = 2.73
    rmin = fl_fit.rmin
    rmax = fl_fit.rmax
    dr = fl_field.get_bin_widths(dim="r")
    zmin = fl_fit.zmin
    zmax = fl_fit.zmax
    dz = fl_field.get_bin_widths(dim="z")
    r = rmin + dr/2.
    z = zmin + dz/2.
    chi2 = 0.
    ndf = 0.
    L = 1.64
    Lz = 6.4
    z0 = 3.2
    
    my_fit_pars = [
        -0.0079183265975624993, 
        0.048823971714266258, 
        14.765057787869672, 
        -17.69499379359727, 
        0.5975359779098911, 
        -2.0280511817921987, 
        -0.0038413391485602397
    ]
    
    my_fit_par_errors = [
        0.0011047176665554483, 
        0.0024210259311981761, 
        1.7823223188870345, 
        4.0364675840851145, 
        0.0076633030277736339, 
        0.045502843940619431, 
        0.0041565953092060227
    ]

    fl_fit.set_pars(pars=my_fit_pars)
    fl_fit.set_par_errors(my_fit_par_errors)
    check = Check2DFit(fl_field, fl_fit)

    part_derivs_fluka_expr = [
        "x/(1+y*y/([0]+[1]*x)/([0]+[1]*x))",
        "1/(1+y*y/([0]+[1]*x)/([0]+[1]*x))",
        "2*x*([0]+[1]*x)*y*y/(pow([2]+[3]*x,3)*(1+y*y/([2]+[3]*x)/([2]+[3]*x)))",
        "2*([0]+[1]*x)*y*y/(pow([2]+[3]*x,3)*(1+y*y/([2]+[3]*x)/([2]+[3]*x)))",
        "pow(x,[0])+0*y",
        "[0]*pow(x,[1])*TMath::Log(x)+0*y",
        "[0]+0*x+0*y"
    ]

    part_derivs_pars = [
        [my_fit_pars[3], my_fit_pars[2]],
        [my_fit_pars[3], my_fit_pars[2]],
        [my_fit_pars[1], my_fit_pars[0], my_fit_pars[3], my_fit_pars[2]],
        [my_fit_pars[1], my_fit_pars[0], my_fit_pars[3], my_fit_pars[2]],
        [my_fit_pars[5]],
        [my_fit_pars[4], my_fit_pars[5]],
        [1.]
    ]

    while r < rmax:
        # print("r = %4.2f:"%r)
        while z < zmax:
            difference = check.diff(r,z)
            w_difference = check.weighted_diff(r,z)
            chi2 += w_difference*w_difference
            ndf += 1.
            # print("\tz = %4.2f: diff = %s, w_diff = %s"%(z, difference, w_difference))
            z += dz
        r += dr
        z = zmin + dz/2.
    ndf -= fl_fit.get_npars()
    chi2 /= ndf
    print(("CHI2 = %s"%chi2))
    fl_fit.set_partial_derivatives(part_derivs_fluka_expr, part_derivs_pars)
    new_fl_fit = fl_fit.tf2_r_to_l(r0)
    integral = new_fl_fit.eval_integral(-L/2., L/2., z0-Lz/2., z0+Lz/2.)
    integral_per_s = new_fl_fit.fluence_per_area(-L/2., L/2., z0-Lz/2., z0+Lz/2.)
    integral_error = new_fl_fit.get_integral_error(-L/2., L/2., z0-Lz/2., z0+Lz/2.,r0)
    print("Integral(lmin=%4.2f,lmax=%4.2f,zmin=%4.2f,zmax=%4.2f) = %s"%(-L/2., L/2., z0-Lz/2., z0+Lz/2., integral))
    print("1/S Integral(lmin=%4.2f,lmax=%4.2f,zmin=%4.2f,zmax=%4.2f) = %s +- %s"%(-L/2., L/2., z0-Lz/2., z0+Lz/2., integral_per_s, integral_error))
    fluka_field_val = fl_field.Eval(r0,z0)
    of_file = open("fluka_vals_hvgroup.txt", "w+")
    "FLUKA_FIELD(r0=%4.2f,z=%4.2f) = %s\n"%(r0,z0,fluka_field_val)
    mods_set = ["BPix_BmO_SEC7_LYR1_LDR5F_MOD2", "BPix_BmO_SEC7_LYR1_LDR6F_MOD4"]
    mod_numbers = (2,4)
    # mod_numbers = range(1,5)
    for mod_number in mod_numbers:
        aver_fluka, aver_fluka_err = get_aver_fluka(mod_number, 1, fl_fit, mods_set)
        of_file.write("%s: F = %s +- %s\n"%(mod_number, aver_fluka, aver_fluka_err))
    of_file.close()
    # print new_fl_fit.expr
    return 0

main()

