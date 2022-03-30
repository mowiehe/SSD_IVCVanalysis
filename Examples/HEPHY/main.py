import os

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


# CV
myCV = CV.instantiate_from_HEPHY_HGCAL(f_cv, is_open=False)
myCV_open = CV.instantiate_from_HEPHY_HGCAL(f_cv_open, is_open=True)
# select CV mode and frequency
# myCV_s = [a for a in myCV if a.mode == "s"]
CV = myCV[0]
CV.label = "not corrected"

CV_corr = copy.copy(CV)
CV_open = myCV_open[0]
# open_correction = myCV_open[0].C.mean()
# CV_corr.correct_CV_open(open_correction)
CV_corr.correct_CV_open(CV_open)
CV_corr.label = "corrected"
CV_corr.fmt = "ok"

plot_CV([CV, CV_corr])


# IV

myIV = IV.instantiate_from_HEPHY_HGCAL(f_iv, T=-20.0)
plot_IV([myIV])


# IV inter

myIVinter = IVinter.instantiate_from_HEPHY_HGCAL(f_iv_inter, T=-20.0)
plot_IVinter([myIVinter])

# CVinter
myCVinter = CVinter.instantiate_from_HEPHY_HGCAL(f_cvinter, is_open=False)
myCVinter_open = CVinter.instantiate_from_HEPHY_HGCAL(f_cvinter_open, is_open=True)
for i in range(3):
    myCVinter[i].correct_CVinter_open(myCVinter_open[i])
plot_CVinter([myCVinter[0], myCVinter[1], myCVinter[2]])

show_plots()
