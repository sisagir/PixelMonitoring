#include <iostream>
#include <sstream>
#include <ctime>
#include <time.h>
#include "TStyle.h"
#include "TH1D.h"
#include "TString.h"
#include "TCanvas.h"
#include "TTree.h"
#include "TMath.h"
#include "TROOT.h"
#include "TFile.h"
#include "TSpline.h"
#include "TNamed.h"
#include "TLegend.h"
#include "TLatex.h"
#include <map>

// from FillInfo_TotLumi.txt (Annapaola) //TString day_at_fill[] = {};
// 1013 begindate(format 2010-03-31) begintime(format 19:03:10.001864) enddate endtime TotLumi: 0.4947
// TString infile_HV_ByLayer[] = {"",""};

//Set Options:
Int_t Phase0or1 = 1;
TString good_sectors[] = {"BmO", "BmI", "BpO", "BpI"}; //in phase-0, BpI was replaced in LS1
TString broken_sectors[] = {"PixelBarrel_BpI_S3_LAY3", "PixelBarrel_BpI_S3_LAY4", "PixelBarrel_BpI_S5_LAY4"};
//

const Int_t periods3500GeV = 736;
const Int_t periods4000GeV = 257;
const Int_t periodsLS1 = 898;
const Int_t periods6500GeV_phase0 = 720;
const Int_t periods6500GeV_phase1 = 555;
const Double_t rocVol = 0.81*0.81*0.0285; //Annapaola

Int_t num_layers;
Int_t totalperiods;
Color_t colors[] = {kRed-3, kAzure+1, kGreen+1, kOrange+1};
Int_t totallumi;


Int_t rdn(Int_t y, Int_t m, Int_t d) {/* Rata Die day one is 0001-01-01 */
  if (m < 3)
    y--, m += 12;
  return 365*y + y/4 - y/100 + y/400 + (153*m - 457)/5 + d - 306;
}


Int_t getDayNumber(Char_t * fillstartdate) { //Count days starting on 30/03/2010
  std::cout << "fillstartdate in function " << fillstartdate << std::endl;
  std::ostringstream formatstartdate;
  formatstartdate << fillstartdate;
  struct tm tm_fillstartdate;// = {0,0,0,31,02,110};

  strptime(formatstartdate.str().c_str(), "%Y-%m-%d", &tm_fillstartdate);

  Int_t year = 1900+tm_fillstartdate.tm_year; //tm structs count from 1900
  Int_t month = tm_fillstartdate.tm_mon+1; //+1: month AFTER january
  Int_t day = tm_fillstartdate.tm_mday;
  std::cout << "year " << year << " month " << month << " day " << day << std::endl;
  //Rata die algorithm

  Int_t deltadays = 0;
  if (Phase0or1 == 0) {
    deltadays = rdn(year, month, day) - rdn(2010, 03, 30);
  } else {
    deltadays = rdn(year, month, day) - rdn(2017, 05, 23);
  }
  std::cout << "Day number " << deltadays << std::endl;
  return deltadays;
}

void Fill_ileak_per_module_histos() {

  if (Phase0or1 == 0){
  std::cout << " Phase 0 " << std::endl;
  num_layers = 3;
  totalperiods = periods3500GeV+periods4000GeV+periodsLS1+periods6500GeV_phase0;
  totallumi = 100; //fb-1
 } else {
  std::cout << " Phase 1 " << std::endl;
  num_layers = 4;
  totalperiods = periods6500GeV_phase1;
  totallumi = 200; //fb-1
 }


 Double_t ileak_array[num_layers];
 Int_t entries_per_layer[num_layers];


  //Book histograms

  TH1D * h_ileak_per_cm3_vs_days_L1 = new TH1D("h_ileak_percm3_vs_days_L1", "Leakage current per cm3, L1", totalperiods, 0.5, totalperiods + 0.5); //days
  TH1D * h_ileak_per_cm3_vs_days_L2 = new TH1D("h_ileak_percm3_vs_days_L2", "Leakage current per cm3, L2", totalperiods, 0.5, totalperiods + 0.5); //days
  TH1D * h_ileak_per_cm3_vs_days_L3 = new TH1D("h_ileak_percm3_vs_days_L3", "Leakage current per cm3, L3", totalperiods, 0.5, totalperiods + 0.5); //days
  TH1D * h_ileak_per_cm3_vs_days_L4 = new TH1D("h_ileak_percm3_vs_days_L4", "Leakage current per cm3, L4", totalperiods, 0.5, totalperiods + 0.5); //days
  TH1D * h_ileak_per_cm3_vs_days[] = {h_ileak_per_cm3_vs_days_L1, h_ileak_per_cm3_vs_days_L2, h_ileak_per_cm3_vs_days_L3, h_ileak_per_cm3_vs_days_L4};

  TH1D * h_ileak_per_cm3_vs_lumi_L1 = new TH1D("h_ileak_percm3_vs_lumi_L1", "Leakage current per cm3, L1", totallumi, 0., totallumi);
  TH1D * h_ileak_per_cm3_vs_lumi_L2 = new TH1D("h_ileak_percm3_vs_lumi_L2", "Leakage current per cm3, L2", totallumi, 0., totallumi);
  TH1D * h_ileak_per_cm3_vs_lumi_L3 = new TH1D("h_ileak_percm3_vs_lumi_L3", "Leakage current per cm3, L3", totallumi, 0., totallumi);
  TH1D * h_ileak_per_cm3_vs_lumi_L4 = new TH1D("h_ileak_percm3_vs_lumi_L4", "Leakage current per cm3, L4", totallumi, 0., totallumi);
  TH1D * h_ileak_per_cm3_vs_lumi[] = {h_ileak_per_cm3_vs_lumi_L1, h_ileak_per_cm3_vs_lumi_L2, h_ileak_per_cm3_vs_lumi_L3, h_ileak_per_cm3_vs_lumi_L4};

  TH1D * h_ileak_per_cm3_vs_sec_L1 = new TH1D("h_ileak_percm3_vs_sec_L1", "Leakage current per cm3, L1", totalperiods, 0.5, totalperiods*24.*60.*60.+0.5); //s
  TH1D * h_ileak_per_cm3_vs_sec_L2 = new TH1D("h_ileak_percm3_vs_sec_L2", "Leakage current per cm3, L2", totalperiods, 0.5, totalperiods*24.*60.*60.+0.5); //s
  TH1D * h_ileak_per_cm3_vs_sec_L3 = new TH1D("h_ileak_percm3_vs_sec_L3", "Leakage current per cm3, L3", totalperiods, 0.5, totalperiods*24.*60.*60.+0.5); //s
  TH1D * h_ileak_per_cm3_vs_sec_L4 = new TH1D("h_ileak_percm3_vs_sec_L4", "Leakage current per cm3, L4", totalperiods, 0.5, totalperiods*24.*60.*60.+0.5); //s
  TH1D * h_ileak_per_cm3_vs_sec[] = {h_ileak_per_cm3_vs_sec_L1, h_ileak_per_cm3_vs_sec_L2, h_ileak_per_cm3_vs_sec_L3, h_ileak_per_cm3_vs_sec_L4};

  TH1D * h_ileak_per_mod_vs_days_L1 = new TH1D("h_ileak_per_mod_vs_days_L1", "Leakage current per module, L1", totalperiods, 0.5, totalperiods+0.5);
  TH1D * h_ileak_per_mod_vs_days_L2 = new TH1D("h_ileak_per_mod_vs_days_L2", "Leakage current per module, L2", totalperiods, 0.5, totalperiods+0.5);
  TH1D * h_ileak_per_mod_vs_days_L3 = new TH1D("h_ileak_per_mod_vs_days_L3", "Leakage current per module, L3", totalperiods, 0.5, totalperiods+0.5);
  TH1D * h_ileak_per_mod_vs_days_L4 = new TH1D("h_ileak_per_mod_vs_days_L4", "Leakage current per module, L4", totalperiods, 0.5, totalperiods+0.5);
  TH1D * h_ileak_per_mod_vs_days[] = {h_ileak_per_mod_vs_days_L1, h_ileak_per_mod_vs_days_L2, h_ileak_per_mod_vs_days_L3, h_ileak_per_mod_vs_days_L4};

  TH1D * h_ileak_per_mod_vs_sec_L1 = new TH1D("h_ileak_per_mod_vs_sec_L1", "Leakage current per module, L1", totalperiods, 0.5, totalperiods*24.*60.*60. + 0.5);
  TH1D * h_ileak_per_mod_vs_sec_L2 = new TH1D("h_ileak_per_mod_vs_sec_L2", "Leakage current per module, L2", totalperiods, 0.5, totalperiods*24.*60.*60. + 0.5);
  TH1D * h_ileak_per_mod_vs_sec_L3 = new TH1D("h_ileak_per_mod_vs_sec_L3", "Leakage current per module, L3", totalperiods, 0.5, totalperiods*24.*60.*60. + 0.5);
  TH1D * h_ileak_per_mod_vs_sec_L4 = new TH1D("h_ileak_per_mod_vs_sec_L4", "Leakage current per module, L4", totalperiods, 0.5, totalperiods*24.*60.*60. + 0.5);
  TH1D * h_ileak_per_mod_vs_sec[] = {h_ileak_per_mod_vs_sec_L1, h_ileak_per_mod_vs_sec_L2, h_ileak_per_mod_vs_sec_L3, h_ileak_per_mod_vs_sec_L4};

  TH1D * h_ileak_per_mod_vs_lumi_L1 = new TH1D("h_ileak_per_mod_vs_lumi_L1", "Leakage current per module, L1", totallumi, 0., totallumi);
  TH1D * h_ileak_per_mod_vs_lumi_L2 = new TH1D("h_ileak_per_mod_vs_lumi_L2", "Leakage current per module, L2", totallumi, 0., totallumi);
  TH1D * h_ileak_per_mod_vs_lumi_L3 = new TH1D("h_ileak_per_mod_vs_lumi_L3", "Leakage current per module, L3", totallumi, 0., totallumi);
  TH1D * h_ileak_per_mod_vs_lumi_L4 = new TH1D("h_ileak_per_mod_vs_lumi_L4", "Leakage current per module, L4", totallumi, 0., totallumi);
  TH1D * h_ileak_per_mod_vs_lumi[] = {h_ileak_per_mod_vs_lumi_L1, h_ileak_per_mod_vs_lumi_L2, h_ileak_per_mod_vs_lumi_L3, h_ileak_per_mod_vs_lumi_L4};

  //histograms for each sector: ileak per module (no averaging)
  std::map<TString, TH1D*> m_histos_per_module_no_avg;


  // Input file with fill info
  Int_t fillnum;
  Char_t startdate[20];
  Double_t totlumi; //nb-1  Char_t startdate[30];
  TTree* fillinfo = new TTree("fillinfo", "fillinfo");
  //fillinfo->ReadFile("/afs/cern.ch/user/j/juhunt/public/PixelMonitoring/FillInfo_TotLumi.txt", "Fill/I:Startdate/C:Starttime/C:Enddate/C:Endtime/C:Label/C:TotLumi/D");
  fillinfo->ReadFile("/afs/cern.ch/user/f/ffeindt/private/PixelMonitoring/FillInfo_TotLumi.txt", "Fill/I:Startdate/C:Starttime/C:Enddate/C:Endtime/C:Label/C:TotLumi/D");
  fillinfo->SetBranchAddress("Fill", &fillnum);
  fillinfo->SetBranchAddress("Startdate", &startdate);
  fillinfo->SetBranchAddress("TotLumi", &totlumi); //nb-1
  Int_t num_Fills = (Int_t)fillinfo->GetEntries();

  // Loop over files with data of one fill each
  // format: .txt PixelBarrel_BpO_S7_LAY1 etc \t value

  Int_t loopstart, loopend;
  if (Phase0or1 == 0) {
    loopstart = 0;
    loopend = 1045; // 1054th fillentry is last fill in ph0: 5698_Barrel.txt
  } else {
    loopstart = 1046; // first fillentry in ph1
    loopend = num_Fills;
  }



  for (Int_t fillentry = loopstart; fillentry < loopend; fillentry++) {
    fillinfo->GetEntry(fillentry);
    std::cout << "Fillentry " << fillentry << " fillnum " << fillnum << std::endl;

    Int_t deltadays = getDayNumber(startdate); //days in Phase-0 (since 30/03/2010) or days in Phase-1 (since 23/05/2017)
    Char_t sector[30];
    Float_t ileakroc;
    TTree* onefilldata = new TTree("onefilldata", "onefilldata");
    //TString filename = "/afs/cern.ch/user/j/juhunt/public/PixelMonitoring/txt/" + TString::Itoa(fillnum,10) + "_Barrel_HV_ByLayer.txt";
    TString filename = "/afs/cern.ch/user/f/ffeindt/private/PixelMonitoring/txt/" + TString::Itoa(fillnum,10) + "_Barrel_HV_ByLayer.txt";
    std::cout << "filename " << filename << std::endl;
    onefilldata->ReadFile(filename, "SectorLabel/C:IleakROC/F");
    onefilldata->SetBranchAddress("SectorLabel", &sector);
    onefilldata->SetBranchAddress("IleakROC", &ileakroc);
    Int_t num_lines = (Int_t)onefilldata->GetEntries();

    //
    //Collect Ileak per ROC for one given fill (entry) in map[sector]
    //And fill histogram bin (day at fillentry) for each sector with Ileak per ROC*16= Ileak per module.
    //
    std::map<TString,Double_t> m_ileak;


    for(Long64_t entry = 0; entry < onefilldata->GetEntries(); ++entry) {
      onefilldata->GetEntry(entry);
      if( m_ileak.find(sector) != m_ileak.end() ) {
	std::cerr << "Entry for sector " << sector << " already exists!" << std::endl;
	continue;
      }

      m_ileak[sector] = ileakroc;


      //fill unavg histograms:
      if (m_histos_per_module_no_avg.find(sector) == m_histos_per_module_no_avg.end() ) {
	//if sector entry does not yet exist in histogram map (first loop): initialise histo
	m_histos_per_module_no_avg[sector] = new TH1D (sector, sector,  totalperiods, 0.5, totalperiods*24.*60.*60. + 0.5);

      }
      m_histos_per_module_no_avg[sector]->SetBinContent(deltadays, 16 * ileakroc);


    }

    // For each layer:
    // Sum and then average Ileak over all sectors
    //

    for (Int_t layer = 0; layer < num_layers; layer++) {
      ileak_array[layer] = 0;
      entries_per_layer[layer] = 0;

      for (Int_t sec = 1; sec <= 8; sec++) {
	// Double_t mod_in_sec = Get_modinsec(i, layer); // is already per ROC in annapaolas files *_Barrel_HV_ByLayer.txt
	// TString good_sectors[] = {"BmI", "BmO", "BpO"}; //BpI has new modules from LS1 onwards
	//	for (int j = 0; j < num_layers; j++) {
	//	}
	for (Int_t BpmOI = 0; BpmOI < sizeof(good_sectors)/sizeof(*good_sectors); BpmOI++) {
	  TString ConstructLabel = "PixelBarrel_"+good_sectors[BpmOI]+"_S"+TString::Itoa(sec,10)+"_LAY"+TString::Itoa(layer+1,10);
	  if ( (ConstructLabel != broken_sectors[0]) and (ConstructLabel != broken_sectors[1]) and (ConstructLabel != broken_sectors[2]) ) {

	  if ( m_ileak.find(ConstructLabel) == m_ileak.end() ) {
	    std::cout << "Entry for sector " << ConstructLabel << " not found" << std::endl;
	    continue;
	  }

	  //	  std::cout << "ConstructLabel " << ConstructLabel << " " << m_ileak[ConstructLabel] << std::endl;
	  Double_t myileak = m_ileak[ConstructLabel];

	  //collect for avg histograms:

	  ileak_array[layer] += myileak; //leakage current per ROC sum
	  entries_per_layer[layer] += 1;
	  std::cout << ConstructLabel << " " << myileak << "\t sum: " << ileak_array[layer] << "\t entries per layer " << entries_per_layer[layer] << std::endl;
	  } else {
	    std::cout << "Skipping broken sector " << ConstructLabel << std::endl;
	  }
	}
      }

      if (entries_per_layer[layer] == 0) {
	std::cout << "No data in Layer " << layer << " on the " << startdate << std::endl;
      } else {
	ileak_array[layer] /= entries_per_layer[layer]; // avg over all sectors and "good" quadrants: leakage current per ROC in each layer

	std::cout << "Done with sector loop, setting histo contents " << std::endl;
	std::cout << "total lumi " << totlumi << std::endl;
	std::cout << "ileak_array[layer] " << ileak_array[layer] << std::endl;
	//vs lumi
	h_ileak_per_mod_vs_lumi[layer]->SetBinContent( h_ileak_per_mod_vs_lumi[layer]->FindBin(totlumi/1000000), 16 * ileak_array[layer]); //2x8 ROCs per module
	h_ileak_per_cm3_vs_lumi[layer]->SetBinContent( h_ileak_per_mod_vs_lumi[layer]->FindBin(totlumi/1000000), ileak_array[layer]*rocVol);
	//vs days
	h_ileak_per_mod_vs_days[layer]->SetBinContent( deltadays, 16 * ileak_array[layer]); //2x8 ROCs per module
	h_ileak_per_cm3_vs_days[layer]->SetBinContent( deltadays, ileak_array[layer]*rocVol);
	//vs sec
	h_ileak_per_mod_vs_sec[layer]->SetBinContent( h_ileak_per_mod_vs_sec[layer]->FindBin(deltadays*24*60*60), 16 * ileak_array[layer]); //2x8 ROCs per module
	h_ileak_per_cm3_vs_sec[layer]->SetBinContent( h_ileak_per_mod_vs_sec[layer]->FindBin(deltadays*24*60*60), ileak_array[layer]*rocVol);
      }
    }
  }

  // Plot
  std::cout << "Plotting... " << std::endl;
  TFile * outfile = new TFile();
  if (Phase0or1 == 0) {
    outfile = TFile::Open("/afs/cern.ch/user/f/ffeindt/private/cmspixRDmon/input/Annapaola-ileak/ileakdata_ph0.root", "RECREATE");
  } else {
    outfile = TFile::Open("/afs/cern.ch/user/f/ffeindt/private/cmspixRDmon/input/Annapaola-ileak/ileakdata_ph1.root", "RECREATE");
  }
  outfile->mkdir("no_avg_over_sectors_per_module");
  outfile->mkdir("per_module");
  outfile->mkdir("per_cm3");
  outfile->GetDirectory("no_avg_over_sectors_per_module");
  outfile->GetDirectory("per_module");
  outfile->GetDirectory("per_cm3");




  outfile->cd("per_module");
  TString daystitle, secondstitle;

  if (Phase0or1 == 0) {
    secondstitle = Form("Seconds since 30/03/2010");
    daystitle = Form("Days since 30/03/2010");
  } else {
    secondstitle = Form("Seconds since 23/05/2017");
    daystitle = Form("Days since 23/05/2017");
  }

  for (Int_t lay = 0; lay < num_layers; lay++) {
    h_ileak_per_mod_vs_lumi[lay]->GetYaxis()->SetTitle("Leakage current per module in #muA");
    h_ileak_per_mod_vs_lumi[lay]->GetXaxis()->SetTitle("Luminosity /fb^{-1}");
    h_ileak_per_mod_vs_lumi[lay]->SetMarkerStyle(kCircle);
    h_ileak_per_mod_vs_lumi[lay]->SetMarkerSize(2);
    h_ileak_per_mod_vs_lumi[lay]->SetMarkerColor(colors[lay]);
    std::cout << "Writing... " << std::endl;
    h_ileak_per_mod_vs_lumi[lay]->Write();

    h_ileak_per_mod_vs_days[lay]->GetYaxis()->SetTitle("Leakage current per module in #muA");
    h_ileak_per_mod_vs_days[lay]->GetXaxis()->SetTitle(daystitle);
    h_ileak_per_mod_vs_days[lay]->SetMarkerStyle(kCircle);
    h_ileak_per_mod_vs_days[lay]->SetMarkerSize(2);
    h_ileak_per_mod_vs_days[lay]->SetMarkerColor(colors[lay]);
    std::cout << "Writing... " << std::endl;
    h_ileak_per_mod_vs_days[lay]->Write();

    h_ileak_per_mod_vs_sec[lay]->GetYaxis()->SetTitle("Leakage current per module in #muA");
    h_ileak_per_mod_vs_sec[lay]->GetXaxis()->SetTitle(secondstitle);
    h_ileak_per_mod_vs_sec[lay]->SetMarkerStyle(kCircle);
    h_ileak_per_mod_vs_sec[lay]->SetMarkerSize(2);
    h_ileak_per_mod_vs_sec[lay]->SetMarkerColor(colors[lay]);
    std::cout << "Writing... " << std::endl;
    h_ileak_per_mod_vs_sec[lay]->Write();
  }

  outfile->cd("per_cm3");
  for (Int_t lay = 0; lay < num_layers; lay++) {
    h_ileak_per_cm3_vs_lumi[lay]->GetYaxis()->SetTitle("Leakage current per cm^{3} in #muA");
    h_ileak_per_cm3_vs_lumi[lay]->GetXaxis()->SetTitle("Luminosity /fb^{-1}");
    h_ileak_per_cm3_vs_lumi[lay]->SetMarkerStyle(kCircle);
    h_ileak_per_cm3_vs_lumi[lay]->SetMarkerSize(2);
    h_ileak_per_cm3_vs_lumi[lay]->SetMarkerColor(colors[lay]);
    std::cout << "Writing... " << std::endl;
    h_ileak_per_cm3_vs_lumi[lay]->Write();

    h_ileak_per_cm3_vs_days[lay]->GetYaxis()->SetTitle("Leakage current per cm^{3} in #muA");
    h_ileak_per_cm3_vs_days[lay]->GetXaxis()->SetTitle(daystitle);
    h_ileak_per_cm3_vs_days[lay]->SetMarkerStyle(kCircle);
    h_ileak_per_cm3_vs_days[lay]->SetMarkerSize(2);
    h_ileak_per_cm3_vs_days[lay]->SetMarkerColor(colors[lay]);
    std::cout << "Writing... " << std::endl;
    h_ileak_per_cm3_vs_days[lay]->Write();

    h_ileak_per_cm3_vs_sec[lay]->GetYaxis()->SetTitle("Leakage current per cm^{3} in #muA");
    h_ileak_per_cm3_vs_sec[lay]->GetXaxis()->SetTitle(secondstitle);
    h_ileak_per_cm3_vs_sec[lay]->SetMarkerStyle(kCircle);
    h_ileak_per_cm3_vs_sec[lay]->SetMarkerSize(2);
    h_ileak_per_cm3_vs_sec[lay]->SetMarkerColor(colors[lay]);
    std::cout << "Writing... " << std::endl;
    h_ileak_per_cm3_vs_sec[lay]->Write();

  }

  //iterator for map and initialise it to the beginning of map
  std::map<TString, TH1D*>::iterator it = m_histos_per_module_no_avg.begin();
  //access key from iterator: it->first
  //access value from iterator: it->second

  outfile->cd("no_avg_over_sectors_per_module");
  while(it != m_histos_per_module_no_avg.end()) {
    it->second->GetYaxis()->SetTitle("Leakage current per module in #muA");
    it->second->GetXaxis()->SetTitle(secondstitle);
    it->second->SetMarkerStyle(kCircle);
    it->second->SetMarkerSize(2);
    std::cout << "Writing unaveraged histo... " << it->first << std::endl;
    it->second->Write();
    it++;
  }


  outfile->Close();
  std::cout << "__________________________" << std::endl;

}



/*
Double_t Get_modinsec(Int_t i, Int_t layer) { //ith entry in sensornames_array
  Double_t  mod_in_sec; //divide by 8x2 to get number of sensors
  Double_t FM = 1; //Full module: 8x2 array of ROCS bonded to Sensor
  // ROCS have 52 colums x 80 rows, serving 100x150 \mu m^2 pixel cells
  Double_t HM = 0.5; //Half-module: 8x1 array of ROCS bonded to Sensor
  Double_t FL = 4*FM; // modules per full ladder
  Double_t HL = 4*HM; // modules per half-ladder
  switch (layer) {
  case 1:
    switch (i) { //sector B(m,p)O 1...8 B(m,p)I 8...1 sind symmetrisch
    case 1: mod_in_sec = HL + FL;      break;
    case 2: mod_in_sec = FL;      break;
    case 3: mod_in_sec = FL;      break;
    case 4: mod_in_sec = FL;      break;
    case 5: mod_in_sec = FL;      break;
    case 6: mod_in_sec = FL;      break;
    case 7: mod_in_sec = FL;      break;
    case 8: mod_in_sec = FL + HL;      break;
    default: std::cout << "Sector number does not exist" << std::endl; break;
    }
    break;
  case 2:
    switch (i) { //sector B(m,p)O 1...8 B(m,p)I 8...1
    case 1: mod_in_sec = HL + FL;      break;
    case 2: mod_in_sec = 2 * FL;      break;
    case 3: mod_in_sec = 2 * FL;      break;
    case 4: mod_in_sec = 2 * FL;      break;
    case 5: mod_in_sec = 2 * FL;      break;
    case 6: mod_in_sec = 2 * FL;      break;
    case 7: mod_in_sec = 2 * FL;      break;
    case 8: mod_in_sec = FL + HL;      break;
    default: std::cout << "Sector number does not exist" << std::endl; break;
    }
    break;
  case 3:
    switch (i) { //sector B(m,p)O 1...8 B(m,p)I 8...1
    case 1: mod_in_sec = HL + 2 * FL;      break;
    case 2: mod_in_sec = 3 * FL;      break;
    case 3: mod_in_sec = 3 * FL;      break;
    case 4: mod_in_sec = 2 * FL;      break;
    case 5: mod_in_sec = 2 * FL;      break;
    case 6: mod_in_sec = 3 * FL;      break;
    case 7: mod_in_sec = 3 * FL;      break;
    case 8: mod_in_sec = HL + 2 * FL;      break;
    default: std::cout << "Sector number does not exist" << std::endl; break;
    }
    break;
  default:
    std::cout << "no valid layer passed to function" << std::endl;
    break;
  }

  return mod_in_sec;
}
*/




#ifndef __CINT__
int main() {
  Fill_ileak_per_module_histos();
  return 0;
}
#endif
