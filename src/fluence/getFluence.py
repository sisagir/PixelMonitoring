import ROOT
import argparse


class FluenceField(object):
    def __init__(self, fluence_root_file_name, units_file_name):
        self.__fluence_root_file = ROOT.TFile.Open(fluence_root_file_name)
        self.__units_file = open(units_file_name)
        self.__fluence_histo = self.__fluence_root_file.Get("fluence_allpart")
        self.__units = {}
        for line in self.__units_file.read().splitlines():
            quantity = line.split(": ")[0]
            unit = line.split(": ")[1]
            self.__units[quantity] = unit

    def get_fluence(self, r, z):
        bin_x = self.__fluence_histo.GetXaxis().FindBin(r)
        bin_y = self.__fluence_histo.GetYaxis().FindBin(z)
        fluence = self.__fluence_histo.GetBinContent(bin_x, bin_y)
        return fluence

    def get_unit(self, quantity):
        return self.__units[quantity]


def main(args):
    fluence_field = FluenceField(args.f, args.u)
    print("Fluence at r = {r} {r_unit} and z = {z} {z_unit}:\n{fluence} {fluence_unit}".format(
        r=args.r,
        r_unit=fluence_field.get_unit("r"),
        z=args.z,
        z_unit=fluence_field.get_unit("z"),
        fluence=fluence_field.get_fluence(args.r, args.z),
        fluence_unit=fluence_field.get_unit("fluence"),
    ))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r',
        help='radius',
        type=float,
    )
    parser.add_argument(
        '-z',
        help='z',
        type=float,
    )
    parser.add_argument(
        '-f',
        help='Fluence ROOT file',
        default="data/fluence/fluence_field_phase1_6500GeV.root",
    )
    parser.add_argument(
        '-u',
        help='Units file',
        default="data/fluence/fluence_field_phase1_6500GeV_units.txt",
    )
    args = parser.parse_args()
    main(args)

