import os

import SSD_IVCVanalysis.parser.HEPHY_HGCAL_parser as parser

import SSD_IVCVanalysis.CV as CV
import SSD_IVCVanalysis.IV as IV
import SSD_IVCVanalysis.IVinter as IVinter
import SSD_IVCVanalysis.CVinter as CVinter
import SSD_IVCVanalysis.utils as utils
import pdb

script_path = os.path.dirname(os.path.realpath(__file__))  # scripts directory

# data by HEPHY HGCAL setup
f_cv = script_path + "/HPK_ProtoA_300042_HD_UR_1.4E16/cv/cv.dat"
f_iv = script_path + "/HPK_ProtoA_300042_HD_UR_1.4E16/iv/iv.dat"
f_iv_inter = script_path + "/HPK_ProtoA_300042_HD_UR_1.4E16/iv_inter/iv_inter.dat"
f_cvinter = script_path + "/HPK_ProtoA_300042_HD_UR_1.4E16/cv_inter/cv_inter.dat"

f_cv_open = script_path + "/HPK_ProtoA_300042_HD_UR_1.4E16_CV_open/cv/cv.dat"
f_cvinter_open = (
    script_path + "/HPK_ProtoA_300042_HD_UR_1.4E16_CV_open/cv_inter/cv_inter.dat"
)

##### CV
# Instantiate CV measurements
myCV_list = parser.instantiate_CV(f_cv, T=-20, is_open=False)
myCV_open_list = parser.instantiate_CV(f_cv_open, T=-20, is_open=True)

# Get data frame of all measurements
CV_df = CV.CV.get_DataFrame()

# select CV mode and frequency
freq = CV_df["Frequency [Hz]"] == 10e3
mode = CV_df["CV-mode"] == "s"
is_open = CV_df["Open measurement"]

myCV = CV_df.loc[freq & mode & ~is_open, "CV_meas"].item()
myCV_open = CV_df.loc[freq & mode & is_open, "CV_meas"].item()

# correct with open measurement
myCV.correct_CV_open(myCV_open)

# plot CV measurement
CV.plot_CV([myCV])
CV.plot_C2V([myCV])


##### IV

myIV = parser.instantiate_IV(f_iv, T=-20.0)

# files can also be parsed without knowing the measurement type
mymeas = parser.instantiate_measurement(f_iv, is_open=False, T=-20.0)

# change label and fmt
myIV.label = f"Irradiated 1.4E16, T={myIV.T}C"
myIV.fmt = "rv"

IV.plot_IV([myIV])


##### IV inter

myIVinter = parser.instantiate_IVinter(f_iv_inter, T=-20.0)
IVinter.plot_IVinter([myIVinter])


##### CV inter
myCVinter = parser.instantiate_CVinter(f_cvinter, T=-20, is_open=False)
myCVinter_open = parser.instantiate_CVinter(f_cvinter_open, T=-20, is_open=True)
for i in range(3):
    myCVinter[i].correct_CVinter_open(myCVinter_open[i])
CVinter.plot_CVinter([myCVinter[0], myCVinter[1], myCVinter[2]])

utils.show_plots()
