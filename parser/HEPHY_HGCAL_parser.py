import numpy as np
import pandas as pd
import pdb

from SSD_IVCVanalysis.IV import IV
from SSD_IVCVanalysis.CV import CV
from SSD_IVCVanalysis.IVinter import IVinter
from SSD_IVCVanalysis.CVinter import CVinter


def read_CV(filename):
    # one CV instance per frequency and s- p-mode
    meas_type, header, df_single = parse_measurement_file(filename)
    if meas_type != "Single CV":
        return -1
    frequencies = df_single.loc[:, "Freq [Hz]"].drop_duplicates()
    CV_list = []

    for freq in frequencies:
        for mode in ["s", "p"]:
            # obtains data from dataframe and stores to individual arrays
            df = df_single.loc[df_single["Freq [Hz]"] == freq]

            if mode == "p":
                C = np.array(df["Cp [F]"])
            elif mode == "s":
                C = np.array(df["Cs [F]"])
            else:
                print("CV mode not understood, p or s")
            V = np.array(df["Nominal Voltage [V]"])
            # R = np.array(df_single["R [Ohm]"])
            # create CV dict
            CV = {
                "V": V,
                "C": C,
                "freq": freq,
                "mode": mode,
                "filename": filename,
            }
            CV_list.append(CV)

    return CV_list


def read_IV(filename):
    meas_type, header, df_single = parse_measurement_file(filename)
    if meas_type != "Single IV":
        return -1
    I = np.array(df_single["Current [A]"])
    V = np.array(df_single["Nominal Voltage [V]"])

    return {"V": V, "I": I, "filename": filename}


def read_IVinter(filename):
    # obtains data from dataframe and stores to individual arraysy
    meas_type, header, df_single = parse_measurement_file(filename)
    if meas_type != "Interpad R":
        return -1

    df_red = df_single.loc[
        :,
        [
            "Bias Voltage[V]",
            "Resistance (polynom fit) [Ohm]",
            "dR (fit) [Ohm]",
            "Chi2 of Fit [-]",
        ],
    ].drop_duplicates(
        ignore_index=True
    )  # reduce dataframe to significant values, drop interpad measurement, keep fit result per bias voltage
    V = np.array(df_red["Bias Voltage[V]"])
    R = np.array(df_red["Resistance (polynom fit) [Ohm]"])
    dR = np.array(df_red["dR (fit) [Ohm]"])
    Chi2 = np.array(df_red["Chi2 of Fit [-]"])
    return {"V": V, "R": R, "dR": dR, "Chi2": Chi2, "filename": filename}


def read_CVinter(filename):
    meas_type, header, df_single = parse_measurement_file(filename)
    if meas_type != "Interpad C":
        return -1
    frequencies = df_single.loc[:, "Frequency [Hz]"].drop_duplicates()
    CVinter_list = []

    for freq in frequencies:
        df = df_single.loc[df_single["Frequency [Hz]"] == freq]
        V = np.array(df["Nominal Voltage [V]"])
        C = np.array(df["Cp [F]"])
        dC = np.array(df["Cp_Err [F]"])
        # R = np.array(df["Rp [Ohm]"])
        CVinter = {
            "V": V,
            "C": C,
            "dC": dC,
            "freq": freq,
            "filename": filename,
        }
        CVinter_list.append(CVinter)

    return CVinter_list


## from parse_functions.py in HGCAL_strip_analysis
def parse_measurement_file(filename):
    # parses a measurement file of arbitrary type from the HGC strip measurements
    # data is stored in a dataframe
    print("Reading file", filename)
    header = []
    with open(filename) as fin:
        for line in fin:
            if not line.startswith("#"):  # only read header
                break
            header.append(line.strip()[2:])  # remove # and trailing \n
    meas_type = header[0]
    columns = [
        i.strip() for i in header[-1].split("\t")
    ]  # last row of header are column names

    df_single = pd.read_csv(filename, comment="#", delimiter="\t", names=columns)

    return meas_type, header, df_single


def instantiate_measurement(filename, T, is_open, device=None, fmt=None, label=None):
    meas_type, _, _ = parse_measurement_file(filename)
    if meas_type == "Single IV":
        meas = IV.instantiate_from_HEPHY_HGCAL(filename, T, device, fmt, label)
    if meas_type == "Single CV":
        meas = CV.instantiate_from_HEPHY_HGCAL(filename, is_open, device, fmt, label)
    if meas_type == "Interpad R":
        meas = IVinter.instantiate_from_HEPHY_HGCAL(filename, T, device, fmt, label)
    if meas_type == "Interpad C":
        meas = CVinter.instantiate_from_HEPHY_HGCAL(
            filename, is_open, device, fmt, label
        )

    return meas
