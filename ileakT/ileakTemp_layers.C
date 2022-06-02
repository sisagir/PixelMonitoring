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

using namespace std;

// from FillInfo_TotLumi.txt (Annapaola) //TString day_at_fill[] = {};
// 1013 begindate(format 2010-03-31) begintime(format 19:03:10.001864) enddate endtime TotLumi: 0.4947
// TString infile_HV_ByLayer[] = {"",""};
// Finn geting the temperatures matching the leakage current measurements

//Set Options:
Int_t Phase0or1 = 1;
TString good_sectors[] = {"BmO", "BmI", "BpO", "BpI"}; //in phase-0, BpI was replaced in LS1
TString broken_sectors[] = {"PixelBarrel_BpI_S3_LAY3", "PixelBarrel_BpI_S3_LAY4", "PixelBarrel_BpI_S5_LAY4"};
// ignore broken sectors for now
//TString broken_Tempsectors[] = {"PixelBarrel_BpI_Sector_3_POH_3",
//				"PixelBarrel_BpI_Sector_3_POH_4",
//				"PixelBarrel_BpI_Sector_5_POH_4"};
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

// correct the swaped sensor aliases
TString correctAlias( TString sensorName );

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
  }
  else {
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
  }
  else {
    std::cout << " Phase 1 " << std::endl;
    num_layers = 4;
    totalperiods = periods6500GeV_phase1;
    totallumi = 200; //fb-1
  }
  const double granularity = 1.; //in days
  // totalperiods *=4;
  Double_t ileak_array[num_layers];
  Int_t entries_per_layer[num_layers];
  const double hours_interval = 24*granularity;
  //Book histograms
  TH1D * h_ileak_per_mod_vs_sec_L1 = new TH1D("h_ileak_per_mod_vs_sec_L1", "Leakage current per module, L1", totalperiods, 0.5, totalperiods*hours_interval*60.*60. + 0.5);
  TH1D * h_ileak_per_mod_vs_sec_L2 = new TH1D("h_ileak_per_mod_vs_sec_L2", "Leakage current per module, L2", totalperiods, 0.5, totalperiods*hours_interval*60.*60. + 0.5);
  TH1D * h_ileak_per_mod_vs_sec_L3 = new TH1D("h_ileak_per_mod_vs_sec_L3", "Leakage current per module, L3", totalperiods, 0.5, totalperiods*hours_interval*60.*60. + 0.5);
  TH1D * h_ileak_per_mod_vs_sec_L4 = new TH1D("h_ileak_per_mod_vs_sec_L4", "Leakage current per module, L4", totalperiods, 0.5, totalperiods*hours_interval*60.*60. + 0.5);
  TH1D * h_ileak_per_mod_vs_sec[] = {h_ileak_per_mod_vs_sec_L1, h_ileak_per_mod_vs_sec_L2, h_ileak_per_mod_vs_sec_L3, h_ileak_per_mod_vs_sec_L4};

  TH1D * h_ileak_mtchTmp_vs_sec_L1 = new TH1D("h_ileak_mtchTmp_vs_sec_L1", "Temperature matching ileak measurement, L1", totalperiods, 0.5, totalperiods*hours_interval*60.*60. + 0.5);
  TH1D * h_ileak_mtchTmp_vs_sec_L2 = new TH1D("h_ileak_mtchTmp_vs_sec_L2", "Temperature matching ileak measurement, L2", totalperiods, 0.5, totalperiods*hours_interval*60.*60. + 0.5);
  TH1D * h_ileak_mtchTmp_vs_sec_L3 = new TH1D("h_ileak_mtchTmp_vs_sec_L3", "Temperature matching ileak measurement, L3", totalperiods, 0.5, totalperiods*hours_interval*60.*60. + 0.5);
  TH1D * h_ileak_mtchTmp_vs_sec_L4 = new TH1D("h_ileak_mtchTmp_vs_sec_L4", "Temperature matching ileak measurement, L4", totalperiods, 0.5, totalperiods*hours_interval*60.*60. + 0.5);
  TH1D * h_ileak_mtchTmp_vs_sec[] = {h_ileak_mtchTmp_vs_sec_L1, h_ileak_mtchTmp_vs_sec_L2, h_ileak_mtchTmp_vs_sec_L3, h_ileak_mtchTmp_vs_sec_L4};

  //histograms for each sector: ileak per module (no averaging)
  std::map<TString, TH1D*> m_histos_per_module_no_avg;


  // Input file with fill info
  Int_t fillnum;
  Char_t startdate[20];
  Double_t totlumi; //nb-1  Char_t startdate[30];
  TTree* fillinfo = new TTree("fillinfo", "fillinfo");
  //fillinfo->ReadFile("/afs/cern.ch/user/j/juhunt/public/PixelMonitoring/FillInfo_TotLumi.txt", "Fill/I:Startdate/C:Starttime/C:Enddate/C:Endtime/C:Label/C:TotLumi/D");
  TString filepath="/afs/cern.ch/user/d/dbrzhech/ServiceWork/RadDamage/pixelMonitor/CMSSW_9_4_0_pre1/src/PixelMonitoring/";//PixelMonitoring/FillInfo_TotLumi.txt";
  fillinfo->ReadFile((filepath+(TString)"FillInfo_TotLumi.txt").Data(), "Fill/I:Startdate/C:Starttime/C:Enddate/C:Endtime/C:Label/C:TotLumi/D");
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

    // This is filling the leakage current TTree
    Int_t deltadays = getDayNumber(startdate); //days in Phase-0 (since 30/03/2010) or days in Phase-1 (since 23/05/2017)
    Char_t sector[30];
    Float_t ileakroc;
    TTree* onefilldata = new TTree("onefilldata", "onefilldata");
    //TString filename = "/afs/cern.ch/user/j/juhunt/public/PixelMonitoring/txt/" + TString::Itoa(fillnum,10) + "_Barrel_HV_ByLayer.txt";
    TString filename = filepath+(TString)"txt/" + TString::Itoa(fillnum,10) + (TString)"_Barrel_HV_ByLayer.txt";
    std::cout << "filename " << filename << std::endl;
    onefilldata->ReadFile(filename.Data(), "SectorLabel/C:IleakROC/F");
    onefilldata->SetBranchAddress("SectorLabel", &sector);
    onefilldata->SetBranchAddress("IleakROC", &ileakroc);
    Int_t num_lines = (Int_t)onefilldata->GetEntries();


    // Fill the matching temperature TTree
    Char_t sensorName[30];
    Float_t ileakTmp;
    Char_t dateTmp[20];
    Char_t timeTmp[20];
    TTree* onefilltemp = new TTree("onefilltemp", "onefilltemp");
    //TString filenameT = "/afs/cern.ch/user/f/ffeindt/private/PixelMonitoring/txt2/" + TString::Itoa(fillnum,10) + "_Tpipe.txt";
    TString filenameT = filepath+(TString)"txt/" + TString::Itoa(fillnum,10) + "_Tpipe.txt";
    std::cout << "filenameT " << filenameT << std::endl;
    onefilltemp->ReadFile(filenameT.Data(), "sensorNameT/C:ileakTmpT/F:dateTmpT/C:timeTmpT/C");
    onefilltemp->SetBranchAddress("sensorNameT", &sensorName);
    onefilltemp->SetBranchAddress("ileakTmpT", &ileakTmp);
    onefilltemp->SetBranchAddress("dateTmpT", &dateTmp);
    onefilltemp->SetBranchAddress("timeTmpT", &timeTmp);
    Int_t num_temps = (Int_t)onefilltemp->GetEntries();

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
        m_histos_per_module_no_avg[sector] = new TH1D (sector, sector,  totalperiods, 0.5, totalperiods*hours_interval*60.*60. + 0.5);

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
        	}
          else{
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

        //vs sec 2x8 ROCs per module
        h_ileak_per_mod_vs_sec[layer]->SetBinContent( h_ileak_per_mod_vs_sec[layer]->FindBin(deltadays*hours_interval*60*60), 16 * ileak_array[layer]);
      }
    }

    // #finn
    // variables to store the average per layer
    Double_t temp_array[num_layers];
    Int_t temps_pLay[num_layers];
    for( Int_t i_layers = 0; i_layers < num_layers; i_layers++){
      temp_array[i_layers] = 0;
      temps_pLay[i_layers] = 0;
    }

    // now averaging temperatures
    for(Long64_t entry = 0; entry < onefilltemp->GetEntries(); ++entry) {
      onefilltemp->GetEntry(entry); // now it should be in the variables

      cout << "    sensorName " << sensorName << endl;
      cout << "    ileakTmp   " << ileakTmp   << endl;
      cout << "    dateTmp    " << dateTmp    << endl;
      cout << "    timeTmp    " << timeTmp    << endl;
      cout << "    layer      " << sensorName[20]-'0' << endl;

      Int_t deltadaystemp = getDayNumber(dateTmp);
      cout << " deltadaystemp " << deltadaystemp << endl;

      TString changename = sensorName;
      changename = correctAlias( changename );

      Int_t thatLayer = ((Int_t)sensorName[20]-'0') - 1;
      Int_t thisLayer = ((Int_t)changename(20)-'0') - 1;

      temp_array[thisLayer] += ileakTmp;
      temps_pLay[thisLayer] += 1;

      cout << " layer " << thisLayer << " " << thatLayer << " sum " << temp_array[thisLayer] << " number " << temps_pLay[thisLayer] << endl;

    }// end averaging temperatures

    // fill temperatures
    for( Int_t i_layers = 0; i_layers < num_layers; i_layers++){

      if( 0 == temps_pLay[ i_layers ] )
        continue;                                                          // content (si melting point)

      h_ileak_mtchTmp_vs_sec[i_layers]->SetBinContent(
        h_ileak_per_mod_vs_sec[ i_layers ]->FindBin( deltadays*hours_interval*60*60 ), // bin
        temp_array[ i_layers ] / temps_pLay[ i_layers ] );                 // content

      cout << "---------------------------------------------------------------------------" << endl;
      cout << "bin  " << h_ileak_per_mod_vs_sec[ i_layers ]->FindBin( deltadays*hours_interval*60*60 ) << endl
           << "cont " << temp_array[ i_layers ] / temps_pLay[ i_layers ] << endl;

    }
  }

  // Plot
  std::cout << "Plotting... " << std::endl;
  TFile * outfile = new TFile();
  if (Phase0or1 == 0) {
    outfile = TFile::Open("ileakTemp_ph0.root", "RECREATE");
  } else {
    outfile = TFile::Open("ileakTemp_ph1.root", "RECREATE");
  }
  outfile->mkdir("per_module");
  outfile->GetDirectory("per_module");

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

    h_ileak_per_mod_vs_sec[lay]->GetYaxis()->SetTitle("Leakage current per module in #muA");
    h_ileak_per_mod_vs_sec[lay]->GetXaxis()->SetTitle(secondstitle);
    h_ileak_per_mod_vs_sec[lay]->SetMarkerStyle(kCircle);
    h_ileak_per_mod_vs_sec[lay]->SetMarkerSize(2);
    h_ileak_per_mod_vs_sec[lay]->SetMarkerColor(colors[lay]);
    std::cout << "Writing... " << std::endl;
    h_ileak_per_mod_vs_sec[lay]->Write();
  }

  //outfile->mkdir("temperature");
  //outfile->GetDirectory("temperature");
  //outfile->cd("temperature");

  for (Int_t lay = 0; lay < num_layers; lay++) {

    h_ileak_mtchTmp_vs_sec[lay]->GetYaxis()->SetTitle("Layer-wise Temperature average");
    h_ileak_mtchTmp_vs_sec[lay]->GetXaxis()->SetTitle(secondstitle);
    h_ileak_mtchTmp_vs_sec[lay]->SetMarkerStyle(kCircle);
    h_ileak_mtchTmp_vs_sec[lay]->SetMarkerSize(2);
    h_ileak_mtchTmp_vs_sec[lay]->SetMarkerColor(colors[lay]);
    std::cout << "Writing... " << std::endl;
    h_ileak_mtchTmp_vs_sec[lay]->Write();
  }
  fillinfo->Write();
  outfile->Close();
  std::cout << "__________________________" << std::endl;

}

#ifndef __CINT__
int main() {
  Fill_ileak_per_module_histos();
  return 0;
}
#endif

// correct the swaped sensor aliases
TString correctAlias( TString sensorName ){

  cout << "pre correction" << sensorName << endl;

  // get substrings
  TString part1 = sensorName(  0, 16 ); // PixelBarrel_BmO_ -- part 16
  TString part2 = sensorName( 16, 10 ); // 4I_L1D2MN        -- part

  bool changed = 0; // change only once

  // change the wrong substring
  if( part2 == "4I_L1D2MN" && !changed ) { cout << "made change " << endl; part2 = "4R_L1D2MN"; changed = 1; }
  if( part2 == "4M_L1D2MN" && !changed ) { cout << "made change " << endl; part2 = "4I_L1D2MN"; changed = 1; }
  if( part2 == "4R_L1D2MN" && !changed ) { cout << "made change " << endl; part2 = "4M_L1D2MN"; changed = 1; }
  if( part2 == "3I_L2D1MN" && !changed ) { cout << "made change " << endl; part2 = "1I_L4D2MN"; changed = 1; }
  if( part2 == "3M_L2D1MN" && !changed ) { cout << "made change " << endl; part2 = "1M_L4D2MN"; changed = 1; }
  if( part2 == "3R_L2D1MN" && !changed ) { cout << "made change " << endl; part2 = "1R_L4D2MN"; changed = 1; }
  if( part2 == "4I_L2D2PN" && !changed ) { cout << "made change " << endl; part2 = "6R_L4D3PN"; changed = 1; }
  if( part2 == "4M_L2D2PN" && !changed ) { cout << "made change " << endl; part2 = "6M_L4D3PN"; changed = 1; }
  if( part2 == "4R_L2D2PN" && !changed ) { cout << "made change " << endl; part2 = "6I_L4D3PN"; changed = 1; }
  if( part2 == "2I_L3D1MN" && !changed ) { cout << "made change " << endl; part2 = "2R_L3D1MN"; changed = 1; }
  if( part2 == "2R_L3D1MN" && !changed ) { cout << "made change " << endl; part2 = "2I_L3D1MN"; changed = 1; }
  if( part2 == "5I_L3D3MN" && !changed ) { cout << "made change " << endl; part2 = "5R_L3D3MN"; changed = 1; }
  if( part2 == "5R_L3D3MN" && !changed ) { cout << "made change " << endl; part2 = "5I_L3D3MN"; changed = 1; }
  if( part2 == "1I_L4D2MN" && !changed ) { cout << "made change " << endl; part2 = "3I_L2D1MN"; changed = 1; }
  if( part2 == "1M_L4D2MN" && !changed ) { cout << "made change " << endl; part2 = "3M_L2D1MN"; changed = 1; }
  if( part2 == "1R_L4D2MN" && !changed ) { cout << "made change " << endl; part2 = "3R_L2D1MN"; changed = 1; }
  if( part2 == "6M_L4D3PN" && !changed ) { cout << "made change " << endl; part2 = "4M_L2D2PN"; changed = 1; }
  if( part2 == "6R_L4D3PN" && !changed ) { cout << "made change " << endl; part2 = "4R_L2D2PN"; changed = 1; }
  if( part2 == "6I_L4D4MN" && !changed ) { cout << "made change " << endl; part2 = "6R_L4D4MN"; changed = 1; }
  if( part2 == "6R_L4D4MN" && !changed ) { cout << "made change " << endl; part2 = "6I_L4D4MN"; changed = 1; }
  if( part2 == "3M_L1D1MF" && !changed ) { cout << "made change " << endl; part2 = "3I_L1D1MF"; changed = 1; }
  if( part2 == "3I_L1D1MF" && !changed ) { cout << "made change " << endl; part2 = "3M_L1D1MF"; changed = 1; }
  if( part2 == "3I_L2D1PF" && !changed ) { cout << "made change " << endl; part2 = "1I_L4D2PF"; changed = 1; }
  if( part2 == "3M_L2D1PF" && !changed ) { cout << "made change " << endl; part2 = "1M_L4D2PF"; changed = 1; }
  if( part2 == "3R_L2D1PF" && !changed ) { cout << "made change " << endl; part2 = "1R_L4D2PF"; changed = 1; }
  if( part2 == "2I_L3D1PF" && !changed ) { cout << "made change " << endl; part2 = "2M_L3D1PF"; changed = 1; }
  if( part2 == "2M_L3D1PF" && !changed ) { cout << "made change " << endl; part2 = "2I_L3D1PF"; changed = 1; }
  if( part2 == "2R_L3D2MF" && !changed ) { cout << "made change " << endl; part2 = "2I_L3D2MF"; changed = 1; }
  if( part2 == "2I_L3D2MF" && !changed ) { cout << "made change " << endl; part2 = "2R_L3D2MF"; changed = 1; }
  if( part2 == "1I_L4D2PF" && !changed ) { cout << "made change " << endl; part2 = "3I_L2D1PF"; changed = 1; }
  if( part2 == "1M_L4D2PF" && !changed ) { cout << "made change " << endl; part2 = "3M_L2D1PF"; changed = 1; }
  if( part2 == "1R_L4D2PF" && !changed ) { cout << "made change " << endl; part2 = "3R_L2D1PF"; changed = 1; }
  if( part2 == "6M_L4D3MF" && !changed ) { cout << "made change " << endl; part2 = "4M_L2D2MF"; changed = 1; }
  if( part2 == "6R_L4D3MF" && !changed ) { cout << "made change " << endl; part2 = "4R_L2D2MF"; changed = 1; }
  if( part2 == "4I_L2D2MF" && !changed ) { cout << "made change " << endl; part2 = "6I_L4D3MF"; changed = 1; }
  if( part2 == "4M_L2D2MF" && !changed ) { cout << "made change " << endl; part2 = "6M_L4D3MF"; changed = 1; }
  if( part2 == "4R_L2D2MF" && !changed ) { cout << "made change " << endl; part2 = "6R_L4D3MF"; changed = 1; }
  if( part2 == "6I_L4D4PF" && !changed ) { cout << "made change " << endl; part2 = "6R_L4D4PF"; changed = 1; }
  if( part2 == "6R_L4D4PF" && !changed ) { cout << "made change " << endl; part2 = "6I_L4D4PF"; changed = 1; }

  // rebuild sensor name
  sensorName = part1 + part2;

  cout << "post correction" << sensorName << endl;

  return sensorName;
}
