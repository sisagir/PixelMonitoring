import io
import functools
import argparse

import numpy as np
import pandas as pd

import utils as utl



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
        help="First fill number to analyse. Must be greater than 1005.",
        type=int,
        required=False,
        default=1005,
    )
    parser.add_argument(
        "-lf", "--last_fill",
        help="Last fill number to analyse",
        type=int,
        required=True,
    )

    return parser.parse_args()


def __run_sanity_checks(args):
    assert args.first_fill >= 1005
    assert args.first_fill <= args.last_fill


def get_lumi(fill_begin, fill_end):
    # --normtag {normtag}
    bash_command = ("brilcalc lumi --begin {begin} --end {end} " \
                   + "-u /ub --output-style csv").format(
            # normtag=normtag,
            begin=fill_begin,
            end=fill_end,
            # output_file=brilcalc_output_file_name,
        )
    output = utl.run_bash_command(bash_command).split("\n")[1:-3]
    output[0] = output[0][1:]
    output = functools.reduce(lambda x, y: x + "\n" + y, output)

    df = pd.read_csv(io.StringIO(output))
    df["fill"] = df["run:fill"].apply(lambda x: x.split(":")[1])
    df.drop(labels=["run:fill", "time", "nls", "ncms"], axis=1, inplace=True)
    df = df.groupby("fill").sum()
    df.reset_index(inplace=True)

    return df


def cast_lumi_to_inverse_fb(df):
    df["delivered (/fb)"] = df["delivered(/ub)"] * 1e-9
    df["recorded (/fb)"] = df["recorded(/ub)"] * 1e-9
    df.drop(labels=["delivered(/ub)", "recorded(/ub)"], axis=1, inplace=True)
    return df


def add_integrated_lumi(df):
    df["integrated delivered (/fb)"] = np.cumsum(df["delivered (/fb)"])
    df["integrated recorded (/fb)"] = np.cumsum(df["recorded (/fb)"])
    return df


def main(args):

    __run_sanity_checks(args)
    
    df = get_lumi(args.first_fill, args.last_fill)
    df = cast_lumi_to_inverse_fb(df)
    df = add_integrated_lumi(df)

    output_file_name = args.output_directory + "/" + "integrated_luminosity_per_fill" + args.output_file_name_suffix + ".txt"
    df.to_csv(output_file_name, index=False)


if __name__ == "__main__":

    args = __get_arguments()
    main(args)
