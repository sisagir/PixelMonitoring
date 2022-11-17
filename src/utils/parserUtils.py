import argparse


class ArgumentParser(argparse.ArgumentParser):

    def __init__(self):
        super().__init__()

    # Input / Output flags

    def add_input_fills_file_flag(self):
        self.add_argument(
            "-i", "--input_fills_file_name",
            help="Fills file, default=%(default)s",
            required=False,
            default="data/fills_info/fills.csv",
        )

    def add_bad_fills_file_flag(self):
        self.add_argument(
            "-bf", "--bad_fills_file_name",
            help="Bad fills file, default=%(default)s",
            default="data/fills_info/bad_fills.txt",
        )
    
    def add_input_fills_flags(self, first_fill_required=True, last_fill_required=True):
        self.add_argument(
            "-ff", "--first_fill",
            help="First fill number to analyse",
            type=int,
            required=first_fill_required,
        )
        self.add_argument(
            "-lf", "--last_fill",
            help="Last fill number to analyse",
            type=int,
            required=last_fill_required,
        )
    
    def add_currents_input_directory_flag(self, default_directory):
        self.add_argument(
            "-c", "--input_currents_directory",
            help="Input currents directory, default=%(default)s",
            default=default_directory,
        )

    def add_output_directory_flag(self, default_directory):
        self.add_argument(
            "-o", "--output_directory",
            help="Output directory name, default=%(default)s",
            required=False,
            default=default_directory,
        )

    # Other flags

    def add_sub_system_flag(self):
        self.add_argument(
            "-s", "--sub_system",
            help="Sub-detector to analyse",
            choices=["Barrel", "EndCap"],
            required=True,
        )

    def add_layer_flag(self, default=1):
        self.add_argument(
            "-layer", "--layer",
            help="Layer",
            type=int,
            choices=[1, 2, 3, 4],
            default=default,
            required=False,
        )

    def add_y_axis_range_flags(self, defaults=None):
        if defaults is not None:
            args1 = {
                "required": False,
                "default": defaults[0],
                "help": "y-axis minimum, default=%(default)s",
            }
            args2 = {
                "required": False,
                "default": defaults[1],
                "help": "y-axis maximum, default=%(default)s",
            }
        else:
            args1 = {
                "required": True,
                "help": "y-axis minimum, mandatory",
            }
            args2 = {
                "required": True,
                "help": "y-axis maximum, mandatory",
            }

        self.add_argument(
            "-ymin", "--ymin",
            type=float,
            **args1,
        )
        self.add_argument(
            "-ymax", "--ymax",
            type=float,
            **args2,
        )
 
