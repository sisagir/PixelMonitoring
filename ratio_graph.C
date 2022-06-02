void ratioplot(TFile *_file0, TGraph *h1, TGraph *h2, int nMperROG, int ring, int disk, double hmax, TString out_name, TString out_name2) { //h1 - simulation, h2 - data
   // Define two gaussian histograms. Note the X and Y title are defined
   // at booking time using the convention "Hist_title ; X_title ; Y_title"
   // TH1F *h1 = new TH1F("h1", "Two gaussian plots and their ratio;x title; h1 and h2 gaussian histograms", 100, -5, 5);
   // TH1F *h2 = new TH1F("h2", "h2", 100, -5, 5);
   // TGraph *h1 = _file0->Get(gr1);
   // TGraph *h2 = _file0->Get(gr2);
   // h1->FillRandom("gaus");
   // h2->FillRandom("gaus");
   double *x0 = h1->GetX();
   double *y0 = h1->GetY();
   double volume=0.0285*6.48*1.62;
   bool isPerModule = false;
   if(isPerModule) volume = 1.;
   double *y00 = new double[h1->GetN()];
   h1->SetTitle("Leakage current");
   h2->SetTitle("Leakage current");
   TGraph *h00 = (TGraph*)h1->Clone();
   for(int i=0;i<h1->GetN();i++){
     y00[i]=6.*y0[i];
   }
   h00 = new TGraph(h1->GetN(),x0,y00);
   double *x = h2->GetX();
   int Npoints=h2->GetN();
   double *y3 = new double[Npoints];
   for(int i = 0; i < Npoints; i++){
     y3[i]=h2->Eval(x[i])/h1->Eval(x[i]);
   }
   // Define the Canvas
   TCanvas *c = new TCanvas("c", "canvas", 800, 800);

   // Upper plot will be in pad1
   TPad *pad1 = new TPad("pad1", "pad1", 0, 0.3, 1, 1.0);
   pad1->SetBottomMargin(0); // Upper and lower plot are joined
   pad1->SetGridx();         // Vertical grid
   pad1->Draw();             // Draw the upper pad: pad1
   pad1->cd();               // pad1 becomes the current pad
  //  h2->Scale(5.);
  //  const int nMperROG = 6;
   TGraph *h2pmod = (TGraph*)h2->Clone();
   double *y2pmod = new double[h2->GetN()];
   for(int i=0;i<h2->GetN();i++){
     y2pmod[i]=1/((double)nMperROG)*h2->Eval(x[i])/volume;
   }
   h2pmod = new TGraph(h1->GetN(),x,y2pmod);
   TGraph *h1pmod = (TGraph*)h1->Clone();
   double *y1pmod = new double[h1->GetN()];
   for(int i=0;i<h1->GetN();i++){
     y1pmod[i]=1/((double)nMperROG)*y0[i]/volume;
   }
   h1pmod = new TGraph(h1->GetN(),x0,y1pmod);
   for(int i = 0; i < Npoints; i++){
     y3[i]=h2pmod->Eval(x[i])/h1pmod->Eval(x[i]);
   }
  //  TH1F *h0 = h2->GetHistogram();
  // TH1F *h0 = new TH1F("h0","h0",1000,1488326400,1546300799);
  

   TH1F *h0 = new TH1F("h0","h0",1000,1493463501,1544556700-1);
   h0->SetTitle("Phase-1 Forward Pixel - Leakage current vs day");

   TLegend *leg = new TLegend(0.15,0.6,0.45,0.75);
   h0->SetMaximum(hmax);
   h0->GetXaxis()->SetNdivisions(6, false);
  //  h0->GetXaxis()->SetRangeUser(1488326400.,1546300799.);
   h0->GetXaxis()->SetTimeFormat("%d/%m/%Y%F1970-01-01 00:00:00s0 GMT");
   if (isPerModule) h0->GetYaxis()->SetTitle("I_{leak} (@ 0#circC) [mA] per module");
   else h0->GetYaxis()->SetTitle("I_{leak} (@ 0#circC) [mA/cm^{3}]");
  //  h0->Scale(5.);
   h0->Draw();
   h0->GetYaxis()->ChangeLabel(1,0,0,0,0);
   h0->SetStats(0);          // No statistics on upper plot
   
   h1pmod->SetLineColor(kRed);
   h1pmod->SetLineWidth(2);
   h1pmod->Draw("L");               // Draw h1
   TH1F *h1pmod_histo = h1pmod->GetHistogram();
   h1pmod_histo->SetLineColor(kRed);
   h1pmod_histo->SetLineWidth(2);
   h1pmod_histo->SetMarkerColor(kRed);
  //  h1pmod_histo->Draw("L");               // Draw h1
   h00->SetLineColor(kRed);
   // h00->Draw("L");
   
   h2pmod->SetMarkerStyle(20);
   
   h2pmod->Draw("P");         // Draw h2 on top of h1
   TH1F *h2pmod_histo = h2pmod->GetHistogram();
   h2pmod_histo->SetMarkerStyle(20);
   h2pmod_histo->SetLineWidth(0);
  //  h2pmod_histo->Draw("P");         // Draw h2 on top of h1
   
  //  leg->SetFillStyle(0);
  //  leg->SetName("FPix, ring 1, disk 1");
   TString fpix_logo = "Forward Pixel Ring "+TString::Itoa(ring,10)+" Disk "+TString::Itoa(disk,10);
   TString dr = "Leakage current data";
   leg->AddEntry(h2pmod->GetHistogram(),dr);
   leg->AddEntry(h1pmod->GetHistogram(),"Simulation");
   leg->SetBorderSize(0);
   leg->SetBorderSize(0);
   leg->Draw("same");
   // Do not draw the Y axis label on the upper plot and redraw a small
   // axis instead, in order to avoid the first label (0) to be clipped.
   // h1->GetYaxis()->SetLabelSize(0.);
   cout << "!!!!!!!!!!!" << endl;
   TGaxis *axis = new TGaxis( -5, 20, -5, 220, 0, 10000, 510, "");
  //  axis->SetRangeUser(1488326400,1546300799);
   axis->SetLabelFont(43); // Absolute font size in pixel (precision 3)
   axis->SetLabelSize(15);
   axis->Draw();
   
   //--------------------------------------------------------------------------------------------
   TString cmsText     = "CMS";
    float cmsTextFont   = 61;  // default is helvetic-bold
    bool writeExtraText = true;
    TString extraText   = "Preliminary";
    TString extraText2   = "2020";
    TString extraText3   = "CMS FLUKA study v3.23.1.0";
    float extraTextFont = 52;  // default is helvetica-italics
    // text sizes and text offsets with respect to the top frame in unit of the top margin size
    float lumiTextSize     = 0.5;
    float lumiTextOffset   = 0.15;
    float cmsTextSize      = 0.5;
    float cmsTextOffset    = 0.1;  // only used in outOfFrame version
    float relPosX    = 0.045;
    float relPosY    = 0.035;
    float relExtraDY = 1.2;
    // ratio of "CMS" and extra text size
    float extraOverCmsTextSize  = 0.65;
    TString lumi_13TeV = "20.1 fb^{-1}";
    TString lumi_8TeV  = "19.7 fb^{-1}";
    TString lumi_7TeV  = "5.1 fb^{-1}";
    TString lumiText;
    // lumiText += lumi_8TeV;
    // lumiText += " (13 TeV)";
    // lumiText = "#sqrt{s} = 13 TeV ";
    float t = pad1->GetTopMargin();
    float b = pad1->GetBottomMargin();
    float r = pad1->GetRightMargin();
    float l = pad1->GetLeftMargin();
    // TLatex latex;
    // latex.SetNDC();
    // latex.SetTextAngle(0);
    // latex.SetTextColor(kBlack);
    // float extraTextSize = extraOverCmsTextSize*cmsTextSize;
    // latex.SetTextFont(42);
    // latex.SetTextAlign(31);
    // latex.SetTextSize(lumiTextSize*t);
    // // latex.DrawLatex(1-r,1-t+lumiTextOffset*t,lumiText);
    // latex.SetTextFont(cmsTextFont);
    // latex.SetTextAlign(11);
    // latex.SetTextSize(cmsTextSize*t);
    // latex.DrawLatex(l+0.03,1-t+lumiTextOffset*t-0.09,cmsText);
    // latex.SetTextFont(extraTextFont);
    // latex.SetTextSize(extraTextSize*t);
    // latex.DrawLatex(l+0.03, 1-t+lumiTextOffset*t-0.09-0.06, extraText);
     TLatex latex;
    latex.SetNDC();
    latex.SetTextAngle(0);
    latex.SetTextColor(kBlack);
    float extraTextSize = extraOverCmsTextSize*cmsTextSize*1.1;
    latex.SetTextFont(42);
    latex.SetTextAlign(31);
    latex.SetTextSize(lumiTextSize*t);
    latex.DrawLatex(1-r,1-t+lumiTextOffset*t,lumiText);
    latex.SetTextFont(cmsTextFont);
    latex.SetTextAlign(11);
    latex.SetTextSize(cmsTextSize*t);
    latex.DrawLatex(l+0.05,1-t+lumiTextOffset*t-0.09,cmsText);
    latex.SetTextFont(extraTextFont);
    latex.SetTextSize(extraTextSize*t);
    // latex.DrawLatex(l+0.05, 1-t+lumiTextOffset*t-0.09-0.06, extraText);
    latex.DrawLatex(l+0.05+0.08, 1-t+lumiTextOffset*t-0.09, extraText);
    latex.SetTextFont(extraTextFont-10);
    // latex.DrawLatex(l+0.17, 1-t+lumiTextOffset*t-0.09-0.06, extraText2);
    // latex.DrawLatex(l+0.17+0.08, 1-t+lumiTextOffset*t-0.09, extraText2);
    TString TrackSelctionText = fpix_logo;
    latex.SetTextFont(61);
    latex.SetTextSize(extraTextSize*t);
    latex.DrawLatex(l+0.45, 1-t+lumiTextOffset*t-0.12, TrackSelctionText);
    latex.SetTextFont(51);
    latex.SetTextSize(extraTextSize*t*0.85);
    latex.DrawLatex(l+0.55, 1-t+lumiTextOffset*t-0.05, extraText3);
    TString TrackSelctionText2 = "";
    if(disk==1) TrackSelctionText2 = "z = 32 cm";
    else if(disk==2) TrackSelctionText2 = "z = 40 cm";
    else if(disk==3) TrackSelctionText2 = "z = 50 cm";
    latex.SetTextFont(61);
    latex.SetTextSize(extraTextSize*t);
    latex.DrawLatex(l+0.45, 1-t+lumiTextOffset*t-0.09-0.07, TrackSelctionText2);
    //---------------------------------------------------------------------------------


   // lower plot will be in pad
   c->cd();          // Go back to the main canvas before defining pad2
   TPad *pad2 = new TPad("pad2", "pad2", 0, 0.05, 1, 0.3);
   pad2->SetTopMargin(0);
   pad2->SetBottomMargin(0.2);
   pad2->SetGridx(); // vertical grid
  //  pad2->SetGridy(); // vertical grid
   TF1 *f1 = new TF1("f1","[0]",0,1.6e9);
   f1->SetParameter(0,1);
   pad2->Draw();
   pad2->cd();       // pad2 becomes the current pad

   // Define the ratio plot
   TGraph *h3 = new TGraph(Npoints,x,y3);
   h3->GetXaxis()->SetRangeUser(1.4934635e+09+1,1.5445567e+09-1);
   h3->SetLineColor(kBlack);
   h3->SetMinimum(0.4);  // Define Y ..
   h3->SetMaximum(2.15); // .. range
   // h3->Sumw2();
   // h3->SetStats(0);      // No statistics on lower plot
   // h3->Divide(h2);
   h3->SetMarkerStyle(20);

   h3->Draw("AP");       // Draw the ratio plot
   f1->SetLineColor(kBlack);
   f1->SetLineWidth(1);
   f1->Draw("same");
   // h1 settings
   h1->SetLineColor(kBlue+1);
   h1->SetLineWidth(2);

   // Y axis h1 plot settings
   h1->GetYaxis()->SetTitleSize(20);
   h1->GetYaxis()->SetTitleFont(43);
   h1->GetYaxis()->SetTitleOffset(1.55);

   // h2 settings
   h2->SetLineColor(kRed);
   h2->SetLineWidth(2);

   // Ratio plot (h3) settings
   h3->SetTitle(""); // Remove the ratio title

   // Y axis ratio plot settings
   h3->GetYaxis()->SetTitle("Data/Simulation ");
   h3->GetYaxis()->SetNdivisions(505);
   h3->GetYaxis()->SetTitleSize(20);
   h3->GetYaxis()->SetTitleFont(43);
   h3->GetYaxis()->SetTitleOffset(1.55);
   h3->GetYaxis()->SetLabelFont(43); // Absolute font size in pixel (precision 3)
   h3->GetYaxis()->SetLabelSize(19);

   // X axis ratio plot settings
   h3->GetXaxis()->SetTitleSize(20);
   h3->GetXaxis()->SetTitleFont(43);
   h3->GetXaxis()->SetTitleOffset(4.);
   h3->GetXaxis()->SetLabelFont(43); // Absolute font size in pixel (precision 3)
   h3->GetXaxis()->SetLabelSize(19);
   h3->GetXaxis()->ChangeLabel(1,0,0,0,0);
   h3->GetXaxis()->SetNdivisions(6,false);
   h3->GetXaxis()->SetTitle("Date");
  //  "%d/%m/%Y%F1970-01-01 00:00:00s0 GMT"
  //  cout << h3->GetXaxis()->GetTimeFormat() << endl;
   h3->GetXaxis()->SetTimeFormat("%d/%m/%Y%F1970-01-01 00:00:00s0 GMT");
   c->SaveAs(out_name);
   c->SaveAs(out_name2);
}


void ratio_graph(TString file_name, int nMperROG, int ring, int disk, double hmax, TString out_name, TString out_name2) {
  TFile *_file0 = TFile::Open(file_name);
  TGraph *h1 = (TGraph*)_file0->Get("I_leak_per_module");
  TGraph *h2 = (TGraph*)_file0->Get("I_leak_per_module_data");
  TCanvas *cccc = new TCanvas("cccc", "canvasccc", 800, 800);
  h2->SetMarkerStyle(20);
  h2->Draw("AP");
  ratioplot(_file0, h1, h2, nMperROG, ring, disk, hmax, out_name, out_name2);
}