#include <iostream>
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


// input: periods

//const Int_t periods = 736; //3500 GeV
//const Int_t periods = 257; //4000 GeV
//const Int_t periods = 898; //LS1
//const Int_t periods = 720; //6500 GeV phase0
//const Int_t periods = 238; //~196 value entries; //6500 GeV phase1: May 23 2017 - Jan 16 2018: 238 days
//const Int_t periods = 385; // 6500 GeV phase1: May 23 2017 - Jun 12 2018:
//const Int_t periods = 465; // 6500 GeV phase1: May 23 2017 - Aug 31 2018:
const Int_t periods = 601; // 6500 GeV phase1: May 23 2017 - Jan 15 2019:

//broken: "PixelBarrel_BmO_6I_L4D3MF.txt", "PixelBarrel_BpI_6I_L4D3PN.txt"
//outlier: "PixelBarrel_BmO_6M_L4D3MF.txt"
TString sensorfilenames[] = {"PixelBarrel_BmI_1I_L4D2MN.txt", "PixelBarrel_BmI_1M_L4D2MN.txt", "PixelBarrel_BmI_1R_L4D2MN.txt", "PixelBarrel_BmI_2I_L3D1MN.txt", "PixelBarrel_BmI_2R_L3D1MN.txt", "PixelBarrel_BmI_3I_L2D1MN.txt", "PixelBarrel_BmI_3M_L2D1MN.txt", "PixelBarrel_BmI_3R_L2D1MN.txt", "PixelBarrel_BmI_4I_L1D2MN.txt", "PixelBarrel_BmI_4M_L1D2MN.txt", "PixelBarrel_BmI_4R_L1D2MN.txt", "PixelBarrel_BmI_5I_L3D3MN.txt", "PixelBarrel_BmI_5M_L3D3MN.txt", "PixelBarrel_BmI_5R_L3D3MN.txt", "PixelBarrel_BmI_6I_L4D4MN.txt", "PixelBarrel_BmI_6M_L4D4MN.txt", "PixelBarrel_BmI_6R_L4D4MN.txt", "PixelBarrel_BmO_1I_L4D1MF.txt", "PixelBarrel_BmO_1M_L4D1MF.txt", "PixelBarrel_BmO_1R_L4D1MF.txt", "PixelBarrel_BmO_2I_L3D2MF.txt", "PixelBarrel_BmO_2M_L3D2MF.txt", "PixelBarrel_BmO_2R_L3D2MF.txt", "PixelBarrel_BmO_3I_L1D1MF.txt", "PixelBarrel_BmO_3M_L1D1MF.txt", "PixelBarrel_BmO_3R_L1D1MF.txt", "PixelBarrel_BmO_4I_L2D2MF.txt", "PixelBarrel_BmO_4M_L2D2MF.txt", "PixelBarrel_BmO_4R_L2D2MF.txt", "PixelBarrel_BmO_5I_L3D4MF.txt", "PixelBarrel_BmO_5M_L3D4MF.txt", "PixelBarrel_BmO_5R_L3D4MF.txt", "PixelBarrel_BmO_6R_L4D3MF.txt", "PixelBarrel_BpI_1I_L4D1PN.txt", "PixelBarrel_BpI_1M_L4D1PN.txt", "PixelBarrel_BpI_1R_L4D1PN.txt", "PixelBarrel_BpI_2I_L3D2PN.txt", "PixelBarrel_BpI_2M_L3D2PN.txt", "PixelBarrel_BpI_2R_L3D2PN.txt", "PixelBarrel_BpI_3I_L1D1PN.txt", "PixelBarrel_BpI_3R_L1D1PN.txt", "PixelBarrel_BpI_4I_L2D2PN.txt", "PixelBarrel_BpI_4M_L2D2PN.txt", "PixelBarrel_BpI_4R_L2D2PN.txt", "PixelBarrel_BpI_5M_L3D4PN.txt", "PixelBarrel_BpI_5R_L3D4PN.txt", "PixelBarrel_BpI_6M_L4D3PN.txt", "PixelBarrel_BpI_6R_L4D3PN.txt", "PixelBarrel_BpO_1I_L4D2PF.txt","PixelBarrel_BpO_1M_L4D2PF.txt","PixelBarrel_BpO_1R_L4D2PF.txt","PixelBarrel_BpO_2I_L3D1PF.txt","PixelBarrel_BpO_2M_L3D1PF.txt","PixelBarrel_BpO_2R_L3D1PF.txt","PixelBarrel_BpO_3I_L2D1PF.txt","PixelBarrel_BpO_3M_L2D1PF.txt","PixelBarrel_BpO_3R_L2D1PF.txt","PixelBarrel_BpO_4I_L1D2PF.txt","PixelBarrel_BpO_4R_L1D2PF.txt","PixelBarrel_BpO_5I_L3D3PF.txt","PixelBarrel_BpO_5M_L3D3PF.txt","PixelBarrel_BpO_5R_L3D3PF.txt","PixelBarrel_BpO_6I_L4D4PF.txt","PixelBarrel_BpO_6M_L4D4PF.txt","PixelBarrel_BpO_6R_L4D4PF.txt"};

const Int_t num_sensors = sizeof(sensorfilenames)/sizeof(sensorfilenames[0]);

Double_t temp;
Double_t timestamp;
Double_t temp_array[num_sensors]; // temporary storage for all temperature measurements of a certain day i
Double_t lasttimestamp;
Int_t count_validentries[num_sensors];
Double_t lasttimestamp_array[num_sensors];
Int_t numentries;

Double_t meanvalue(Double_t * first, Double_t * last) {
  Double_t sum = 0;
  Double_t sumw = 0;
  while ( first != last )
    {
      if (*first < 70) {
	sum += *first;
	sumw += 1;
      }
      first++;
    }
  if (!(sumw == 0) and (sumw > 4)) {
    std::cout << "MEAN = " << sum/sumw << std::endl;
    return sum/sumw;
  }
  else {
    std::cout << "sumw " << sumw << ", sum " << sum << std::endl;
    std::cout << "MEAN = " << 1000.0 << std::endl;
    return 1000.0;
  }
}

Double_t medianvalue( Double_t * x) {
  Double_t temp;
  int i, j;
  // the following two loops sort the array x in ascending order
  for(i = 0; i < num_sensors-1; i++) {
    for(j = i + 1; j < num_sensors; j++) {
      if(x[j] < x[i]) {
	// swap elements
	temp = x[i];
	x[i] = x[j];
	x[j] = temp;
      }
    }
  }

  if(num_sensors%2 == 0) {  // if even number of elements, mean of the two middle elements
    return((x[num_sensors/2] + x[num_sensors/2 - 1]) / 2.0);
  } else {
    // else element in the middle
    return x[num_sensors/2];
  }
}


void handle_temperature_input() {

  TFile * temperatures_6500_phase1 = new TFile("temperatures_6500Gev_phase1.root", "RECREATE");

  gROOT->SetStyle("Plain");
  gStyle->SetOptStat(0);
  TCanvas * c1 = new TCanvas("c1", "c1", 200, 10, 700, 500);

  TH1D * h_T_C_mean = new TH1D("h_T_mean", "Mean Temperature of PLC tube sensors", periods, 0.5, periods + 0.5);
  TH1D * h_T_C_median = new TH1D("h_T_median", "Median Temperature of PLC tube sensors", periods, 0.5, periods + 0.5);

  TTree * treesensor = new TTree("treesensor","treesensor");
  Double_t lastvalue[num_sensors];

  Int_t sensorentries[num_sensors];

  for (int i = 0; i < num_sensors; i++) {
    // readfile
    sensorentries[i] = treesensor->GetEntries(); //Entries in treesensor before first falue of sensor i
    TString inputDir = "";
    treesensor->ReadFile(inputDir+sensorfilenames[i],"Time/D:Temperature/D",'\t');
    count_validentries[i] = 0; //Initialise

    lasttimestamp_array[i] = 1495533600000; // Adapt - timestamp for first day
  }
  treesensor->SetBranchAddress("Temperature",&temp);
  treesensor->SetBranchAddress("Time",&timestamp);
  numentries =  treesensor->GetEntries();


  for (int day = 0; day < periods; day ++) {
    std::cout << "DAY " << day << std::endl;

    for (int i = 0; i < num_sensors; i++) {
      //      std::cout << " sensor nr " << i << " - " ;
      //      std::cout << "Entry nr " << sensorentries[i] + count_validentries[i];
      treesensor->GetEntry(sensorentries[i]+count_validentries[i]);
      //      std::cout << "timestamp " << timestamp << " lasttimestamp_array[i] "<< lasttimestamp_array[i] << " 36*60*60*1000 " << 36*60*60*1000 << std::endl;
      if ( timestamp < lasttimestamp_array[i] + 36*60*60*1000 ) {//if the entry is not more than 36 hours later ("next day")

	//	if (temp < 50) {
	  //  std::cout << "if temp<50 " << std::endl;
	  lastvalue[i] = temp; //accept new value
	  lasttimestamp_array[i] = timestamp;
	  count_validentries[i] += 1;
	  //	}
      } else {
	std::cout << "else " << std::endl;
	lasttimestamp_array[i] += 24*60*60*1000; //if no valid entry, step forward to next day
      }
      temp_array[i] = lastvalue[i];
      std::cout << i << ": " << temp_array[i] << ", ";
    }
    std::cout << std::endl <<std::endl;
    h_T_C_mean->SetBinContent(day, meanvalue(&(temp_array[0]), &(temp_array[num_sensors])));
    h_T_C_median->SetBinContent(day, medianvalue(&temp_array[0]));

  }

  c1->cd();
  h_T_C_mean->Write();
  h_T_C_median->Write();

  // temperatures_3500->Close();
  // temperatures_4000->Close();
  //  temperatures_LS1->Close();
  // temperatures_6500->Close();
   temperatures_6500_phase1->Close();
}

#ifndef __CINT__
int main() {
  handle_temperature_input();
  return 0;
}
#endif
