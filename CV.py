import pandas as pd
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt

from .Measurement import Measurement
from . import utils
import pdb


class CV(Measurement):
    all_CV = []

    @classmethod
    def get_DataFrame(cls, meas_list=None):
        if not meas_list:
            meas_list = cls.all_CV
        freq = [i.freq for i in meas_list]
        mode = [i.mode for i in meas_list]
        filename = [i.filename for i in meas_list]
        is_open = [i.is_open for i in meas_list]
        df = pd.DataFrame(
            {
                "Filename": filename,
                "Frequency [Hz]": freq,
                "CV-mode": mode,
                "Open measurement": is_open,
                "CV_meas": meas_list,
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

        self.is_corrected = False

        CV.all_CV.append(self)

    def C2(self):
        return 1 / self.C ** 2

    def correct_CV_open(self, CV_open=None, device=None):
        if self.is_open:  # don't correct if self is an open measutement
            return -1
        if (
            not CV_open
        ):  # no measurement or value is provided, find automatically within measurements of the same device
            if not device:  # device can be specified to search for open measurement
                device = self.device
            # same type, frequency and mode (p,s), open measurement
            open_meas = [
                meas
                for meas in device.measurements
                if meas.Type == self.Type
                and meas.freq == self.freq
                and meas.mode == self.mode
                and meas.is_open is True
            ]
            if len(open_meas) != 1:
                print("Open measurement not found.")
            else:
                CV_open = open_meas[0]

        # CV_open can be a CV_meas object or a float value
        # in case of CV_meas object, freq have to be identical
        if type(CV_open) == CV:  # verify type
            if (
                self.freq == CV_open.freq and self.mode == CV_open.mode
            ):  # verify frequency and mode
                if all(self.V == CV_open.V):
                    CV_open = CV_open.C
                else:  # take the mean value if different voltages
                    CV_open = CV_open.C.mean()
                self.C = self.C - CV_open
                self.is_corrected = True

            else:
                print("Frequencies differ for CV open correction", self.filename)
        if type(CV_open) == float:
            self.C = self.C - CV_open
            self.is_corrected = True

    def sandbox(self):
        fig, ax = plt.subplots(figsize=[8, 6])
        y_norm = self.C / np.max(self.C)
        x_norm = self.V / np.max(self.V)
        savgol_windowsize = int(len(self.C) / 30 + 1) * 2 + 1
        spl_dev = scipy.signal.savgol_filter(
            y_norm, window_length=savgol_windowsize, polyorder=1, deriv=1
        )
        # ax.plot(x_norm, y_norm, label="y_norm")
        ax.plot(x_norm, spl_dev, label="spl_dev")
        # dx = [x_norm[i + 1] - x_norm[i] for i in range(len(x_norm) - 1)]
        dx = np.max(x_norm) / len(x_norm)
        grad = np.gradient(np.gradient(y_norm, dx), dx)
        pdb.set_trace()
        ax.plot(x_norm, grad, label="grad")
        ax.legend()

        return fig, ax


def plot_CV(meas_list, Cprefix="p", Clim=[None, None], Vlim=[None, None], **kwargs):
    fig, ax = plt.subplots(figsize=[8, 6])

    for meas in meas_list:
        # change plot scale
        plotC = meas.C * utils.prefix[Cprefix]
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, plotC, fmt, label=meas.label, **kwargs)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"Capacitance [{Cprefix}F]")
    ax.set_xlim(Vlim)
    ax.set_ylim(Clim)
    ax.grid(True)
    ax.legend()
    return fig, ax


def plot_C2V(meas_list, C2lim=[None, None], Vlim=[None, None], scale="log", **kwargs):

    Vlim[0] = 1 if scale == "log" and Vlim[0] == None else Vlim[0]
    C2lim[0] = 1 if scale == "log" and C2lim[0] == None else C2lim[0]

    fig, ax = plt.subplots(figsize=[8, 6])

    for meas in meas_list:
        # check formatter
        fmt = meas.fmt if meas.fmt else "^"
        ax.plot(meas.V, meas.C2(), fmt, label=meas.label, **kwargs)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"$1 / C^2$ [$1/F^2$]")
    ax.set_xlim(Vlim)
    ax.set_ylim(C2lim)
    ax.set_yscale(scale)
    ax.set_xscale(scale)
    ax.grid(True)
    ax.legend()
    return fig, ax
