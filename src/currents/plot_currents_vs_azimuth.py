from pathlib import Path
import math

import ROOT

from utils import generalUtils as gUtl
from utils import pixelDesignUtils as designUtl
from utils.parserUtils import ArgumentParser
from utils.pythonUtils import dict_linear_combination
from utils.Module import ReadoutGroup
from utils.constants import *

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetOptFit(0o001)
ROOT.gStyle.SetPadLeftMargin(0.15)
ROOT.gStyle.SetPadBottomMargin(0.15)
# ROOT.gStyle.SetPadTopMargin(0.1)


def __get_arguments():

    parser = ArgumentParser()
    parser.add_input_fills_file_flag()
    parser.add_bad_fills_file_flag()
    parser.add_currents_input_directory_flag(default_directory="data/currents/processed")
    parser.add_output_directory_flag(default_directory="plots/currents")
    parser.add_input_fills_flags(first_fill_required=True, last_fill_required=False)
    parser.add_sub_system_flag()
    parser.add_y_axis_range_flags(defaults=(0., 2000.))
    parser.add_layer_flag(default=1)

    return parser.parse_args()


# TODO: Put this function in some utils scripts
def __temperature_scale_leakage_current(I, T):
    I_vol = I/rocVol
    #print "Average current per ROC: ", I
    a = -Eg/(2*kb)
    b =  (1./Tref) - (1./T)
    expo = a * b
    IatZero = I_vol * math.pow(Tref/T, 2) *math.exp(expo)
#    return I_vol#IatZero
    return IatZero


def __get_leakage_currents_per_readout_group(fill, sub_system, layer, currents_directory, side="m"):
    """Get currents versus azimuth phi for minus or plus z-side.
    
    Args:
        side (str): "m" or "p" for minus or plus side
    """

    # TODO: Correct for this centrally
    T_coolant = designUtl.get_coolant_temperature_for_fill(fill)
    ### Sensor temperature in Kelvin
    T_sensor = T_coolant + T_diff + Kfact

    filename = currents_directory + "/" + str(fill) + "_" + sub_system + "_HV_ByLayer.txt"
    f = open(filename, 'r+')

    leakage_current_per_readout_group = {}

    layer_string = "LYR" + str(layer)
    for row in f.readlines():
        readout_group_name, leakage_current = row.split()
        _, half_cylinder, _, layer_candidate = readout_group_name.split("_")
        z_side = half_cylinder[1]
        if layer_candidate != layer_string: continue
        if z_side != side: continue
        leakage_current = float(leakage_current)
        rescaled_leakage_current = __temperature_scale_leakage_current(leakage_current, T_sensor)
        if readout_group_name in leakage_current_per_readout_group.keys():
            print("Error: {readout_group_name} already added to dict!")
            exit(0)
        leakage_current_per_readout_group[readout_group_name] = rescaled_leakage_current

    return leakage_current_per_readout_group


def __get_graph_vs_azimuth(quantity_per_readout_group, y_label, title, color):

    x_label = "Azimuthal angle #Phi [rad]"

    azimuthal_angles = []
    y_values = []
    for readout_group_name, quantity in quantity_per_readout_group.items():
        readout_group = ReadoutGroup(readout_group_name)
        phi = readout_group.getAverageAzimuthalAngle()
        azimuthal_angles.append(phi)
        y_values.append(quantity)
        
    graph = gUtl.get_graph(azimuthal_angles, y_values, x_label, y_label, title)
    graph.SetLineColor(color)
    graph.SetMarkerColor(color)
    graph.SetMarkerStyle(22)
    graph.SetMarkerSize(0.8)
    return graph


def __plot_graphs(graph_minus_side, graph_plus_side, y_min, y_max, legend_text,
                  output_directory, figure_name, extensions):

    leg = ROOT.TLegend(0.3, 0.78, 0.9, 0.9)
    ROOT.SetOwnership(leg, 0)

    leg.SetNColumns(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetBorderSize(0)

    c = ROOT.TCanvas()
    c.cd()

    graph_plus_side.GetYaxis().SetRangeUser(y_min, y_max)
    graph_minus_side.GetYaxis().SetRangeUser(y_min, y_max)

    graph_plus_side.GetXaxis().SetLabelSize(0.045)
    graph_plus_side.GetYaxis().SetLabelSize(0.045)
    graph_plus_side.GetXaxis().SetTitleSize(0.05)
    graph_plus_side.GetYaxis().SetTitleSize(0.05)
    graph_plus_side.GetXaxis().SetTitleOffset(1.2)
    graph_plus_side.GetYaxis().SetTitleOffset(1.35)
    graph_plus_side.Draw("AP")
    graph_minus_side.Draw("Psame")

    leg.AddEntry(graph_plus_side, f"{legend_text}, +z", "P")
    leg.AddEntry(graph_minus_side, f"{legend_text}, -z", "P")
    leg.Draw("same")
    
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(61)
    latex.SetTextAlign(11)
    latex.DrawLatex(0.1, .93, "CMS");
    latex.SetTextFont(52)
    latex.DrawLatex(0.18, .93, "Preliminary");

    # TODO: Automatize center of mass energy for Run3
    # latex2 = ROOT.TLatex()
    # latex2.SetNDC()
    # latex2.SetTextFont(42)
    # latex2.SetTextSize(0.04)
    # latex2.SetTextAlign(11)
    # latex2.DrawLatex(0.615, 0.93, " 42.45 fb^{-1} at #sqrt{s} = 13 TeV");

    figure_base_name = output_directory + "/" + figure_name
    for extension in extensions:
        full_figure_name = figure_base_name + extension
        c.Print(full_figure_name)



def __plot_leakage_current_vs_phi(
        fill,
        sub_system,
        layer,
        y_min,
        y_max,
        input_currents_directory,
        output_directory,
        extensions=(".png", ".pdf"),
    ):

    base_args = (fill, sub_system, layer, input_currents_directory)
    leakage_current_per_readout_group_minus_side = __get_leakage_currents_per_readout_group(*base_args, side="m")
    leakage_current_per_readout_group_plus_side  = __get_leakage_currents_per_readout_group(*base_args, side="p")

    labels_args = {
        "title": "",
        "y_label": "I_{leak} [#mu A / cm^{3}]", 
    }
    graph_minus_side = __get_graph_vs_azimuth(
        leakage_current_per_readout_group_minus_side,
        color=ROOT.kBlue,
        **labels_args
    )
    graph_plus_side = __get_graph_vs_azimuth(
        leakage_current_per_readout_group_plus_side,
        color=ROOT.kRed,
        **labels_args
    )

    figure_name = "leakage_current_vs_azimuthal_angle_fills_%d" % (fill)
    legend_text = f"Fill {fill}, Layer {layer}"
    __plot_graphs(graph_minus_side, graph_plus_side, y_min, y_max, legend_text,
                  output_directory, figure_name, extensions)


def __plot_leakage_current_difference_vs_phi(
        first_fill,
        last_fill,
        sub_system,
        layer,
        y_min,
        y_max,
        input_currents_directory,
        output_directory,
        extensions=(".png", ".pdf"),
    ):

    base_args = (first_fill, sub_system, layer, input_currents_directory)
    leakage_current_reference_per_sector_minus_side = __get_leakage_currents_per_readout_group(*base_args, side="m")
    leakage_current_reference_per_sector_plus_side  = __get_leakage_currents_per_readout_group(*base_args, side="p")

    base_args = (last_fill, sub_system, layer, input_currents_directory)
    leakage_current_per_readout_group_minus_side = __get_leakage_currents_per_readout_group(*base_args, side="m")
    leakage_current_per_readout_group_plus_side  = __get_leakage_currents_per_readout_group(*base_args, side="p")

    leakage_current_difference_per_sector_minus_side = dict_linear_combination(
        leakage_current_per_readout_group_minus_side,
        leakage_current_reference_per_sector_minus_side,
        1,
        -1,
        reduce_to_common_keys=True,
    )
    leakage_current_difference_per_sector_plus_side = dict_linear_combination(
        leakage_current_per_readout_group_plus_side,
        leakage_current_reference_per_sector_plus_side,
        1,
        -1,
        reduce_to_common_keys=True,
    )
    
    labels_args = {
        "title": "",
        "y_label": "#Delta I_{leak} [#mu A / cm^{3}]", 
    }
    graph_minus_side = __get_graph_vs_azimuth(
        leakage_current_difference_per_sector_minus_side,
        color=ROOT.kBlue,
        **labels_args,
    )
    graph_plus_side = __get_graph_vs_azimuth(
        leakage_current_difference_per_sector_plus_side,
        color=ROOT.kRed,
        **labels_args,
    )

    figure_name = "leakage_current_difference_vs_azimuthal_angle_fills_%d_%d" % (first_fill, last_fill)
    legend_text = f"Fills difference {last_fill}/{first_fill}, Layer {layer}"
    __plot_graphs(graph_minus_side, graph_plus_side, y_min, y_max, legend_text,
                  output_directory, figure_name, extensions)


def main(args):

    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    bad_fills = gUtl.get_bad_fills(args.bad_fills_file_name)
    fills_info = gUtl.get_fill_info(args.input_fills_file_name)
    
    if args.last_fill is None:
        last_fill = args.first_fill
    else:
        last_fill = args.last_fill
    fills = gUtl.get_fills(fills_info, bad_fills, args.first_fill, last_fill)

    for fill in (args.first_fill, last_fill):
        if fill not in fills:
            print("Error: Fill %d is not in list of valid fills!" % fill)

    base_args = (
        args.sub_system,
        args.layer,
        args.ymin,
        args.ymax,
        args.input_currents_directory,
        args.output_directory,
    )
    if args.last_fill is None:
        __plot_leakage_current_vs_phi(
            args.first_fill,
            *base_args,
        )
    else:
        __plot_leakage_current_difference_vs_phi(
            args.first_fill,
            args.last_fill,
            *base_args,
        )


if __name__ == "__main__":

    args = __get_arguments()
    main(args)
