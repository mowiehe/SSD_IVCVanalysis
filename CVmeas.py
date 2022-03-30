import numpy as np
import matplotlib.pyplot as plt

from .parser import HEPHY_HGCAL_parser
import pdb


class CVmeas:
    all_CV = []

    @classmethod
    def intantiate_from_HEPHY_HGCAL(cls, filename, device=None, fmt=None, label=None):
        CV_dict_list = HEPHY_HGCAL_parser.read_CV(filename)
        return [
            CVmeas(
                CV["V"],
                CV["C"],
                CV["freq"],
                CV["mode"],
                CV["filename"],
                device=device,
                fmt=fmt,
                label=label,
            )
            for CV in CV_dict_list
        ]

    def __init__(self, V, C, freq, mode, filename, device=None, fmt=None, label=None):
        # initialize with device name, voltage array, capacitance and measurement frequency
        assert type(V) == np.ndarray, "Voltage array as np.ndarray"
        assert type(C) == np.ndarray, "Voltage array as np.ndarray"
        assert type(freq) == float, "Provide measurement frequency as float"
        assert str.lower(mode) == "s" or mode == "p", "mode is s or p?"
        assert type(filename) == str, "Provide filename as str"

        self.is_negative_V = True if V.mean() < 0 else False
        self.V = V * -1 if self.is_negative_V else V
        self.C = C
        self.freq = freq
        self.mode = str.lower(mode)
        self.filename = filename
        self.device = device
        self.fmt = fmt
        self.label = label if label else f"{self.freq}Hz  {self.mode}"

        CVmeas.all_CV.append(self)

    def C2(self):
        return 1 / self.C ** 2


prefix = {"m": 1e3, "u": 1e6, "n": 1e9, "p": 1e12, "k": 1e-3, "M": 1e-6, "": 1}


def plot_CV(meas_list, Cprefix="p", Clim=[None, None], Vlim=[None, None]):
    fig, ax = plt.subplots()

    for meas in meas_list:
        # change plot scale
        plotC = meas.C * prefix[Cprefix]
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, plotC, fmt, label=meas.label)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"Capacitance [{Cprefix}F]")
    ax.set_xlim(Vlim)
    ax.set_ylim(Clim)
    ax.legend()
    return fig, ax


def plot_C2V(meas_list, C2lim=[None, None], Vlim=[None, None]):
    fig, ax = plt.subplots()

    for meas in meas_list:
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, meas.C2, fmt, label=meas.label)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"$1 / C^2$ [$1/F^2$]")
    ax.set_xlim(Vlim)
    ax.set_ylim(C2lim)
    ax.legend()
    return fig, ax


def show_plots():
    plt.show()
