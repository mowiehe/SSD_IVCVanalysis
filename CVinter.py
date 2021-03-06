import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from . import utils
from .Measurement import Measurement
import pdb


class CVinter(Measurement):
    all_CVinter = []

    @classmethod
    def get_DataFrame(cls, meas_list=None):
        if not meas_list:
            meas_list = cls.all_CVinter
        freq = [i.freq for i in meas_list]
        filename = [i.filename for i in meas_list]
        is_open = [i.is_open for i in meas_list]
        df = pd.DataFrame(
            {
                "Filename": filename,
                "Frequency [Hz]": freq,
                "Open measurement": is_open,
                "CVinter_meas": meas_list,
            }
        )
        return df

    def __init__(
        self, V, C, dC, freq, filename, T, is_open, device=None, fmt=None, label=None
    ):
        super().__init__(filename, T, device, fmt, label)
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

        self.is_corrected = False

        CVinter.all_CVinter.append(self)

    def correct_CVinter_open(self, CVinter_open=None, device=None):
        if self.is_open:  # don't correct if self is an open measutement
            return -1
        if not CVinter_open:
            # no measurement or value is provided, find automatically within measurements of the same device
            if not device:
                # device can be specified to search for open measurement
                device = self.device
            # same type, frequency and mode (p,s), open measurement
            open_meas = [
                meas
                for meas in device.measurements
                if meas.Type == self.Type
                and meas.freq == self.freq
                and meas.is_open is True
            ]
            if len(open_meas) != 1:
                print("Open measurement not found.")
            else:
                CVinter_open = open_meas[0]

        # CVinter_open can be a CVinter_meas object or a float value
        # in case of CVinter_meas object, freq have to be identical
        if type(CVinter_open) == CVinter:
            if self.freq == CVinter_open.freq:

                # find common voltage values and corresponding indices
                V_common, CV_ind, CV_open_ind = np.intersect1d(
                    self.V, CVinter_open.V, return_indices=True
                )
                # new capacitance arrays measured at common voltages
                C_common = self.C[CV_ind]
                C_open_common = CVinter_open.C[CV_open_ind]
                # subtract open measurement
                C_common = C_common - C_open_common
                # reset array values
                self.C = C_common
                self.V = V_common
                self.is_corrected = True

            else:
                print("Frequencies differ for CVinter open correction", self.filename)
        if type(CVinter_open) == float:
            self.C = self.C - CVinter_open
            self.is_corrected = True


def plot_CVinter(
    meas_list, Cprefix="p", Clim=[None, None], Vlim=[None, None], **kwargs
):
    fig, ax = plt.subplots(figsize=[8, 6])

    for meas in meas_list:
        # change plot scale
        plotC = meas.C * utils.prefix[Cprefix]
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, plotC, fmt, label=meas.label, **kwargs)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"Interpad capacitance [{Cprefix}F]")
    ax.set_xlim(Vlim)
    ax.set_ylim(Clim)
    ax.grid(True)
    ax.legend()
    return fig, ax
