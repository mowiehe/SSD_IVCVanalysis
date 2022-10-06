import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from . import utils
from .Measurement import Measurement
import pdb


class IV(Measurement):
    all_IV = []

    @classmethod
    def get_DataFrame(cls, meas_list=None):
        if not meas_list:
            meas_list = cls.all_IV
        temp = [i.T for i in meas_list]
        filename = [i.filename for i in meas_list]
        df = pd.DataFrame(
            {
                "Filename": filename,
                "Temperature": temp,
                "IV_meas": meas_list,
            }
        )
        return df

    def __init__(self, V, I, filename, T, device=None, fmt=None, label=None):
        super().__init__(filename, T, device, fmt, label)
        # initialize with device name, voltage array, capacitance and measurement frequency
        assert type(V) == np.ndarray, "Voltage array as np.ndarray"
        assert type(I) == np.ndarray, "Current array as np.ndarray"
        assert type(T) == float, "Provide measurement temperature (C) as float"

        self.is_negative_V = True if V.mean() < 0 else False
        self.V = V * -1 if self.is_negative_V else V
        self.I = I * -1 if self.is_negative_V else I
        self.label = self.label if self.label else f"{self.T}C"

        IV.all_IV.append(self)

    def I_norm(self):
        # get current normalized by volume
        return self.I / (self.device.area * self.device.thickness)


def plot_IV(
    meas_list,
    Iprefix="u",
    Ilim=[None, None],
    Vlim=[None, None],
    log="True",
    normalize=False,
    **kwargs,
):
    Ilim[0] = 1 if log and Ilim[0] == None else Ilim[0]
    fig, ax = plt.subplots(figsize=[8, 6])

    for meas in meas_list:
        if normalize:
            plotI = meas.I_norm()
        else:
            plotI = meas.I
        # change plot scale
        plotI = plotI * utils.prefix[Iprefix]
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, plotI, fmt, label=meas.label, **kwargs)
    ax.set_xlabel("Bias voltage [V]")
    if normalize:
        ax.set_ylabel(f"Leakage current per unit-volume [{Iprefix}A/cm$^3$]")
    else:
        ax.set_ylabel(f"Leakage current [{Iprefix}A]")
    ax.set_xlim(Vlim)
    ax.set_ylim(Ilim)
    if log:
        ax.set_yscale("log")
    ax.grid(True)
    ax.legend()
    return fig, ax
