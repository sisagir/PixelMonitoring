import ROOT as rt
from . import fluka_l1
import math

n = [0,0,0,0]
r = [0,0,0,0]
z = [0,0,0,0]
fl = [0,0,0,0]

alpha_log = {}
alpha_lin = {}
alpha_lin_err = {}

for i in range(1,6):
   alpha_log[i] = list()
   alpha_lin[i] = list()
   alpha_lin_err[i] = list()


# fluence = [
#    0.0875378424909,
#    0.0849352178077,
#    0.0807983035748,
#    0.0769244261551,
# ]
# dfluence = [
#    0.00136665214972,
#    0.00139773261582,
#    0.00153435147896,
#    0.00177183515082,
# ]

fluence = [
   None,
   0.0940240145989,
   None,
   0.0633744011094,
]
dfluence = [
   None,
   0.00683477366132,
   None,
   0.00691847444178,
]
input_file_name = {
 1:"../RadDamSim/r_vs_z_minibias/onelinefit_2018_08_17/output.txt",
 2:"../RadDamSim/r_vs_z_minibias/onelinefit_2018_09_01/output.txt",
 3:"../RadDamSim/r_vs_z_minibias/onelinefit_2018_09_07/output.txt",
 4:"../RadDamSim/r_vs_z_minibias/onelinefit_2018_09_26/output.txt",
 5:"../RadDamSim/r_vs_z_minibias/onelinefit_2018_10_20/output.txt",
}

for m in range(1,6):
 input_file = open(input_file_name[m], "r")
 lines = input_file.readlines()
 for i in range(0,4):
  # if "real" in lines[i-2] and "lin" in lines[i]:
  if "lin" in lines[i] and i in (1,3):
   l = lines[i].split("=")[1]
   l = l.split('+-')
   alpha_lin[m].append(float(l[0]))
   alpha_lin_err[m].append(float(l[1]))
  else:
   alpha_lin[m].append(0.)
   alpha_lin_err[m].append(0.)
     
print((str(alpha_lin)))
print((str(alpha_lin_err)))
for i in range(0,4):
 for s in fluka_l1.fl_pos_dict:
  if ('LYR1' in s and 'MOD%s'%(i+1) in s):
   r[i] += fluka_l1.fl_pos_dict[s].r
   z[i] += abs(fluka_l1.fl_pos_dict[s].z)
   n[i] += 1.0

fl_error = [0,0,0,0]
for i in range(0,4):
 r[i]/=n[i]
 z[i]/=n[i]
 fl[i] = fluence[i]
 fl_error[i] = dfluence[i]

# month = "april"
# month = "july"
outfilename = {
   1:"fl_vs_z_all_1.pdf",
   2:"fl_vs_z_all_2.pdf",
   3:"fl_vs_z_all_3.pdf",
   4:"fl_vs_z_all_4.pdf",
   5:"fl_vs_z_all_5.pdf"
}

th1d_fl_vs_z_lin = rt.TH1D("Fluence_vs_z_lin","Fluence_vs_z",4,0,25.7)
th1d_fl_vs_z_log = rt.TH1D("Fluence_vs_z_log","Fluence_vs_z",4,0,25.7)
th1d_fl_vs_z_equiv = rt.TH1D("Fluence_vs_z_equiv","Fluence_vs_z_equiv",4,0,25.7)
th1d_fluka_vs_z = rt.TH1D("Fluka_vs_z","Fluka_vs_z",4,0,25.7)
th1d_v_vs_z = rt.TH1D("V_vs_z","V_vs_z",4,0,25.7)

vdepl_arr = {}
vdepl_arr_err = {}

for i in range(1,6):
   vdepl_arr[i] = list()
   vdepl_arr_err[i] = list()

vdepl_input_file = dict()
parent_input_dir = "../HVBiasScans/1f_mods_mini_scan/"
input_data = dict()
for j in (1,2,3,4):
 if j is not 3:
   vdepl_input_file = open("%s/pdfs_mod%s/vdepl_values_mod%s.txt"%(parent_input_dir,j,j))
   input_lines = vdepl_input_file.readlines()
 for i,l in enumerate(input_lines):
  if i == 0:
   continue
  else:
   l = l.split('\t')
   if j == 1 or j == 3:
    vdepl_arr[i].append(None)
    vdepl_arr_err[i].append(None)
   else:
    vdepl_arr[i].append(float(l[1]))
    vdepl_arr_err[i].append(float(l[2]))

c1 = rt.TCanvas("c1","c1",0,0,800,800)
# print(vdepl_arr["april"])
# print(fl)
for month in range(1,6):
 for i in (1,3):
  th1d_fl_vs_z_equiv.SetBinContent(i+1,(vdepl_arr[month][i]/fl[i])/(vdepl_arr[month][1]/fl[1]))
  th1d_fl_vs_z_equiv.SetBinError(i+1,(vdepl_arr[month][i]/fl[i])/(vdepl_arr[month][1]/fl[1])*
   math.sqrt(
   (vdepl_arr_err[month][i]/vdepl_arr[month][i])**2+
   (fl_error[i]/fl[i])**2+
   (vdepl_arr_err[month][1]/vdepl_arr[month][1])**2+
   (fl_error[1]/fl[1])**2
   )
  )
  th1d_fl_vs_z_lin.SetBinContent(i+1, alpha_lin[month][i]/alpha_lin[month][1])
  th1d_fl_vs_z_lin.SetBinError(i+1, alpha_lin[month][i]/alpha_lin[month][1]*
   math.sqrt((alpha_lin_err[month][i]/alpha_lin[month][i])**2+(alpha_lin_err[month][1]/alpha_lin[month][1])**2))
  th1d_fluka_vs_z.SetBinContent(i+1, fl[i]/fl[1])
  th1d_fluka_vs_z.SetBinError(i+1, fl[i]/fl[1]*math.sqrt(
   (fl_error[i]/fl[i])**2+
   (fl_error[1]/fl[1])**2
   )
  )
  th1d_v_vs_z.SetBinContent(i+1, vdepl_arr[month][i]/vdepl_arr[month][1])
  th1d_v_vs_z.SetBinError(i+1,vdepl_arr[month][i]/vdepl_arr[month][1]*math.sqrt(
   (vdepl_arr_err[month][i]/vdepl_arr[month][i])**2+
   (vdepl_arr_err[month][1]/vdepl_arr[month][1])**2
   )
  )
  # th1d_fl_vs_z_log.SetBinError(i+1,0.001)
  # th1d_fluka_vs_z.SetBinError(i+1,0.001)
  # th1d_v_vs_z.SetBinError(i+1,0.001)
 
 th1d_fl_vs_z_equiv.SetMarkerStyle(4)
 th1d_fl_vs_z_lin.SetLineColor(rt.kBlack)
 # th1d_fl_vs_z_log.SetLineColor(rt.kGreen+2)
 th1d_fluka_vs_z.SetLineColor(rt.kRed)
 th1d_v_vs_z.SetLineColor(rt.kBlue)
 th1d_fl_vs_z_lin.SetLineWidth(2)
 # th1d_fl_vs_z_log.SetLineWidth(2)
 th1d_fluka_vs_z.SetLineWidth(2)
 th1d_v_vs_z.SetLineWidth(2)
 
 th1d_fl_vs_z_lin.GetXaxis().SetTitle("|z|, cm")
 th1d_fl_vs_z_lin.GetYaxis().SetTitle("Ratio")
 
 th1d_fl_vs_z_lin.GetYaxis().SetRangeUser(0.7,1.5)
 
 rt.gPad.SetGrid()
 th1d_fl_vs_z_lin.Draw()
 th1d_v_vs_z.Draw("same")
 th1d_fluka_vs_z.Draw("same")
 th1d_fl_vs_z_equiv.Draw("same p")
 th1d_fl_vs_z_lin.Draw("same")
 leg = rt.TLegend(0.1,0.1,0.5,0.3)
 leg.AddEntry(th1d_fl_vs_z_lin, "(#Phi_{eq}^{real}(z)/#Phi_{eq}^{real}(0))/(#Phi_{eq}^{fluka}(z)/#Phi_{eq}^{fluka}(0))")
 leg.AddEntry(th1d_fl_vs_z_equiv, "(V(z)/V(0))/(#Phi_{eq}^{fluka}(z)/#Phi_{eq}^{fluka}(0))")
 leg.AddEntry(th1d_fluka_vs_z, "#Phi_{eq}^{fluka}(z)/#Phi_{eq}^{fluka}(0)")
 leg.AddEntry(th1d_v_vs_z, "V(z)/V(0)")
 leg.Draw("same")
 rt.gStyle.SetOptStat(000000000)
 
 c1.SaveAs(outfilename[month])