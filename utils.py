import matplotlib.pyplot as plt

prefix = {
    "m": 1e3,
    "u": 1e6,
    "n": 1e9,
    "p": 1e12,
    "k": 1e-3,
    "M": 1e-6,
    "G": 1e-9,
    "": 1,
}


def show_plots():
    plt.show()


def line(x, slope, offset):
    return slope * x + offset
