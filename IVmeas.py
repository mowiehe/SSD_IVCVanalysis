import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import utils
from .parser import HEPHY_HGCAL_parser
import pdb


class IVmeas:
    all_IV = []

    @classmethod
    def intantiate_from_HEPHY_HGCAL(
        cls, filename, T, device=None, fmt=None, label=None
    ):
        IV_dict = HEPHY_HGCAL_parser.read_IV(filename)
        IV = IVmeas(
            IV_dict["V"],
            IV_dict["I"],
            T,
            IV_dict["filename"],
            device=device,
            fmt=fmt,
            label=label,
        )
        return IV

    @classmethod
    def get_DataFrame(cls):
        temp = [i.T for i in cls.all_IV]
        filename = [i.filename for i in cls.all_IV]
        df = pd.DataFrame(
            {
                "Filename": filename,
                "Temperature": temp,
                "IV_meas": cls.all_IV,
            }
        )
        return df

    def __init__(self, V, I, T, filename, device=None, fmt=None, label=None):
        # initialize with device name, voltage array, capacitance and measurement frequency
        assert type(V) == np.ndarray, "Voltage array as np.ndarray"
        assert type(I) == np.ndarray, "Current array as np.ndarray"
        assert type(T) == float, "Provide measurement temperature (C) as float"
        assert type(filename) == str, "Provide filename as str"

        self.is_negative_V = True if V.mean() < 0 else False
        self.V = V * -1 if self.is_negative_V else V
        self.I = I * -1 if self.is_negative_V else I
        self.T = T
        self.filename = filename
        self.device = device
        self.fmt = fmt
        self.label = label if label else f"{self.T}C"

        IVmeas.all_IV.append(self)


def plot_IV(meas_list, Iprefix="u", Ilim=[None, None], Vlim=[None, None]):
    fig, ax = plt.subplots()

    for meas in meas_list:
        # change plot scale
        plotI = meas.I * utils.prefix[Iprefix]
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, plotI, fmt, label=meas.label)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"Leakage current [{Iprefix}A]")
    ax.set_xlim(Vlim)
    ax.set_ylim(Ilim)
    ax.legend()
    return fig, ax
