#include <map>
#include <vector>
#include <iostream>
#include <TFile.h>
#include <TTree.h>
#include "TMath.h"
#include <stdio.h>
#include <TCanvas.h>
#include <TH1F.h>
#include <TF1.h>
#include <TROOT.h>
#include "TStyle.h"
#include <iostream>
#include <fstream>
#include <numeric>
#include <string.h>

#define tecringoffset_   5
#define subdetoffset_   25
#define layerstartbit_  14
#define tecringmask_   0x7
#define subdetmask_    0x7
#define layermask_     0x7

////initialisation of constants   
const Double_t B = 3280.;
const Double_t T0 = 273.1;
const Double_t T25 = 298.1;
const Double_t Kdiv = 0.5;
const Double_t tsGain = 8.9;
const Double_t i20 = 0.02;
const Double_t i10 = 0.01;
const Double_t Rt0 = 10000;
const Double_t R0  = 0.681;

const char* fname_params = "DCU_conv_params.txt";

// get index of subdetector 1=TIB, 2=TID, 3=TOB, 4=TEC from detid
Int_t get_detector(int detid){
  Int_t subdet;
  subdet = ((detid >> subdetoffset_) & subdetmask_);
  if(subdet==3) return 1; //TIB
  if(subdet==4) return 2; // TID
  if(subdet==5) return 3;//TOB
  if(subdet==6) return 4; //TEC
  std::cerr << " no subdetector found for detid: " << detid << std::endl;
  return -1;
}

Int_t get_nth(int detid){

  Int_t det_index = get_detector(detid);
  if(det_index==1 || det_index==2) return 1;
  else if(det_index == 3 || det_index==4) return 2;
  else return -1;
  
}

void convertDCU(char* fname_raw_value){

  char ologfilename[80];
  strcpy(ologfilename,"conv_");
  strcat(ologfilename,fname_raw_value);

  std::ofstream log;
  log.open(ologfilename);
  
  Int_t detid0;
  Int_t TSIL_raw;
  Int_t IL_raw;

  TTree* Tree0 = new TTree("tree_values","Tree_DCU_raw");
  Tree0->ReadFile(fname_raw_value,"DETID/I:TSIL_RAW/I:IL_RAW/I");
  Tree0->SetBranchAddress("DETID", &detid0);
  Tree0->SetBranchAddress("TSIL_RAW", &TSIL_raw);
  Tree0->SetBranchAddress("IL_RAW", &IL_raw);
  Long64_t t0entries = Tree0->GetEntries();



  Int_t detid_params;
  Float_t ADC_gain;
  Float_t ADC_offset;

  TTree* Tree_params = new TTree("DCUconversionparams","DCUconvparams");
  Tree_params->ReadFile(fname_params,"DETID/I:ADC_GAIN/F:ADC_OFFSET/F");
  Tree_params->SetBranchAddress("DETID", &detid_params);
  Tree_params->SetBranchAddress("ADC_GAIN", &ADC_gain);
  Tree_params->SetBranchAddress("ADC_OFFSET", &ADC_offset);
  Long64_t tparamentries = Tree_params->GetEntries();


  Int_t nth;
  Double_t Rt12;
  Double_t TSil_temp_back_calc;
  Double_t Ileak;

  for(Long64_t i=0;i<t0entries;i++){
    Tree0->GetEntry(i);
    for(Long64_t j=0; j<tparamentries;j++){
      Tree_params->GetEntry(j);
      if(detid0==detid_params){
	nth = get_nth(detid0);
	Rt12 = nth*(TSIL_raw-ADC_offset)/(i20*ADC_gain);
	TSil_temp_back_calc = 1/(TMath::Log(Rt12/Rt0)/B+1/T25)-T0;
	Ileak = (IL_raw-ADC_offset)/(R0*ADC_gain);
	log << detid0 << " " << TSil_temp_back_calc << " " << Ileak << std::endl;
	break;
      }
    }
  } 
  log.close();

}
