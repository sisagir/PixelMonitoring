import os
import pandas as pd

from array import array as pyArray
import ROOT

from utils import eraUtils as eraUtl
from utils.pythonUtils import run_bash_command


def get_database_password(file_name="pwd.txt"):
    directory = run_bash_command("echo $PIXEL_MONITORING_DIR")
    with open(directory + "/" + file_name) as f:
        return f.readline().strip()


def get_bad_fills(bad_fills_file_name):
    with open(bad_fills_file_name) as file:
        bad_fills = file.readlines()
    bad_fills = [int(x.replace("\n", "")) for x in bad_fills]
    return bad_fills


def get_fill_info(fill_info_file_name):
    return pd.read_csv(fill_info_file_name)


def get_fills(fills_info, bad_fills, first_fill=None, last_fill=None, era=None):

    fills = []

    if first_fill and last_fill:
        for fill in range(first_fill, last_fill+1):
            if fill not in fills_info.fill_number.values or fill in bad_fills:
                continue

            start_stable_beam = fills_info.start_stable_beam[fills_info.fill_number == fill].to_list()
            if len(start_stable_beam) > 1:
                print("Error! Fill %d appears twice in input fills file name." % fill)
            start_stable_beam = start_stable_beam[0]
            if "2013" in start_stable_beam: continue  # TODO: Why is it like this?

            fills.append(fill)

    else:
        fills_in_era = eraUtl.get_fills_for_era(era)
        fills = list(set(fills_info.fill_number) & (set(fills_in_era)))
        fills = [fill for fill in fills if fill not in bad_fills]

    return fills


def get_integrated_lumi_per_fill(luminosity_file_name, fills=None):

    df = pd.read_csv(luminosity_file_name)
    condition = lambda x: (fills is not None and x in fills) or (fills is None)
    integrated_lumi_per_fill = {
        fill: lumi for fill, lumi in zip(df["fill"], df["integrated delivered (/fb)"])
        if condition(fill)
    }
    
    return integrated_lumi_per_fill


def get_graph(x, y, x_label, y_label, title=""):
    if not isinstance(x, pyArray):
        x = pyArray("f", x)
    if not isinstance(y, pyArray):
        y = pyArray("f", y)
    graph = ROOT.TGraph(len(x), x, y)
    graph.GetXaxis().SetTitle(x_label)
    graph.GetYaxis().SetTitle(y_label)
    graph.SetTitle(title)

    return graph


def remove_files(files_list):
    for file_name in files_list:
        if os.path.isfile(file_name):
            os.remove(file_name)
