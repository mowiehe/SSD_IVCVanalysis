import ROOT as rt
import pandas as pd
import numpy as np
import helper as hp

from . import utils
from .Measurement import Measurement

hp.set_CLICdpStyle()


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
    Ilim=None,
    Vlim=None,
    log=True,
    normalize=False,
    draw="L",
    colors=[1, 2, 3, 4],
    markers=[21, 22, 23, 24],
    leg_loc=[0.2, 0.8, 0.6, 0.85],
):
    c = rt.TCanvas("c_IV", "c_IV", 800, 800)
    g_list = []
    if log:
        c.SetLogy()
    c.SetGridx()
    c.SetGridy()
    leg = rt.TLegend(leg_loc[0], leg_loc[1], leg_loc[2], leg_loc[3])

    for i, meas in enumerate(meas_list):
        if normalize:
            plotI = meas.I_norm()
        else:
            plotI = meas.I

        plotI = plotI * utils.prefix[Iprefix]
        g = rt.TGraph(len(meas.V), meas.V, plotI)
        g.SetLineColor(colors[i % len(colors)])
        g.SetMarkerColor(colors[i % len(colors)])
        g.SetMarkerStyle(markers[i % len(markers)])
        if Vlim:
            g.GetXaxis().SetRangeUser(Vlim[0], Vlim[1])
        if Ilim:
            g.GetYaxis().SetRangeUser(Ilim[0], Ilim[1])
        if normalize:
            g.SetTitle(
                meas.label
                + f";Bias voltage [V];fLeakage current per unit-volume [{Iprefix}A/cm^{3}]"
            )
        else:
            g.SetTitle(meas.label + f";Bias voltage [V];Leakage current [{Iprefix}A]")
        g.Draw(f"A{draw}" if i == 0 else f"{draw} SAME")
        g_list.append(g)
        leg.AddEntry(g, meas.label, draw)
    leg.Draw("same")

    return c, g_list, leg
