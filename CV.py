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
        self.is_fit = False

        CV.all_CV.append(self)

    def C2(self):
        return 1 / self.C**2

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
        c2_rise = self.C2()[is_rise]
        c2_const = self.C2()[is_const]
        self.c_end = np.mean(self.C[is_const])

        (
            slope_rise,
            intercept_rise,
            r_value_rise,
            p_value_rise,
            std_err_rise,
        ) = scipy.stats.linregress(v_rise, c2_rise)

        self.v_rise_fit = v_rise
        self.c2_rise_fit = utils.line(self.v_rise_fit, slope_rise, intercept_rise)

        (
            slope_const,
            intercept_const,
            r_value_const,
            p_value_const,
            std_err_const,
        ) = scipy.stats.linregress(v_const, c2_const)

        self.v_const_fit = v_const
        self.c2_const_fit = utils.line(self.v_const_fit, slope_const, intercept_const)

        v_depl = (intercept_const - intercept_rise) / (slope_rise - slope_const)
        self.v_depl = round(v_depl, 2)
        self.c2_depl = utils.line(self.v_depl, slope_rise, intercept_rise)

        self.is_fit = True

        return (
            self.v_depl,
            self.c2_depl,
            slope_rise,
            intercept_rise,
            slope_const,
            intercept_const,
        )

    def W(self, index):
        # return the depletion depth [in µm] based on capacitance and surface area [in cm^2]
        return (
            1e4 * utils.constants.perm * self.device.area / self.C[index]
        )  # 1E4 to convert to um

    def dCdV(self, index):
        dCdV = []
        # calculate left and right slopes and average
        if index != 0:
            dCdV.append(
                (self.C[index] - self.C[index - 1])
                / (self.V[index] - self.V[index - 1])
            )
        if index != len(self.V) - 1:
            dCdV.append(
                (self.C[index + 1] - self.C[index])
                / (self.V[index + 1] - self.V[index])
            )
        return np.mean(dCdV)

    def Neff_index(self, index):  # 1/cm^3
        #         #calculation of net impurity concentration and depth, taken from The electrical characterization of semiconductors, Blood, with help from Esteban, 13.8.2020
        #         #N(x)=-C^3/(epsilon*e*A^2)*(dC/dV)^-1
        #         #x= epsilon*A/C

        # if self.dCdV(index)==0: dCdV=1e-15 #avoid division by zero
        # else: dCdV=self.dCdV(index)

        Neff = -self.C[index] ** 3 / (
            utils.constants.perm
            * utils.constants.q_el
            * self.device.area**2
            * self.dCdV(index)
        )
        return Neff

    def Neff(self):
        epsilon = utils.constants.perm  # F/cm
        q = utils.constants.q_el  # C
        area = self.device.area  # cm^2
        Cend = self.c_end  # F
        Vdep = self.v_depl

        return 2 * Cend**2 * Vdep / (area**2 * epsilon * q)

    def print_info(self):
        super().print_info()
        print("Frequency [Hz]:", self.freq, ", mode:", self.mode)


def plot_CV(
    meas_list,
    Cprefix="p",
    Clim=[None, None],
    Vlim=[None, None],
    log=False,
    fmt="^",
    leg_title=None,
    **kwargs,
):
    fig, ax = plt.subplots()

    Vlim[0] = 1 if log and Vlim[0] is None else Vlim[0]
    Clim[0] = 1 if log and Clim[0] is None else Clim[0]

    for meas in meas_list:
        # change plot scale
        plotC = meas.C * utils.prefix[Cprefix]
        # check formatter
        fmt = meas.fmt if meas.fmt else fmt
        ax.plot(meas.V, plotC, fmt, label=meas.label, **kwargs)
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel(f"Capacitance [{Cprefix}F]")
    ax.set_xlim(Vlim)
    ax.set_ylim(Clim)
    if log:
        ax.set_yscale("log")
        ax.set_xscale("log")
    ax.grid(True)
    ax.legend(title=leg_title)
    return fig, ax


def plot_C2V(
    meas_list,
    C2lim=[None, None],
    Vlim=[None, None],
    log=True,
    fmt="^",
    show_fit=False,
    leg_title=None,
    **kwargs,
):

    Vlim[0] = 1 if log and Vlim[0] is None else Vlim[0]
    C2lim[0] = 1 if log and C2lim[0] is None else C2lim[0]

    fig, ax = plt.subplots()

    for meas in meas_list:
        # check formatter
        label = meas.label
        if meas.is_fit and show_fit:  # update label
            label = (
                meas.label
                + "\n  $V_{depl}$"
                + f" = {meas.v_depl} V"
                + ",  $N_{eff}$"
                + f" = {meas.Neff():.2e}"
                + " $cm^{-3}$"
            )
        fmt = meas.fmt if meas.fmt else fmt
        # plot data
        ax.plot(meas.V, meas.C2(), fmt, label=label, **kwargs)
        if meas.is_fit and show_fit:  # plot lines
            ax.plot(meas.v_depl, meas.c2_depl, "+k", markersize=15)
            ax.plot(meas.v_rise_fit, meas.c2_rise_fit, "r--")
            ax.plot(meas.v_const_fit, meas.c2_const_fit, "r--")
    ax.set_xlabel("Bias voltage [V]")
    ax.set_ylabel("$1 / C^2$ [$1/F^2$]")
    ax.set_xlim(Vlim)
    ax.set_ylim(C2lim)
    if log:
        ax.set_yscale("log")
        ax.set_xscale("log")
    ax.legend(title=leg_title)
    ax.grid(True)
    return fig, ax


def plot_Neff(
    meas_list,
    Nefflim=[None, None],
    Wlim=[None, None],
    fmt="^",
    leg_title=None,
    **kwargs,
):

    Nefflim[0] = 1 if Nefflim[0] is None else Nefflim[0]

    fig, ax = plt.subplots()

    for meas in meas_list:
        Neff = [meas.Neff_index(i) for i in range(len(meas.V))]
        W = [meas.W(i) for i in range(len(meas.V))]
        # check formatter
        fmt = meas.fmt if meas.fmt else fmt

        ax.plot(W, Neff, fmt, label=meas.label, **kwargs)

    ax.set_xlabel("Depth [µm]")
    ax.set_ylabel("N$_{eff}$ [$1/cm^3$]")
    ax.set_xlim(Wlim)
    ax.set_ylim(Nefflim)
    ax.set_yscale("log")
    ax.legend(title=leg_title)
    ax.grid(True)
    return fig, ax
