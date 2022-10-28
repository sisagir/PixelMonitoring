from pathlib import Path
import argparse 

import ROOT

from utils import generalUtils as gUtl


ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gStyle.SetOptFit(0o001)


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input_fills_file_name",
        help="Fills file",
        required=False,
        default="data/fills_info/fills.csv",
    )
    parser.add_argument(
        "-b", "--bad_fills_file_name",
        help="Bad fills file",
        required=False,
        default="data/fills_info/bad_fills.txt",
    )
    parser.add_argument(
        "-l", "--input_lumi_file_name",
        help="Luminosity file",
        required=False,
        default="data/fills_info/integrated_luminosity_per_fill.csv",
    )
    parser.add_argument(
        "-t", "--input_temperature_directory",
        help="Input directory with temperatures",
        required=False,
        default="data/temperatures",
    )
    parser.add_argument(
        "-ts", "--temperature_source",
        help="Temperature source",
        required=False,
        default="air",
    )
    parser.add_argument(
        "-x", "--x_axis",
        help="X-axis",
        required=False,
        choices=["fill", "lumi"],
        default="fill",
    )
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory name",
        required=False,
        default="plots/temperatures",
    )
    parser.add_argument(
        "-ff", "--first_fill",
        help="First fill number to analyse",
        type=int,
        required=False,
    )
    parser.add_argument(
        "-lf", "--last_fill",
        help="Last fill number to analyse",
        type=int,
        required=False,
    )
    parser.add_argument(
        "-s", "--sub_detector",
        help="Sub-detector to analyse",
        choices=["Barrel", "Endcap", \
                 "Barrel_BmI", "Barrel_BmO", "Barrel_BpI", "Barrel_BpO",
                 "Endcap_BmI", "Endcap_BmO", "Endcap_BpI", "Endcap_BpO",
                ],
        required=False,
    )
    
    return parser.parse_args()


def __get_temperatures(input_temperature_directory, temperature_source, sub_detector, fills):
    temperatures = {}
    for fill in fills:
        filename = input_temperature_directory + "/" + str(fill) + "_" + temperature_source + ".txt"
        with open(filename, 'r+') as file:
            temperature = 0.
            n_measurements = 0
            for row in file.readlines():
                if sub_detector is not None and sub_detector not in row: continue
                temperature += float(row.split()[1])
                n_measurements += 1
            if n_measurements == 0:
                print("Warning: no temperature for fill %s. Skipping!" % fill)
                continue
            temperature /= n_measurements
            
        temperatures[fill] = temperature

    return temperatures


def make_y_label(sub_detector, temperature_source):
    if sub_detector is None:
        sub_detector = "Pixel"
    y_label = sub_detector.replace("_", " ")\
                          .replace("Endcap", "FPix")\
                          .replace("Barrel", "BPix")\
              + " " + temperature_source \
              + " temperature [#circC]"
    return y_label


def plot_temperature(output_directory, x_axis, temperatures, integrated_lumi_per_fill, y_label):
    c = ROOT.TCanvas("Temperature.pdf")
    c.cd()
    leg = ROOT.TLegend(0.15, 0.7, 0.35, 0.85)
    ROOT.SetOwnership(leg,0)
      
    if x_axis == "fill":
        x = temperatures.keys()
        x_label = "Fill number"
    elif x_axis == "lumi":
        x = integrated_lumi_per_fill.values()
        x_label = "Integrated luminosity [fb^{-1}]"

    graph = gUtl.get_graph(
        x=x,
        y=temperatures.values(),
        x_label=x_label,
        y_label=y_label,
    )
    graph.SetLineColor(ROOT.kTeal+4)
    graph.SetMarkerColor(ROOT.kTeal+4)
    graph.SetMarkerStyle(22)
    graph.SetMarkerSize(0.8)

    ROOT.SetOwnership(graph, 0)
    graph.Draw("AP")
    graph.GetYaxis().SetTitleOffset(1.3)
  
    leg.SetNColumns(1)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetBorderSize(0)

    ### Latex box
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextFont(61)
    latex.SetTextAlign(11)
    latex.DrawLatex(0.1, .93, "CMS");
    latex.SetTextFont(52)
    latex.DrawLatex(0.18, .93, "Preliminary");

    figure_name = output_directory + "/temperatures"
    extensions = (".pdf", ".png", ".C")
    for extension in extensions:
        c.Print(figure_name + extension)


def main(args):

    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    bad_fills = gUtl.get_bad_fills(args.bad_fills_file_name)
    fills_info = gUtl.get_fill_info(args.input_fills_file_name)
    fills = gUtl.get_fills(fills_info, bad_fills, args.first_fill, args.last_fill)

    temperatures = __get_temperatures(
        args.input_temperature_directory,
        args.temperature_source,
        args.sub_detector,
        fills,
    )
    # fills = list(map(lambda x: int(x), temperatures.keys()))
    integrated_lumi_per_fill = gUtl.get_integrated_lumi_per_fill(args.input_lumi_file_name,
                                                                fills=temperatures.keys())

    plot_temperature(
        args.output_directory,
        args.x_axis,
        temperatures,
        integrated_lumi_per_fill,
        make_y_label(args.sub_detector, args.temperature_source)
    )


if __name__ == "__main__":

    args = __get_arguments()
    main(args)