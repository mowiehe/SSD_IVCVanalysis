import numpy as np
import pandas as pd
import pdb


def read_CV(filename):
    # one CV instance per frequency and s- p-mode
    meas_type, header, df_single = parse_measurement_file(filename)
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
