import os

from SSD_IVCVanalysis.parser.HEPHY_HGCAL_parser import instantiate_measurement

from SSD_IVCVanalysis.CV import CV, plot_CV, plot_C2V
from SSD_IVCVanalysis.IV import IV, plot_IV
from SSD_IVCVanalysis.IVinter import IVinter, plot_IVinter
from SSD_IVCVanalysis.CVinter import CVinter, plot_CVinter
from SSD_IVCVanalysis.utils import show_plots
import copy
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
myCV_list = CV.instantiate_from_HEPHY_HGCAL(f_cv, is_open=False)
myCV_open_list = CV.instantiate_from_HEPHY_HGCAL(f_cv_open, is_open=True)

# Get data frame of all measurements
CV_df = CV.get_DataFrame()

# select CV mode and frequency
freq = CV_df["Frequency [Hz]"] == 10e3
mode = CV_df["CV-mode"] == "s"
is_open = CV_df["Open measurement"]

myCV = CV_df.loc[freq & mode & ~is_open, "CV_meas"].item()
myCV_open = CV_df.loc[freq & mode & is_open, "CV_meas"].item()

# correct with open measurement
myCV.correct_CV_open(myCV_open)

# plot CV measurement
plot_CV([myCV])
plot_C2V([myCV])


##### IV

myIV = IV.instantiate_from_HEPHY_HGCAL(f_iv, T=-20.0)
# files can also be parsed without knowing the measurement type
mymeas = instantiate_measurement(f_iv, is_open=False, T=-20.0)
# change label and fmt
myIV.label = f"Irradiated 1.4E16, T={myIV.T}C"
myIV.fmt = "rv"

plot_IV([myIV])


##### IV inter

myIVinter = IVinter.instantiate_from_HEPHY_HGCAL(f_iv_inter, T=-20.0)
plot_IVinter([myIVinter])


##### CV inter
myCVinter = CVinter.instantiate_from_HEPHY_HGCAL(f_cvinter, is_open=False)
myCVinter_open = CVinter.instantiate_from_HEPHY_HGCAL(f_cvinter_open, is_open=True)
for i in range(3):
    myCVinter[i].correct_CVinter_open(myCVinter_open[i])
plot_CVinter([myCVinter[0], myCVinter[1], myCVinter[2]])

show_plots()
