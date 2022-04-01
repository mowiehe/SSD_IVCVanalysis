import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from .parser import HEPHY_HGCAL_parser
from . import utils
from .Measurement import Measurement
import pdb


class CVinter(Measurement):
    all_CVinter = []

    @classmethod
    def instantiate_from_HEPHY_HGCAL(
        cls, filename, is_open, device=None, fmt=None, label=None
    ):
        CVinter_dict_list = HEPHY_HGCAL_parser.read_CVinter(filename)
        return [
            CVinter(
                CVinter_dict["V"],
                CVinter_dict["C"],
                CVinter_dict["dC"],
                CVinter_dict["freq"],
                CVinter_dict["filename"],
                is_open=is_open,
                device=device,
                fmt=fmt,
                label=label,
            )
            for CVinter_dict in CVinter_dict_list
        ]

    @classmethod
    def get_DataFrame(cls):
        freq = [i.freq for i in cls.all_CVinter]
        filename = [i.filename for i in cls.all_CVinter]
        is_open = [i.is_open for i in cls.all_CVinter]
        df = pd.DataFrame(
            {
                "Filename": filename,
                "Frequency [Hz]": freq,
                "Open measurement": is_open,
                "CVinter_meas": cls.all_CVinter,
            }
        )
        return df

    def __init__(
        self, V, C, dC, freq, filename, is_open, device=None, fmt=None, label=None
    ):
        super().__init__(filename, device, fmt, label)
        # initialize with device name, voltage array, capacitance and measurement frequency
        assert type(V) == np.ndarray, "Voltage array as np.ndarray"
        assert type(C) == np.ndarray, "Capacitance array as np.ndarray"
        assert type(dC) == np.ndarray, "Capacitance error array as np.ndarray"
        assert type(freq) == float, "Provide measurement frequency as float"
        assert type(is_open) == bool, "is_open, True or False?"

        self.is_negative_V = True if V.mean() < 0 else False
        self.V = V * -1 if self.is_negative_V else V
        self.C = C
        self.dC = dC
        self.freq = freq
        self.is_open = is_open
        self.label = self.label if self.label else f"{self.freq/1000}kHz"

        CVinter.all_CVinter.append(self)

    def correct_CVinter_open(self, CVinter_open):
        # CVinter_open can be a CVinter_meas object or a float value
        # in case of CVinter_meas object, freq have to be identical
        if type(CVinter_open) == CVinter:
            if self.freq == CVinter_open.freq:
                if all(self.V == CVinter_open.V):
                    CVinter_open = CVinter_open.C
                else:  # take the mean value if different voltages
                    CVinter_open = CVinter_open.C.mean()
            else:
                print("Frequencies differ for CVinter open correction", self.filename)
                CVinter_open = np.nan
        self.C = self.C - CVinter_open


def plot_CVinter(meas_list, Cprefix="p", Clim=[None, None], Vlim=[None, None]):
    fig, ax = plt.subplots()

    for meas in meas_list:
        # change plot scale
        plotC = meas.C * utils.prefix[Cprefix]
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, plotC, fmt, label=meas.label)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"Interpad capacitance [{Cprefix}F]")
    ax.set_xlim(Vlim)
    ax.set_ylim(Clim)
    ax.legend()
    return fig, ax
