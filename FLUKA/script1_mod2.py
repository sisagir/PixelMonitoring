import ROOT as rt
from . import fluka_l1
import math

n = [0,0,0,0]
r = [0,0,0,0]
z = [0,0,0,0]
fl = [0,0,0,0]

alpha_log = {"april":list(),"july":list()}
alpha_lin = {"april":list(),"july":list()}
alpha_lin_err = {"april":list(),"july":list()}

fluence = [
   0.0875378424909,
   0.0849352178077,
   0.0807983035748,
   0.0769244261551,
]
dfluence = [
   0.00136665214972,
   0.00139773261582,
   0.00153435147896,
   0.00177183515082,
]
input_file_name = {
 "april":"../RadDamSim/r_vs_z_full/onelinefit_2018_04_19/output.txt",
 "july":"../RadDamSim/r_vs_z_full/onelinefit_2018_07_30/output.txt"
}

for m in ("april","july"):
 input_file = open(input_file_name[m], "r")
 lines = input_file.readlines()
 for i in range(0,len(lines)):
  # if "real" in lines[i-2] and "lin" in lines[i]:
  if "lin" in lines[i]:
   l = lines[i].split("=")[1]
   l = l.split('+-')
   alpha_lin[m].append(float(l[0]))
   alpha_lin_err[m].append(float(l[1]))
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
   "april":"fl_vs_z_all_apr_mod2.pdf",
   "july":"fl_vs_z_all_jul_mod2.pdf"
}

th1d_fl_vs_z_lin = rt.TH1D("Fluence_vs_z_lin","Fluence_vs_z",4,0,25.7)
th1d_fl_vs_z_log = rt.TH1D("Fluence_vs_z_log","Fluence_vs_z",4,0,25.7)
th1d_fl_vs_z_equiv = rt.TH1D("Fluence_vs_z_equiv","Fluence_vs_z_equiv",4,0,25.7)
th1d_fluka_vs_z = rt.TH1D("Fluka_vs_z","Fluka_vs_z",4,0,25.7)
th1d_v_vs_z = rt.TH1D("V_vs_z","V_vs_z",4,0,25.7)

vdepl_arr = {
   # "april":[260.89, 249.69, 226.32, 210.66],
   "april": list(),
   "july":  list()
}
vdepl_arr_err = {
   # "april":[260.89, 249.69, 226.32, 210.66],
   "april": list(),
   "july":  list()
}

vdepl_input_file = dict()
parent_input_dir = "../HVBiasScans/1f_mods_full_scan/"
input_data = dict()
for i in range(1,5):
 vdepl_input_file = open("%s/pdfs_mod%s/vdepl_values_mod%s.txt"%(parent_input_dir,i,i))
 input_lines = vdepl_input_file.readlines()
 for i,l in enumerate(input_lines):
  if i == 0:
   continue
  else:
   l = l.split('\t')
   if "04" in l[0][5:7]:
    vdepl_arr["april"].append(float(l[1]))
    vdepl_arr_err["april"].append(float(l[2]))
   else:
    vdepl_arr["july"].append(float(l[1]))
    vdepl_arr_err["july"].append(float(l[2]))

c1 = rt.TCanvas("c1","c1",0,0,800,800)
# print(vdepl_arr["april"])
# print(fl)
mod0=1
for month in ["april","july"]:
 for i in range(mod0,4):
  th1d_fl_vs_z_equiv.SetBinContent(i+1,(vdepl_arr[month][i]/fl[i])/(vdepl_arr[month][mod0]/fl[mod0]))
  th1d_fl_vs_z_equiv.SetBinError(i+1,(vdepl_arr[month][i]/fl[i])/(vdepl_arr[month][mod0]/fl[mod0])*
   math.sqrt(
   (vdepl_arr_err[month][i]/vdepl_arr[month][i])**2+
   (fl_error[i]/fl[i])**2+
   (vdepl_arr_err[month][mod0]/vdepl_arr[month][mod0])**2+
   (fl_error[mod0]/fl[mod0])**2
   )
  )
  if i == mod0:
     th1d_fl_vs_z_equiv.SetBinError(i+1,0.)
  th1d_fl_vs_z_lin.SetBinContent(i+1, alpha_lin[month][i]/alpha_lin[month][mod0])
  th1d_fl_vs_z_lin.SetBinError(i+1, alpha_lin[month][i]/alpha_lin[month][mod0]*
   math.sqrt((alpha_lin_err[month][i]/alpha_lin[month][i])**2+(alpha_lin_err[month][mod0]/alpha_lin[month][mod0])**2))
  if i == mod0:
     th1d_fl_vs_z_lin.SetBinError(i+1, 0.)
  th1d_fluka_vs_z.SetBinContent(i+1, fl[i]/fl[mod0])
  th1d_fluka_vs_z.SetBinError(i+1, fl[i]/fl[mod0]*math.sqrt(
   (fl_error[i]/fl[i])**2+
   (fl_error[mod0]/fl[mod0])**2
   )
  )
  if i == mod0:
     th1d_fluka_vs_z.SetBinError(i+1, 0.)
  th1d_v_vs_z.SetBinContent(i+1, vdepl_arr[month][i]/vdepl_arr[month][mod0])
  th1d_v_vs_z.SetBinError(i+1,vdepl_arr[month][i]/vdepl_arr[month][mod0]*math.sqrt(
   (vdepl_arr_err[month][i]/vdepl_arr[month][i])**2+
   (vdepl_arr_err[month][mod0]/vdepl_arr[month][mod0])**2
   )
  )
  if i == mod0:
     th1d_v_vs_z.SetBinError(i+1, 0.)
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
 
 th1d_fl_vs_z_lin.GetYaxis().SetRangeUser(0.5,1.1)
 
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