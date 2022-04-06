import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from .parser import HEPHY_HGCAL_parser
from .Measurement import Measurement
from . import utils
import pdb


class CV(Measurement):
    all_CV = []

    @classmethod
    def instantiate_from_HEPHY_HGCAL(
        cls, filename, T, is_open, device=None, fmt=None, label=None
    ):
        CV_dict_list = HEPHY_HGCAL_parser.read_CV(filename)
        return [
            CV(
                CV_dict["V"],
                CV_dict["C"],
                CV_dict["freq"],
                CV_dict["mode"],
                CV_dict["filename"],
                T,
                is_open=is_open,
                device=device,
                fmt=fmt,
                label=label,
            )
            for CV_dict in CV_dict_list
        ]

    @classmethod
    def get_DataFrame(cls):
        freq = [i.freq for i in cls.all_CV]
        mode = [i.mode for i in cls.all_CV]
        filename = [i.filename for i in cls.all_CV]
        is_open = [i.is_open for i in cls.all_CV]
        df = pd.DataFrame(
            {
                "Filename": filename,
                "Frequency [Hz]": freq,
                "CV-mode": mode,
                "Open measurement": is_open,
                "CV_meas": cls.all_CV,
            }
        )
        return df

    def __init__(
        self, V, C, freq, mode, filename, T, is_open, device=None, fmt=None, label=None
    ):
        super().__init__(filename, T, device, fmt, label)
        # initialize with device name, voltage array, capacitance and measurement frequency
        assert type(V) == np.ndarray, "Voltage array as np.ndarray"
        assert type(C) == np.ndarray, "Capacitance array as np.ndarray"
        assert type(freq) == float, "Provide measurement frequency as float"
        assert str.lower(mode) == "s" or mode == "p", "mode is s or p?"
        assert type(is_open) == bool, "is_open, True or False?"

        self.is_negative_V = True if V.mean() < 0 else False
        self.V = V * -1 if self.is_negative_V else V
        self.C = C
        self.freq = freq
        self.mode = str.lower(mode)
        self.is_open = is_open
        self.label = self.label if self.label else f"{self.freq/1000}kHz  {self.mode}"

        self.corrected = False

        CV.all_CV.append(self)

    def C2(self):
        return 1 / self.C ** 2

    def correct_CV_open(self, CV_open):
        # CV_open can be a CV_meas object or a float value
        # in case of CV_meas object, freq have to be identical
        if type(CV_open) == CV:
            if self.freq == CV_open.freq:
                if all(self.V == CV_open.V):
                    CV_open = CV_open.C
                else:  # take the mean value if different voltages
                    CV_open = CV_open.C.mean()
            else:
                print("Frequencies differ for CV open correction", self.filename)
                CV_open = np.nan
        self.C = self.C - CV_open
        self.corrected = True


def plot_CV(meas_list, Cprefix="p", Clim=[None, None], Vlim=[None, None]):
    fig, ax = plt.subplots(figsize=[8, 6])

    for meas in meas_list:
        # change plot scale
        plotC = meas.C * utils.prefix[Cprefix]
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, plotC, fmt, label=meas.label)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"Capacitance [{Cprefix}F]")
    ax.set_xlim(Vlim)
    ax.set_ylim(Clim)
    ax.grid(True)
    ax.legend()
    return fig, ax


def plot_C2V(meas_list, C2lim=[None, None], Vlim=[None, None]):
    fig, ax = plt.subplots(figsize=[8, 6])

    for meas in meas_list:
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, meas.C2(), fmt, label=meas.label)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"$1 / C^2$ [$1/F^2$]")
    ax.set_xlim(Vlim)
    ax.set_ylim(C2lim)
    ax.grid(True)
    ax.legend()
    return fig, ax
