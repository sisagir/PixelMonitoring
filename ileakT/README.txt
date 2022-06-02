Temperature measured together with the leakage current 
in this way the leakage current simulation can be scaled
to the temperature at which measurements were taken

It uses a script similar to the one geting the leakage
current measurements. you need to go all the way...

probably you will have to moddify some path names.
in case something does not work search for
"feindtf" or "ffeindt"

  LEAKAGE CURRENT
  - on lxplus
  - get the git from annapaola:
    ssh://git@gitlab.cern.ch:7999/decosa/PixelMonitoring.git
  - change getCurrents.py; 
    "txt/" -> ""
  - change getFill_TotalLumi.py line 5:
    from numberOfROCs import numberOfRocsBarrelPhase1
    
  - Tue Apr 16 -> need CMSSW now. Thanks to Feng:
    $ mkdir pixelMonitor
    $ cd pixelMonitor
    $ export SCRAM_ARCH=slc6_amd64_gcc481
    $ cmsrel CMSSW_9_4_0_pre1
    $ cd CMSSW_9_4_0_pre1/src
    $ cmsenv 
    $ mv PixelMonitoring CMSSW_9_4_0_pre1/src/. and run from there
    
  - now RUN -- instructions on https://gitlab.cern.ch/decosa/PixelMonitoring
    - python getFill_TotalLumi.py
    - python getCurrentsFromDB.py --BarrelOrEndCap Barrel 
      first fill is 5698
      remember last fill number -> 7492
      - maybe i can do this just from last fill number (7334 till newest [which i get from previous script])
    - python getCurrents.py --BarrelOrEndCap Barrel
    
    # this gets you the temperatures
    - python getPLC_Tpipe.py 
    
    # this removes some bad fills but is a quick and dirty solution
    # read and use with caution in a directory where you copied the data
    - run rm_badfills.sh in txt to remove bad fills
    
    # these you find in this directory
      -> in case of broken sektor look here
      -> set correct input/ output path
      - make ileak and temp
      - run leak_layers and ileakTemp_layers
    - output ileakdata_ph1.root and ileakTemp_ph1.root
    - ileakTemp-ph1 is the druid you are looking for