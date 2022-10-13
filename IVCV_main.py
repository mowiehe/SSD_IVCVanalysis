# Command line tool for plotting SSD IV and CV measurements
# E.g. python3 -i IVCV_main.py -f $file1 $file2 -l $label1 $label2 -Ilim 0 30 -Clim 0 100

from argparse import ArgumentParser
import os.path
from SSD_IVCVanalysis.parser import SSDparser as parser
from SSD_IVCVanalysis import utils
from SSD_IVCVanalysis.IV import plot_IV
from SSD_IVCVanalysis.CV import plot_CV
import pdb

####
default_search_path = "/home/mw/cernbox/SSD_Defects/CIS_LGADs/EPI_1mm__cv-iv/"
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
    args = PARSER.parse_args()

    # check if all given files exist
    my_files = []
    # pdb.set_trace()
    for f in args.f:
        if os.path.isfile(f):
            my_files.append(f)
        else:
            # try to find it under search path
            found = False
            for root, directory, files in os.walk(args.search_in):
                if f in files:
                    my_files.append(os.path.join(root, f))
                    found = True
            if not found:
                raise Exception(f"File {f} not found")
    # check if same number of labels and files
    if bool(args.l) and len(args.l) != len(files):
        raise Exception("Unequal number of files and labels")
    # instantiate measurements
    meas_list = [
        parser.instantiate_measurement(f, label=args.l[i])
        for i, f in enumerate(my_files)
    ]
    # identify CV and IV measurements
    IV_list = [meas for meas in meas_list if meas.Type == "IV"]
    CV_list = [meas for meas in meas_list if meas.Type == "CV"]
    # plot IV and CV measurements
    fig_IV, ax_IV = plot_IV(IV_list, log=False, Ilim=args.Ilim, Iprefix=args.Iprefix)
    fig_CV, ax_CV = plot_CV(CV_list, Clim=args.Clim, Cprefix=args.Cprefix)
    fig_IV.tight_layout()
    fig_CV.tight_layout()

    utils.show_plots()
