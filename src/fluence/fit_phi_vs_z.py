import fitFluenceField
import ROOT as rt
from collections import namedtuple
import os

class ProjZFitFluka(object):
    
    def __init__(self):
        pass
    
    def set_fit_function(self, name, expr, xmin, xmax):
        self.fit_func_expr = expr
        self.tf1 = rt.TF1(name, expr, xmin, xmax)
        self.npars = self.tf1.GetNpar()
        return self.tf1
    
    def set_output_directory(self, out_dir):
        self.out_dir = out_dir
    
    def fit_z_proj(self, th2proj, tf1, r, xmin, xmax):
        c1 = rt.TCanvas("fit_%r"%r, "fit_%r"%r, 0, 0, 1000, 800)
        rt.Math.MinimizerOptions.SetDefaultMaxFunctionCalls(100000)
        th2proj.Fit(tf1, "Q", "", xmin, xmax)
        # th2proj.Fit(tf1, "", "", xmin, xmax)
        th2proj.GetXaxis().SetRangeUser(xmin, xmax)
        # th2proj.GetYaxis().SetRangeUser(0.04, 0.18)
        rt.gPad.SetGrid()
        th2proj.Draw()
        c1.SaveAs("%s/proj_plot_r%s_z_%s_%s.pdf"%(self.out_dir, r, xmin, xmax))
        ParPoint = namedtuple("ParPoint", "r p dp")
        pars = dict()
        for p_i in range(0, tf1.GetNpar()):
            pars["p%s"%p_i] = ParPoint(r, tf1.GetParameter(p_i), tf1.GetParError(p_i))
        pars["chi2"] = ParPoint(r, tf1.GetChisquare()/float(tf1.GetNDF()), 0)
        return pars
    
    def fit_z_proj_vs_r(self, th2, tf1, rmin, rmax, dr, xmin, xmax, par0, setparlims=True, parlims = None):
        r = rmin
        th2proj = None
        self.pars = dict()
        for p_i in range(0, tf1.GetNpar()):
            self.pars["p%s_z%s_r%s_%s"%(p_i, round(xmax*10), round(rmin*10), round(rmax*10))] = list()
        self.pars["chi2_z%s_r%s_%s"%(round(xmax*10), round(rmin*10), round(rmax*10))] = list()
        
        while r < rmax+dr/2.:
            for i,p in enumerate(par0):
                tf1.SetParameter(i,p)
                if setparlims:
                    tf1.SetParLimits(i,parlims[i][0],parlims[i][1])
            tf1.FixParameter(2,1.)
            bin_x = th2.GetXaxis().FindBin(r)
            th2proj = th2.ProjectionY("fluka_r_%s_mm"%round(r*10, 2), bin_x, bin_x)
            pars1 = self.fit_z_proj(th2proj, tf1, r, xmin, xmax)
            for p_i in range(0, tf1.GetNpar()):
                self.pars["p%s_z%s_r%s_%s"%(p_i, round(xmax*10), round(rmin*10), round(rmax*10))].append(pars1["p%s"%p_i])
            self.pars["chi2_z%s_r%s_%s"%(round(xmax*10), round(rmin*10), round(rmax*10))].append(pars1["chi2"])
            r += dr
        
        return self.pars
    
    def create_th1_par_vs_r(self, pars_dict, rmin, rmax, dr):
        th1s = dict()
        rmin -= dr/2.
        rmax += dr/2.
        # bin_r = 0
        for par_name in pars_dict:
            n = len(pars_dict[par_name])
            th1s[par_name] = rt.TH1D("h_%s"%par_name, "h_%s"%par_name, n, rmin, rmax)
            for par_point in pars_dict[par_name]:
                th1s[par_name].Fill(par_point.r, par_point.p)
                th1s[par_name].SetBinError(th1s[par_name].GetXaxis().FindBin(par_point.r), par_point.dp)
        return th1s
    
    def save_th1s(self, th1s, out_dir, expr_list, setpar_list, setparlim_list):
        canv = dict()
        exprs = dict()
        setpars = dict()
        setparslims = dict()
        for par_name in th1s:
            if "p" in par_name[0]:
                exprs[par_name] = expr_list[int(par_name[1])]
                setpars[par_name] = setpar_list[int(par_name[1])]
                setparslims[par_name] = setparlim_list[int(par_name[1])]
        for par_name in th1s:
            canv[par_name] = rt.TCanvas("canv_%s"%par_name, "%s"%par_name, 0,0,1000,800)
            if "p" in par_name[0]:
                tf1 = rt.TF1("f1_p%s"%par_name[1], exprs[par_name],th1s[par_name].GetXaxis().GetXmin(), th1s[par_name].GetXaxis().GetXmax())
                for i in range(0, tf1.GetNpar()):
                    tf1.SetParameter(i,setpars[par_name][i])
                    tf1.SetParLimits(i,setparslims[par_name][i][0],setparslims[par_name][i][1])
                th1s[par_name].Fit(tf1, "")
            th1s[par_name].Draw()
            rt.gPad.SetGrid()
            # rt.gStyle.SetOptStat(1111111)
            canv[par_name].SaveAs("%s/%s.pdf"%(out_dir, par_name))
        return 0

def run(outdir, zmin, zmax, rmin, rmax, dr, expr_list, setpar_list, setparlim_list, par0, parlims = None):
    projzfitfluka = ProjZFitFluka()
    projzfitfluka.set_output_directory(outdir)
    fluka_field = fitFluenceField.get_fluka_field()
    # tf1 = projzfitfluka.set_fit_function("f1","[0]*x*x+[2]", zmin, zmax)
    # tf1 = projzfitfluka.set_fit_function("f1","[0]/TMath::Sqrt(2*TMath::Pi())/[1]*exp(-x*x/[1]/[1]/2)+[2]", zmin, zmax)
    # tf1 = projzfitfluka.set_fit_function("f1","[0]*TMath::Gamma(([1]+1)/2.)/TMath::Gamma([1]/2.)/TMath::Sqrt([1]*TMath::Pi())*pow(1+x*x/[1]/[2]/[2],-([1]+1)/2.)+[3]", zmin, zmax)
    tf1 = projzfitfluka.set_fit_function("f1","[0]*pow(1+x*x/[1]/[1],-[2])+[3]", zmin, zmax)
    # tf1 = projzfitfluka.set_fit_function("f1","[0]*pow(1+x*x/[1],-[2])+[3]", zmin, zmax)
    setparlims = True
    if parlims == None:
        setparlims = False
    pars = projzfitfluka.fit_z_proj_vs_r(fluka_field, tf1, rmin, rmax, dr, zmin, zmax, par0, setparlims, parlims)
    th1s = projzfitfluka.create_th1_par_vs_r(pars, rmin, rmax, dr)
    projzfitfluka.save_th1s(th1s, "fit_fluka/find_pars_cauchy_final",expr_list, setpar_list, setparlim_list)

def main(parent_outdir):
    # run_dict = dict()
    zmaxs = [30]
    # zmaxs = [30]
    rmins = [2.05]
    rmaxs = [3.95]
    dr=0.1
    outdir = str()
    parlims = None
    parlims = [
        [0.,0.1],
        [2.,40.],
        [0.,5.],
        [-0.2,0.2]
    ]
    expr_list = [   
        # "[0]*pow(x,-[5])+[1]*exp(-(x-2.55)*(x-2.55)/[2]/[2])+[3]*exp(-(x-3.35)*(x-3.35)/[2]/[2])+[4]", 
        # "[0]*pow(x,-[1])+[2]",
        "[0]*x+[1]",
        # "[0]/(1+exp(-[1]*(x-[2])))+[3]",
        "[0]*x+[1]",
        "[0]",
        "[0]*pow(x,-[1])+[2]"
    ]
    setpar_list = [
        # [1, 0.005, 0.2, 0.005, 0., 1.5, 2.55,3.35],
        # [5, 1.5, 0.01],
        # [10,1, 2.4, 14],
        [-0.015, 0.08],
        [5,3],
        [1],
        [1, 1.5, 0]
    ]
    setparlim_list = [
        # [[-1,1e6], [-1,1e6], [-1,1e6], [0,1e6], [0,1e6], [0,1e6], [0,1e6], [0,1e6]],
        # [[0,20], [0.,4], [-1,3]],
        # [1, 1.5, 0.01],
        # [[5, 20], [0,5], [2,3.5], [10,20]],
        [[-1, 0],[0, 1]],
        [[0, 20],[0, 20]],
        [[0.5,2]],
        [[-1,1e6], [-1,1e6], [-1,1e6]]
    ]
    for zmax in zmaxs:
        for rmin in rmins:
            for rmax in rmaxs:
                outdir = "z%s_r%s_%s"%(round(zmax*10), round((rmin-dr)*10), round(rmax*10))
                # run_dict[outdir] = [-zmax, zmax, rmin,rmax]
                if not os.path.exists("%s/%s"%(parent_outdir, outdir)):
                    os.mkdir("%s/%s"%(parent_outdir, outdir))
                else:
                    pass
                # run("%s/%s"%(parent_outdir,outdir), -zmax, zmax, rmin, rmax, dr, [0.01,0.01], parlims)
                run("%s/%s"%(parent_outdir,outdir), -zmax, zmax, rmin, rmax, dr, expr_list, setpar_list, setparlim_list, [0.04,10,1,0.1], parlims)
                # run("%s/%s"%(parent_outdir,outdir), -zmax, zmax, rmin, rmax, dr, [0.01,20,0.], parlims)
                # run("%s/%s"%(parent_outdir,outdir), -zmax, zmax, rmin, rmax, dr, [1.,100,0.01,0.], parlims)
    # run("find_pars_z30", -50, 50, 2.05, 3.95, 0.1, [0.01,0.001,0.05])
    # run("find_pars_z50", -50, 50, 2.05, 3.95, 0.1, [0.01,0.001,0.05])
    # run("find_pars_z50", -50, 50, 2.05, 3.95, 0.1, [0.01,0.001,0.05])

main("fit_fluka/find_pars_cauchy_final")


