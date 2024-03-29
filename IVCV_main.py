#!/usr/bin/env python3
# Command line tool for plotting SSD IV and CV measurements
# E.g. python3 -i IVCV_main.py -f $file1 $file2 -l $label1 $label2 -Ilim 0 30 -Clim 0 100

from argparse import ArgumentParser
import os.path
from SSD_IVCVanalysis.parser import SSDparser as parser
from SSD_IVCVanalysis import utils
from SSD_IVCVanalysis.IV import plot_IV
from SSD_IVCVanalysis.CV import plot_CV, plot_C2V
import pdb

####
default_search_path = "/home/mw/cernbox/SSD_Defects/CIS_LGADs/EPI_5mm__cv-iv"
####

if __name__ == "__main__":
    PARSER = ArgumentParser()
    PARSER.add_argument("-f", nargs="+", help="Measurement file(s)")
    PARSER.add_argument("-l", nargs="+", help="Measurement label(s)")
    PARSER.add_argument(
        "-Ilim",
        nargs="+",
        type=float,
        default=[None, None],
        help="Low and high limit of current: -Ilim low high",
    )
    PARSER.add_argument(
        "-Clim",
        nargs="+",
        default=[None, None],
        type=float,
        help="Low and high limit of capacitance: -Clim low high",
    )
    PARSER.add_argument(
        "-C2lim",
        nargs="+",
        default=[None, None],
        type=float,
        help="Low and high limit of 1/C2: -C2lim low high",
    )

    PARSER.add_argument("-Iprefix", default="p", help="Unit prefix of current")
    PARSER.add_argument(
        "-Cprefix",
        default="p",
        help="Unit prefix of capacitance",
    )
    PARSER.add_argument(
        "-search_in",
        default=default_search_path,
        help="Location of measurements",
    )
    PARSER.add_argument(
        "-title",
        default=None,
        help="Title of the figures",
    )
    args = PARSER.parse_args()

    # check if all given files exist
    my_files = []
    for f in args.f:
        if os.path.isfile(f):
            my_files.append(f)
        else:
            # try to find it under search path
            for root, directory, files in os.walk(args.search_in):
                found = [
                    os.path.join(root, ifile) for ifile in files if f in ifile
                ]  # list of files matching searchstring
                found.sort()
                my_files += found
    # check if same number of labels and files
    has_labels = bool(args.l)
    if has_labels and len(args.l) != len(my_files):
        raise Exception("Unequal number of files and labels")
    # instantiate measurements
    meas_list = []
    for i, f in enumerate(my_files):
        try:
            meas = parser.instantiate_measurement(f)
        except:
            print("Parsing not possible, skipping file..")
            continue
        if has_labels:
            meas.label = args.l[i]
        else:
            meas.label = os.path.basename(f)
        meas_list.append(meas)
    # Print information about measurements
    for meas in meas_list:
        meas.print_info()
    # identify CV and IV measurements
    IV_list = [meas for meas in meas_list if meas.Type == "IV"]
    CV_list = [meas for meas in meas_list if meas.Type == "CV"]
    # plot IV and CV measurements
    if bool(IV_list):
        fig_IV, ax_IV = plot_IV(
            IV_list, log=False, Ilim=args.Ilim, Iprefix=args.Iprefix
        )
        ax_IV.set_title(args.title)
        fig_IV.tight_layout()
    if bool(CV_list):
        fig_CV, ax_CV = plot_CV(CV_list, Clim=args.Clim, Cprefix=args.Cprefix)
        ax_CV.set_title(args.title)
        fig_CV.tight_layout()

        fig_C2V, ax_C2V = plot_C2V(CV_list, C2lim=args.C2lim, log=False)
        ax_C2V.set_title(args.title)
        fig_C2V.tight_layout()

    utils.show_plots()
