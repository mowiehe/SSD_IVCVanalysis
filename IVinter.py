import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from . import utils
from .Measurement import Measurement
import pdb


class IVinter(Measurement):
    all_IVinter = []

    @classmethod
    def get_DataFrame(cls):
        temp = [i.T for i in cls.all_IVinter]
        filename = [i.filename for i in cls.all_IVinter]
        df = pd.DataFrame(
            {
                "Filename": filename,
                "Temperature": temp,
                "IVinter_meas": cls.all_IVinter,
            }
        )
        return df

    def __init__(self, V, R, dR, Chi2, filename, T, device=None, fmt=None, label=None):
        super().__init__(filename, T, device, fmt, label)
        # initialize with device name, voltage array, capacitance and measurement frequency
        assert type(V) == np.ndarray, "Voltage array as np.ndarray"
        assert type(R) == np.ndarray, "Resistance array as np.ndarray"
        assert type(dR) == np.ndarray, "Resistance error array as np.ndarray"
        assert type(Chi2) == np.ndarray, "Chi2 array as np.ndarray"
        assert type(T) == float, "Provide measurement temperature (C) as float"

        self.is_negative_V = True if V.mean() < 0 else False
        self.V = V * -1 if self.is_negative_V else V
        self.R = R
        self.dR = dR
        self.Chi2 = Chi2
        self.label = self.label if self.label else f"{self.T}C"

        IVinter.all_IVinter.append(self)


def plot_IVinter(
    meas_list, Rprefix="M", Rlim=[None, None], Vlim=[None, None], **kwargs
):
    fig, ax = plt.subplots(figsize=[8, 6])

    for meas in meas_list:
        # change plot scale
        plotR = meas.R * utils.prefix[Rprefix]
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, plotR, fmt, label=meas.label, **kwargs)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"Interpad resistance [{Rprefix}Ohm]")
    ax.set_xlim(Vlim)
    ax.set_ylim(Rlim)
    ax.grid(True)
    ax.legend()
    return fig, ax
