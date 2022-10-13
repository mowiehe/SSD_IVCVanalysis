#! /usr/bin/env python

import math

perm = (
    11.68 * 8.854187e-14
)  # F/cm permittivity, rel.per.Silicon times vacuum permittivity
q_el = 1.602e-19  # electron charge [C]
kB = 8.617333262145e-5  # eV/K
hbar_Js = 1.054571817 * 10**-34  # Js
hbar_eVs = 6.582119569 * 10**-16  # eVs
c = 299792458.0  # m/s


def lambda2omega(x, n=1):
    # circular frequency
    return 2 * math.pi * c / (n * x)


def nm2eV(x, n=1):
    # conversion between wavelength in nm and photon energy in eV
    return lambda2omega(x * 1e-9, n) * hbar_eVs


def eV2nm(x, n=1):
    return nm2eV(x, n)


def nJ2eV(nJ):
    return 6.24150974e18 * nJ * 1e-9


def mW2nJ(mW, freq):
    return mW * 1e-3 / freq * 1e9


def V2fC(V, gain=12.5):
    return (
        V * 1000 / gain
    )  # convert to fC. standard g=12.5mV/fC (Cividec charge amplifier)


def C2K(C):
    return C + 273.15
