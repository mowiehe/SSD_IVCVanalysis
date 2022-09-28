# 10.2.2021, mw, updated 28/09/2022
# functions common to all parsing modules

import pandas as pd
import numpy as np

from SSD_IVCVanalysis.IV import IV
from SSD_IVCVanalysis.CV import CV


def parser(filename):
    header = {}
    filecontent = []
    data = pd.DataFrame()
    readData = False
    with open(filename, "r") as reader:
        filecontent = reader.readlines()
    if "IV with two I-meter" in filecontent[0]:
        meas_type = "Single IV"
    if "CV measurement" in filecontent[0]:
        meas_type = "Single CV"
    for i, line in enumerate(filecontent):
        if line[0] == ":":
            header_label = line[1:-1]
            j = 1
            header_entry = []
            while filecontent[i + j][0] != ":" and "BEGIN" not in filecontent[i + j]:
                header_entry.append(filecontent[i + j][:-1])
                j += 1
            header[
                header_label
            ] = header_entry  # bug: only reads first line of each header entry
        if "BEGIN" in line:
            header["legend"] = header["legend"][0].split(
                "\t"
            )  # this defines the DF columns
            readData = True
            continue
        if "END" in line:
            readData = False
            break
        if readData:
            line = line[:-1].split("\t")  # delete end of line and split in tab
            if len(line) != len(header["legend"]):
                print("Error in number of columns!")
                break
            row = pd.DataFrame(
                {header["legend"][col]: float(line[col]) for col in range(len(line))},
                index=[0],
            )
            data = pd.concat([data, row], ignore_index=True)
    ##
    ##adfjust for older versions
    if header["Program Version"][0].split(",")[-1] == " 6.2011 Gabrysch":
        header["Sample"] = header.pop("device")
    return meas_type, header, data


def instantiate_measurement(filename, device=None, fmt=None, label=None):
    # user function, input is filename, output is measurement object
    print("Parsing file", filename)
    meas_type, _, _ = parser(filename)
    if meas_type == "Single IV":
        meas = instantiate_IV(filename, device, fmt, label)
    if meas_type == "Single CV":
        meas = instantiate_CV(filename, device, fmt, label)

    return meas


def instantiate_IV(filename, device=None, fmt=None, label=None):
    # convert IV dict to IV class object
    IV_dict = read_IV(filename)
    return IV(
        IV_dict["V"],
        IV_dict["I"],
        IV_dict["filename"],
        T=IV_dict["T"],
        device=device,
        fmt=fmt,
        label=label,
    )


def read_IV(filename):
    meas_type, header, df_single = parser(filename)
    if meas_type != "Single IV":
        return -1
    I = np.array(df_single["Pad Current [A]"])
    V = np.array(df_single["bias [V]"])
    T = float(header["temperature [C]"][0])

    return {"V": V, "I": I, "T": T, "filename": filename}


def instantiate_CV(filename, device=None, fmt=None, label=None):
    CV_dict = read_CV(filename)
    return CV(
        CV_dict["V"],
        CV_dict["C"],
        CV_dict["freq"],
        CV_dict["mode"],
        CV_dict["filename"],
        T=CV_dict["T"],
        is_open=False,
        device=device,
        fmt=fmt,
        label=label,
    )


def read_CV(filename):
    # one CV instance per frequency and s- p-mode
    meas_type, header, df = parser(filename)
    if meas_type != "Single CV":
        return -1

    # obtains data from dataframe and stores to individual arrays
    C = np.array(df["Capacitance [F]"])
    V = np.array(df["V_detector [V]"])
    T = float(header["temperature[C]"][0])
    freq = float([x for x in header["Instruments"] if "Frequency" in x][0].split()[2])
    # create CV dict
    CV = {
        "V": V,
        "C": C,
        "T": T,
        "freq": freq,
        "mode": "p",
        "filename": filename,
    }
    return CV
