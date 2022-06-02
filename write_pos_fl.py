import ROOT as rt
import SiPixelDetsUpdatedAfterFlippedChange_BPIX as pos
from collections import namedtuple
import argparse

def weight_f(z0,dz_full,dz,zmin,zmax):
    wl = -((z0 - dz_full/2.) - zmax)/dz
    wr =  ((z0 + dz_full/2.) - zmin)/dz
    # print "wl=%s - wr=%s"%(wl, wr)
    # print "z0,dz_full,dz,zmin,zmax = (%s,%s,%s,%s,%s)"%(z0,dz_full,dz,zmin,zmax)
    weight = dz/dz_full
    if wl < 0 or wr < 0: return 0
    elif wl < 1 and wr > 1: return wl*weight
    elif wr < 1 and wl > 1: return wr*weight
    else: return weight
    
def get_integral_fl(histo,r,z0,method="aver",dz_full=6.4,dz=1.):
    zmin = histo.GetYaxis().GetBinLowEdge(histo.GetYaxis().FindBin(z0))
    zmax = histo.GetYaxis().GetBinLowEdge(histo.GetYaxis().FindBin(z0)+1)
    fl_dict = {}
    if method == "aver":
        fl = weight_f(z0,dz_full,dz,zmin,zmax)*histo.GetBinContent(
                histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0))
        fl_dict[(zmin+zmax)/2.] = weight_f(z0,dz_full,dz,zmin,zmax)*histo.GetBinContent(
                histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0))
    else:
        fl_dict[(zmin+zmax)/2.] = histo.GetBinContent(
                histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0))
        fl = histo.GetBinContent(
                histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0))
    n = 1.
    
    for i in range(1,5):
        zmin = histo.GetYaxis().GetBinLowEdge(histo.GetYaxis().FindBin(z0+i*dz))
        zmax = histo.GetYaxis().GetBinLowEdge(histo.GetYaxis().FindBin(z0+i*dz)+1)
        # print "zmax=%s - zmin=%s"%(zmax,zmin)
        # print "w = %s"%weight_f(z0,dz_full,dz,zmin,zmax)
        if method == "aver":
            fl_dict[(zmin+zmax)/2.] = weight_f(z0,dz_full,dz,zmin,zmax)*histo.GetBinContent(
                    histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0+i*dz))
            fl += weight_f(z0,dz_full,dz,zmin,zmax)*histo.GetBinContent(
                    histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0+i*dz))
        else:
            fl_dict[(zmin+zmax)/2.] = histo.GetBinContent(
                    histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0+i*dz))
            if fl < histo.GetBinContent(histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0+i*dz)):
                fl = histo.GetBinContent(histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0+i*dz))
            else:
                pass
        
        zmin = histo.GetYaxis().GetBinLowEdge(histo.GetYaxis().FindBin(z0-i*dz))
        zmax = histo.GetYaxis().GetBinLowEdge(histo.GetYaxis().FindBin(z0-i*dz)+1)
        # print "zmax=%s - zmin=%s"%(zmax,zmin)
        # print "w = %s"%weight_f(z0,dz_full,dz,zmin,zmax)
        if method == "aver":
            fl += weight_f(z0,dz_full,dz,zmin,zmax)*histo.GetBinContent(
                histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0-i*dz))
            fl_dict[(zmin+zmax)/2.] = weight_f(z0,dz_full,dz,zmin,zmax)*histo.GetBinContent(
                histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0-i*dz))
        else:
            fl_dict[(zmin+zmax)/2.] = histo.GetBinContent(
                histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0-i*dz))
            if fl < histo.GetBinContent(histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0+i*dz)):
                fl = histo.GetBinContent(histo.GetXaxis().FindBin(r),histo.GetYaxis().FindBin(z0+i*dz))
            else:
                pass
        n +=2
    return fl

def get_th2d(histo, pos_dict):
    histo_2d = rt.TH2D("fluence","Fluence",histo.GetNbinsX(),histo.GetXaxis().GetXmin(),
        histo.GetXaxis().GetXmax(),histo.GetNbinsY(),histo.GetYaxis().GetXmin(),
        histo.GetYaxis().GetXmax())
    outfile = rt.TFile.Open("histo_2d.root","recreate")


def write_pos_fl(histo, pos_dict):
    fw = open('FLUKA/fluka_l1.py','w')
    fw.write('''from collections import namedtuple
    \n\nPosFluence = namedtuple('PosFluence', 'r phi z fluence')\n''')
    fw.write('fl_pos_dict = {\n')
    for m,p in pos_dict.iteritems():
        fw.write('"%s": PosFluence(r = %s, phi = %s, z = %s, fluence = %s),\n'%(m,p[0],p[1],p[2],
            histo.GetBinContent(histo.GetXaxis().FindBin(p[0]), histo.GetYaxis().FindBin(p[2]))))
        # print "%s - %s"%(histo.GetXaxis().FindBin(p[0]), histo.GetYaxis().FindBin(p[2]))
    fw.write('}')
    fw.close()

def average_fl(fl_dict,histo):
    FluncePointAverage = namedtuple('FluncePointAverage', 'r phi z fluence')
    n = 0.
    aver_r=0.
    aver_phi=0.
    aver_z=0.
    aver_fl = 0
    
    for m,pos_fl in fl_dict.iteritems():
        if 'LYR1' in m:
            print "%s -> %s"%(m,pos_fl)
            aver_r += pos_fl.r
            aver_phi += pos_fl.phi
            aver_z += pos_fl.z
            aver_fl += get_integral_fl(histo,pos_fl.r,pos_fl.z,"max")
            n += 1.

    fl_aver = FluncePointAverage(r=aver_r/n,phi=aver_phi/n,
                z=aver_z/n,fluence=aver_fl/n)
    return fl_aver

def histo_draw(fl_pos, aver_r, in_histo, out_file_name):
    out_root_file = rt.TFile.Open(out_file_name,"recreate")
    c1 = rt.TCanvas("c1", "canva", 1200, 800)
    histo = rt.TH1D("flunce_vs_z", "Fluence vs z", 100, -50, 50)
    bin_r = in_histo.GetXaxis().FindBin(aver_r)
    for z in range(-50,50,1):
        bin_z = in_histo.GetYaxis().FindBin(z+0.5)
        fl = in_histo.GetBinContent(bin_r, bin_z)
        histo.Fill(z, fl)
        histo.SetBinError(histo.GetXaxis().FindBin(z+0.5),0)
    histo.GetXaxis().SetTitle("z [cm^{-1}]")
    histo.GetYaxis().SetTitle("#Phi_{eq}/C for 1 fb^{-1} [n_{eq}/cm^{-2}]")
    histo.SetMinimum(0.055)
    histo.SetMaximum(0.105)
    rt.gStyle.SetOptStat(0000000)
    c1.Draw()
    histo.Draw()
    c1.SaveAs("BPix_studies/%s.pdf"%out_file_name.split('.')[0])
    out_root_file.Write()
    out_root_file.Close()

def main(args):
    f = rt.TFile.Open("FLUKA/fluence_field.root")
    histo = f.Get("fluence_allpart_6500GeV_phase1")
    to_do = args.to_do
    if to_do == 'write':
        pos_dict = pos.name_pos_map
        write_pos_fl(histo, pos_dict)
    elif to_do == 'aver':
        from FLUKA import fluka_l1
        fl_pos = fluka_l1.fl_pos_dict
        fl_aver = average_fl(fl_pos,histo)
        print "AVERAGE FLUENCE: %s"%fl_aver.fluence
        print "AVERAGE R      : %s"%fl_aver.r
        print "AVERAGE PHI    : %s"%fl_aver.phi
        print "AVERAGE Z      : %s"%fl_aver.z
    elif to_do == 'histo_draw':
        from FLUKA import fluka_l1
        fl_pos = fluka_l1.fl_pos_dict
        fl_aver = average_fl(fl_pos,histo)
        histo_draw(fl_pos,2.7,histo,"fl_vs_z_l1_27mm.root")
        histo_draw(fl_pos,3.2,histo,"fl_vs_z_l1_32mm.root")
        histo_draw(fl_pos,fl_aver.r,histo,"fl_vs_z_l1_29mm_aver_r.root")
        get_th2d(histo, fl_pos)
    elif to_do == "get_integr_fl":
        f = rt.TFile.Open("FLUKA/fluence_field.root")
        histo = f.Get("fluence_allpart_6500GeV_phase1")
        print get_integral_fl(histo,2.9,0,"max")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--to-do', dest='to_do', action='store', help='to_do', choices = ["write", "aver", "histo_draw", "get_integr_fl"])
    parser.add_argument('-b', '--batch',dest='batch', action='store_true', help='batch')
    # parser.add_argument('-z', dest='z', action='store', help='z')
    args = parser.parse_args()
    # to_do='histo_draw'
    main(args)


# 0.0882050022483
# 0.0845220926884
# 0.084028
# 0.0859955711871
# begin fill 5698
# 8.9275E-02