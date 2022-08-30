import os
import argparse
from pathlib import Path
from decimal import Decimal

import ROOT
import uproot

from utils import generalUtils as gUtl


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_ascii_file_name",
        help="Input ASCII FLUKA file",
        required=False,
        default="fluence/cmsv3_23_1_0_usrbin_40_ascii",
        # cmsv3_20_1_0_usrbin_40_ascii  phase0 6500 GeV
        # cmsv3_23_1_0_usrbin_40_ascii  phase1 6500 GeV
    )
    parser.add_argument(
        "-o", "--root_file_output_directory",
        help="Output ROOT file directory",
        required=False,
        default="fluence",
    )
    parser.add_argument(
        "-ot", "--txt_files_output_directory",
        help="Txt files output directory",
        required=False,
        default="fluence/txt_files",
    )
    parser.add_argument(
        "-s", "--suffix",
        help="Txt files suffix",
        required=False,
        default="phase1_6500GeV",
    )
 
    return parser.parse_args()


def per_section(datafile):
    section = []
    for line in datafile:
        if (line.strip() == str(1)):
            tmp = section
            section = []
            if tmp: # don't count first empty one
                yield tmp
        else:
            section.append(line)
    yield section # last one


def get_binning():
    rbins=200
    rmin=0. #cm
    rmax=20. #cm
    rbinwidth=0.1 #cm
    zbins=700
    zmin=-350. #cm
    zmax=350. #cm
    zbinwidth=1. #cm
    entriesPerLine=10.
    linesPerZPos = rbins/entriesPerLine

    return rbins, rmin, rmax, rbinwidth, zbins, zmin, zmax, zbinwidth, linesPerZPos


def get_error_txt_file_name(txt_file_name):
    return txt_file_name.replace(".txt", "_error.txt")


def write_txt_files(input_ascii_file_name, txt_files):

    error_txt_files = [get_error_txt_file_name(x) for x in txt_files]

    # Delete old files
    gUtl.remove_files(txt_files + error_txt_files)

    rbins, rmin, rmax, rbinwidth, zbins, zmin, zmax, zbinwidth, linesPerZPos = get_binning()

    # correspond to section index si = 1, 3, 5, 7, 9, 11. Want: neutrons, protons, pions = 3, 7, 11
    with open(input_ascii_file_name, "r") as ascii_file:
        for si, section in enumerate(per_section(ascii_file)):
            rpos=rmin+rbinwidth/2 # mid-bin = 0.0+halfbinwidth
            zpos=zmin+zbinwidth/2 # mid-bin = 0.0+halfbinwidth
            with (open(txt_files[int(si)], "a") as txt_file,
                  open(error_txt_files[int(si)], "a") as error_txt_file):
                txt_file.write('z = ' + str(  round(zpos,2)  ) + '\n');
                for i, line in enumerate(section[8:]):
                    if i < zbins*linesPerZPos:
                        if i%linesPerZPos == 0 and i!=0:
                            zpos += zbinwidth
                            rpos=rmin+rbinwidth/2 # mid-bin = 0.0+halfbinwidth
                            txt_file.write('z = ' + str(  round(zpos,2)  ) + '\n');
                        for j, fluenceentry in enumerate(line.split()):
                            txt_file.write(str(  round(rpos,2)  ) + '\t' + str(fluenceentry) + '\n');
                            rpos+=rbinwidth;
                    elif i >= zbins*linesPerZPos + 3:
                        if (i-3)%linesPerZPos == 0:
                            if i == zbins*linesPerZPos + 3:
                                rpos=rmin+rbinwidth/2 # mid-bin = 0.0+halfbinwidth
                                zpos=zmin+zbinwidth/2 # mid-bin = 0.0+halfbinwidth
                            else:
                                zpos += zbinwidth
                                rpos=rmin+rbinwidth/2 # mid-bin = 0.0+halfbinwidth
                        for j, errentry in enumerate(line.split()):
                            binx = int((rpos-rmin)/rbinwidth)
                            biny = int((zpos-zmin)/zbinwidth)
                            error = float(errentry)*1e-2
                            error_txt_file.write('%d %d %.4E\n' %(binx, biny, error))
                            rpos+=rbinwidth;
            rpos=rmin+rbinwidth/2 # mid-bin = 0.0+halfbinwidth

    for file_name in txt_files + error_txt_files:
        print("%s has been written." % file_name)


def sum_txt_files(input_txt_file_names, output_txt_file_name):

    # Delete old files
    gUtl.remove_files(output_txt_file_name)

    input_txt_files_rows = []
    for file_name in input_txt_file_names:
        file = open(file_name)
        input_txt_files_rows.append(file.read().splitlines())

    with open(output_txt_file_name, "a") as file:
        for rows in zip(*input_txt_files_rows):
            if "=" in rows[0]:
                text = rows[0] + "\n"
            else:
                sum_ = sum(map(lambda x: Decimal(x.split()[1]), rows))
                text = rows[0].split()[0] + "\t" + "%.4E\n" % sum_
            file.write(text)

    print("%s has been written." % output_txt_file_name)


def get_th2(txt_file_name, histogram_base_name):

    error_txt_file_name = get_error_txt_file_name(txt_file_name)
    rbins, rmin, rmax, rbinwidth, zbins, zmin, zmax, zbinwidth, linesPerZPos = get_binning()

    histogram_name = "fluence_" + histogram_base_name
    name = "Fluence(r, z) " + histogram_base_name
    th2 = ROOT.TH2F(histogram_name, name, rbins, rmin, rmax, zbins, zmin, zmax)

    with open(txt_file_name, "r") as file:
        for row in file.read().splitlines():
            if "=" in row:
                zpos = float(row.split("=")[1])
            else:
                rpos, fluence = map(lambda x: float(x), row.split())
                th2.Fill(rpos, zpos, fluence)

    if os.path.isfile(error_txt_file_name):
        with open(error_txt_file_name, "r") as file:
            for row in file.read().splitlines():
                x = row.split()
                binx, biny, error = int(x[0]), int(x[1]), float(x[2])
                th2.SetBinError(binx, biny, th2.GetBinContent(binx, biny) * error)

    return th2


def main(args):

    Path(args.root_file_output_directory).mkdir(parents=True, exist_ok=True)
    Path(args.txt_files_output_directory).mkdir(parents=True, exist_ok=True)

    suffix = "_" + args.suffix if args.suffix else ""

    output_root_file_name = args.root_file_output_directory + "/fluence_field" + suffix + ".root"

    # In order of sections in ascii file:
    txt_files_base_names = [
        "allpart",
        "neut",
        "aneut",
        "prot",
        "aprot",
        "pions",
    ]
    txt_file_names = [args.txt_files_output_directory + "/" + x +  suffix + ".txt" for x in txt_files_base_names]
    input_charged_txt_file_names = txt_file_names[3:]
    input_neutral_txt_file_names = txt_file_names[1:3]
    output_charged_txt_file_name = args.txt_files_output_directory + "/charged" + suffix + ".txt"
    output_neutral_txt_file_name = args.txt_files_output_directory + "/neutral" + suffix + ".txt"

    all_txt_file_names = txt_file_names + [output_charged_txt_file_name, output_neutral_txt_file_name]

    #txt_files = ["symtestzminus3/symtestzminus3_allpart_6500GeV_phase1.txt", "symtestzminus3/symtestzminus3_neut_6500GeV_phase1.txt", "symtestzminus3/symtestzminus3_aneut_6500GeV_phase1.txt", "symtestzminus3/symtestzminus3_prot_6500GeV_phase1.txt", "symtestzminus3/symtestzminus3_aprot_6500GeV_phase1.txt", "symtestzminus3/symtestzminus3_pions_6500GeV_phase1.txt"]
    # percerrtxt_files = ["symtestzminus3/symtestzminus3_allpart_6500GeV_phase1_perc_errors.txt", "symtestzminus3/symtestzminus3_neut_6500GeV_phase1_perc_errors.txt", "symtestzminus3/symtestzminus3_aneut_6500GeV_phase1_perc_errors.txt", "symtestzminus3/symtestzminus3_prot_6500GeV_phase1_perc_errors.txt", "symtestzminus3/symtestzminus3_aprot_6500GeV_phase1_perc_errors.txt", "symtestzminus3/symtestzminus3_pions_6500GeV_phase1_perc_errors.txt"]

    # write_txt_files(args.input_ascii_file_name, txt_file_names)
    # sum_txt_files(input_charged_txt_file_names, output_charged_txt_file_name)
    # sum_txt_files(input_neutral_txt_file_names, output_neutral_txt_file_name)

    fluence_file = ROOT.TFile.Open(output_root_file_name, "RECREATE")
    for txt_file_name in all_txt_file_names:
        histogram_base_name = os.path.basename(txt_file_name).replace(".txt", "").replace(suffix, "")
        th2 = get_th2(txt_file_name, histogram_base_name)
        th2.Write()
    fluence_file.Close()
    print("%s has been written." % output_root_file_name)

    units_file_name = output_root_file_name.replace(".root", "_units.txt")
    with open(units_file_name, "w") as units_file:
        units_file.write("fluence: n_{eq} cm^{-2}\n")
        units_file.write("r: cm\n")
        units_file.write("z: cm")
    print("%s has been written." % units_file_name)

 
if __name__ == "__main__":

    args = __get_arguments()
    main(args)