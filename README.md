# Pixel monitoring tools

## Installation
To simplify the environment setting, we advise to install the code on `lxplus` or anywhere else where you have access to `cvmfs` (see Section `Setup environment`)
```bash
git clone git@github.com:fleble/PixelMonitoring.git
source setup.sh
```

<br></br>
## Setup environment
After every new login, if you do not use `brilcalc`, do:
```bash
source setenv.sh
```
This can be unset only with a new login. 

For using `brilcalc`, do:
```bash
source brilwsenv.sh
```
You can unset this setup by doing:
```bash
source unset_brilwsenv.sh
```
This will only work if you have access to `cvmfs`.

<br></br>
## Overview and decription of all scripts

For all scripts, learn about its usage with `python script.py -h`.

| Script      | Description |
| :---------- | :---------- |
| `getFills.py`                 | Reads start and stop timestamps using CMSOMS API for desired fills and writes to an output file (default `fills_info/fills.csv`). |
| `getIntegratedLuminosity.py`  | Reads instantaneous and integrated lumi using `brilcalc` and writes it to an output file (default `fills_info/integrated_luminosity_per_fill.csv`). |
| `getCurrentsFromDB.py`        | Reads the currents from the `cms_omds_adg` Oracle database and write one file per fill in `currents/from_database/`. |
| `getCurrents.py`              | Reads currents from database and writes digital, analog, analog per ROC and HV per ROC currents (default in `currents/processed/`). |
| `getPLCAirTemperatures.py`    | Reads temperatures from the `cms_omds_adg` Oracle database and writes one file per fill (default in `temperatures/`). |
| `getFluenceField.py`          | Reads ASCII FLUKA file, creates txt files with equivalent information (default in `fluence/txt_files/`) and creates a ROOT file with the 2D fluence field histogram `F(r, z)` for different particles (default `fluence/fluence_field_phase1_6500GeV.root`). Units are stored in a txt file (default `fluence/fluence_field_phase1_6500GeV_units.txt`). |
| `getFluence.py`               | Reads all particles fluence field from ROOT file for given coordinates `r` and `z` and outputs the fluence. |
| `fitFluenceField.py`          | Fit the all particles fluence field from output of `getFluenceField.py`. Command line examples can be found in `getFluenceField.sh`. |
| `plotCurrents.py`             | Plot digital, analog, analog per ROC and leakage current from output of `getCurrents.py`. Default output: `plots/currents` |
| `plotTemperatures.py`          | Plot temperatures from output of `getPLCAirTemperatures.py` |

List of scripts that were not checked:
* check_2dfit_fluka.py
* CMS_lumi.py
* fit_phi_vs_z.py
* fluka_l1.py
* getPLC_Tpipe.py
* getPLC_Tpipe_bpix.py
* mapping_geom.py
* Module.py
* modules_geom.py
* prof_datetime.py
* ratio_graph.C
* rogchannel_modules.py
* rogring_pc.py
* run3_profile.py
* run_ileak.sh
* run_Run3.py
* SiPixelDetsUpdatedAfterFlippedChange.py
* SiPixelDetsUpdatedAfterFlippedChange_BPIX.py 
* temperature.py
* time_cold_counter.py
* write_pos_fl.py

