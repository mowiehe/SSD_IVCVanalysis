import numpy as np
from SSD_IVCVanalysis.CVmeas import CVmeas, plot_CV, plot_C2V, show_plots

frequency = 1e3
volt = np.arange(100) * -1
cap = 1 / (np.sqrt(abs(volt)) + 0.5)
cap = np.where(abs(volt) < 50, 1 / (np.sqrt(abs(volt)) + 0.5), 1 / (np.sqrt(50) + 0.5))

myCV = CVmeas(volt, cap, frequency, CVmode="s", label="Meas1", fmt="^k")
fig, ax = plot_CV([myCV], Cprefix="")
fig, ax = plot_C2V([myCV])
show_plots()
