import ROOT as rt

fluence_file=rt.TFile.Open("FLUKA/fluence_field.root")
th2f_fluence = fluence_file.Get("fluence_allpart_6500GeV_phase1")
th2f_fluence.SetTitle("Fluence distribution for 1fb^{-1} vs. (r,z);r [cm];z [cm];#Phi_{eq} [n_{eq} cm^{-2}]")
ppXS = 79.1
conversionFactor=ppXS*10e-15/10e-27
th2f_fluence.Scale(conversionFactor)
c=rt.TCanvas("c1","c1",1400,800)
c.SetRightMargin(0.15)
rt.gStyle.SetOptStat(000000)
th2f_fluence.GetYaxis().SetRangeUser(-50,50)
# th2f_fluence.Draw("COLZ")
th2f_fluence.GetXaxis().SetRangeUser(4,16)
th2f_fluence.GetZaxis().SetTitleOffset(1.05)
# th2f_fluence.GetYaxis().SetTitle("z [cm]")
# th2f_fluence.GetXaxis().SetTitle("r [cm]")
# th2f_fluence.GetZaxis().SetTitle("#Phi_{eq} [n_{eq} cm^{-2}]")
th2f_fluence.Draw("COLZ")

cmsText = "CMS"
cmsTextFont = 61
writeExtraText = True
extraText = "Simulation Preliminary"
extraText2 = "2020"
extraText3 = "CMS FLUKA study v3.23.1.0"
extraTextFont = 52
lumiTextSize = 0.5
lumiTextOffset = 0.15
cmsTextSize = 0.5
cmsTextOffset = 0.1
# only used in outOfFrame version
relPosX = 0.045
relPosY = 0.035
relExtraDY = 1.2
# ratio of "CMS" and extra text size
extraOverCmsTextSize = 0.65
# lumi_13TeV = "20.1 fb^{-1}"
# lumi_8TeV = "19.7 fb^{-1}"
# lumi_7TeV = "5.1 fb^{-1}"
# lumiText
# lumiText += lumi_8TeV
# lumiText += " (13 TeV)"
# lumiText = "#sqrt{s} = 13 TeV "
t = c.GetTopMargin()
b = c.GetBottomMargin()
r = c.GetRightMargin()
l = c.GetLeftMargin()
latex = rt.TLatex()
latex.SetNDC()
latex.SetTextAngle(0)
latex.SetTextColor(rt.kBlack)
extraTextSize = extraOverCmsTextSize*cmsTextSize*1.1
latex.SetTextFont(42)
latex.SetTextAlign(31)
latex.SetTextSize(lumiTextSize*t)
# latex.DrawLatex(1-r, 1-t+lumiTextOffset*t, lumiText)
latex.SetTextFont(cmsTextFont)
latex.SetTextAlign(11)
latex.SetTextSize(cmsTextSize*t)
latex.DrawLatex(l+0.05, 1-t+lumiTextOffset*t-0.07, cmsText)
latex.SetTextFont(extraTextFont)
latex.SetTextSize(extraTextSize*t)
# latex.DrawLatex(l+0.05, 1-t+lumiTextOffset*t-0.09-0.06, extraText)
latex.DrawLatex(l+0.05+0.07, 1-t+lumiTextOffset*t-0.07, extraText)
latex.SetTextFont(extraTextFont-10)
# latex.DrawLatex(l+0.14, 1-t+lumiTextOffset*t-0.09-0.06, extraText2)
# latex.DrawLatex(l+0.16+0.06, 1-t+lumiTextOffset*t-0.07, extraText2)
latex.SetTextFont(51)
latex.SetTextSize(extraTextSize*t*0.85)
latex.SetTextColor(0)
latex.DrawLatex(l+0.54, 1-t+lumiTextOffset*t-0.05, extraText3)
c.SaveAs("ileak_vdep_appr_run2/fluence_th2f.pdf")
c.SaveAs("ileak_vdep_appr_run2/fluence_th2f.png")
# fpix_logo = "Forward Pixel Ring %s Disk %s" % (self.ring, self.disk)
# TrackSelctionText = fpix_logo
# latex.SetTextFont(61)
# latex.SetTextSize(extraTextSize*t)
# latex.SetTextFont(extraTextFont+10)
# latex.DrawLatex(l+0.4, 1-t+lumiTextOffset*t-0.15, TrackSelctionText)