import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from omsapi import OMSAPI


def __get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--output_directory",
        help="Output directory name",
        required=False,
        default="./fills_info/",
    )
    parser.add_argument(
        "-suffix", "--output_file_name_suffix",
        help="Output file name",
        required=False,
        default="",
    )
    parser.add_argument(
        "-ff", "--first_fill",
        help="First fill number to analyse",
        type=int,
        required=True,
    )
    parser.add_argument(
        "-lf", "--last_fill",
        help="Last fill number to analyse",
        type=int,
        required=True,
    )

    return parser.parse_args()


def __get_data(first_fill, last_fill, attributes):
    omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False)
    omsapi.auth_krb()
    
    # Create a query.
    query = omsapi.query("fills")
    query.set_verbose(False)

    query.attrs(attributes)
    query.filter("fill_number", first_fill, "GE")
    query.filter("fill_number", last_fill, "LE")
    for fill in range(3474, 3564):
        query.filter("fill_number", fill, "NEQ")

    query.filter("stable_beams", "true", "EQ")
    query.filter("start_time", "null", "NEQ")
    query.filter("delivered_lumi", "null", "NEQ")
    query.filter("delivered_lumi", 0, "GT")
    query.filter("injection_scheme", "null", "NEQ")

    query.paginate(1, per_page=last_fill-first_fill+1)
    
    data = pd.json_normalize(query.data().json()["data"])

    mapping = {
        x: x.replace("attributes.", "")
        for x in data.columns
    }
    data.rename(columns=mapping, inplace=True)
    data = data[attributes]

    return data


def __add_integrated_lumi(data, lumi_column_name="delivered_lumi"):
    lumi = data[lumi_column_name]
    integrated_lumi = np.cumsum(lumi)
    data["integrated_" + lumi_column_name] = integrated_lumi
    return data
    

def main():

    args = __get_arguments()
    Path(args.output_directory).mkdir(parents=True, exist_ok=True)

    attributes = ["delivered_lumi", "fill_number", "start_time", "end_time"]
    data = __get_data(args.first_fill, args.last_fill, attributes)
    data = __add_integrated_lumi(data)
    data.drop(columns="delivered_lumi", inplace=True)
    
    output_file_name = args.output_directory + "/" + "fills" + args.output_file_name_suffix + ".txt"
    data.to_csv(output_file_name, index=False, columns=["fill_number", "start_time", "end_time"])
            
    output_file_name = args.output_directory + "/" + "fills_with_integrated_lumi" + args.output_file_name_suffix + ".txt"
    data.to_csv(output_file_name, index=False)


if __name__ == "__main__":
   main()
