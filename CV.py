import pandas as pd
import numpy as np
import scipy.signal
import matplotlib.pyplot as plt
import scipy

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
        self.v_depl = None
        self.c2_depl = None

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
                # find common voltage values and corresponding indices
                V_common, CV_ind, CV_open_ind = np.intersect1d(
                    self.V, CV_open.V, return_indices=True
                )
                # new capacitance arrays measured at common voltages
                C_common = self.C[CV_ind]
                C_open_common = CV_open.C[CV_open_ind]
                # subtract open measurement
                C_common = C_common - C_open_common
                # reset array values
                self.C = C_common
                self.V = V_common
                self.is_corrected = True

            else:
                print("Frequencies differ for CV open correction", self.filename)
        if type(CV_open) == float:
            print(self.device.ID, ": Correcting CV open constant value", CV_open)
            self.C = self.C - CV_open
            self.is_corrected = True

    def fit_C2(self, rise_lim, const_lim):
        # provide limits lower and upper: lim=[lower,upper]
        is_rise = (self.V > rise_lim[0]) & (self.V < rise_lim[1])
        is_const = (self.V > const_lim[0]) & (self.V < const_lim[1])
        v_rise = self.V[is_rise]
        v_const = self.V[is_const]
        c_rise = self.C2()[is_rise]
        c_const = self.C2()[is_const]

        (
            slope_rise,
            intercept_rise,
            r_value_rise,
            p_value_rise,
            std_err_rise,
        ) = scipy.stats.linregress(v_rise, c_rise)

        c_rise_fit = utils.line(v_rise, slope_rise, intercept_rise)

        (
            slope_const,
            intercept_const,
            r_value_const,
            p_value_const,
            std_err_const,
        ) = scipy.stats.linregress(v_const, c_const)

        c_const_fit = utils.line(v_const, slope_const, intercept_const)

        v_depl = (intercept_const - intercept_rise) / (slope_rise - slope_const)
        self.v_depl = int(round(v_depl, 0))
        self.c2_depl = utils.line(self.v_depl, slope_rise, intercept_rise)
        self.label = self.label + "  $V_{depl}$" + f" = {self.v_depl} V"

        return (
            self.v_depl,
            self.c2_depl,
            slope_rise,
            intercept_rise,
            slope_const,
            intercept_const,
        )


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
        if meas.v_depl:
            ax.plot(meas.v_depl, meas.c2_depl, "+k", markersize=15)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"$1 / C^2$ [$1/F^2$]")
    ax.set_xlim(Vlim)
    ax.set_ylim(C2lim)
    ax.set_yscale(scale)
    ax.set_xscale(scale)
    ax.legend()
    ax.grid(True)
    return fig, ax
