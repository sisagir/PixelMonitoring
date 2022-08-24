# Pixel monitoring tools

### Installation
```bash
git clone git@github.com:fleble/PixelMonitoring.git
source setup.sh
```

### Setup
After every new login, do:
```bash
source cmsenv.sh
```

### List of fills with stable beams
```bash
python getFill_TotalLumi.py
```

Will produce an output file with the list of all fills with stable beams: `FillInfo_TotLumi.txt`
We can use this file to exclude some fill ranges.

### Get currents

First get currents from Timber with:
```bash
python getCurrentsFromDB.py --BarrelOrEndCap Barrel/EndCap
```
You will be asked for the first fill number and for the last fill number of the range you want to examine. In this way a txt file collecting information on analog, digital and bias currents will be produced by accessing the DB.

Then produce separate files for Analog/Digital and HV averaged currents.
```bash
python getCurrents.py --BarrelOrEndCap Barrel/EndCap
```

### Plot leakage current
Run the analysis and produce plots and fits with:
```bash
python plotLeakageCurrent.py --BarrelOrEndCap Barrel/EndCap
```
