#!/usr/bin/env python3

#6.1.2021, mw
#check guard ring current vs. pad current for irradiated LGADs, calculate alpha
import sys
print(sys.version)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import SSDanalysis.modules.IVparser as IVp
import helper as hp
'''
############### LGAD
sensorname='LGAD W5_I3_1'
M80=3.5#multiplication factor for 80min, obtained from e.g. TCT
#IV, Ana, -20C, 1E14, p, 80min, probestation
ref=hp.replacehome('~/cernbox/data/IVCV/MW_LGAD_8622_W5_I3_1/LGAD_8622_W5_I3_1_2017-12-05_1.iv')
#IV, MW, -20C, 1E14, p, Susi
myfilepath=hp.replacehome('~/cernbox/data/IVCV/MW_LGAD_8622_W5_I3_1/')
myfilelist=[
    'MW_LGAD_8622_W5_I3_1_2018-05-18_1.iv',#80min
    'MW_LGAD_8622_W5_I3_1_2018-06-15_1.iv',#240min
    'MW_LGAD_8622_W5_I3_1_2018-07-11_1.iv',#560min
    'MW_LGAD_8622_W5_I3_1_2018-09-06_1.iv',#1200min
    'MW_LGAD_8622_W5_I3_1_2018-09-09_1.iv',#2480min
    'MW_LGAD_8622_W5_I3_1_2018-11-16_1.iv'#5040min
    ]
####################################################
'''
################### PIN
sensorname='PIN W5_E3_4'
M80=1.5
#IV, Ana, -20C, 1E14, p, 80min, probestation
ref=hp.replacehome('~/cernbox/data/IVCV/MW_PIN_8622_W5_E3_4/PIN_8622_W5_E3_4_2017-12-05_1.iv')
#IV, MW, -20C, 1E14, p, Susi
myfilepath=hp.replacehome('~/cernbox/data/IVCV/MW_PIN_8622_W5_E3_4/')
myfilelist=[
    'MW_PIN_8622_W5_E3_4_2018-05-16_1.iv',#80min
    'MW_PIN_8622_W5_E3_4_2018-05-17_1.iv',#240min
    'MW_PIN_8622_W5_E3_4_2018-07-10_1.iv',#560min
    'MW_PIN_8622_W5_E3_4_2018-09-05_1.iv',#1200min
    'MW_PIN_8622_W5_E3_4_2018-09-08_1.iv',#2480min
    'MW_PIN_8622_W5_E3_4_2018-11-03_1.iv'#5040min
    ]
###########################
#'''
t_annealing=[80.,240.,560.,1200.,2480.,5040.]
voltages=np.array([150.,200.,250.,300.,350.,400])

#scaling F=Itot/Ipad used in paper were F=1.41 for LGADs and F=[2.06,2.11,2.16,2.20,2.25,2.28]
thickness=277e-4#value in cm #value by Salva per mail from 14.1.20 for sensors from 8622
surface=(3.*3)/100#value in cm^2
Vpad=thickness*surface #in cm^3
phi=1.e+14 #neq/cm^2

header_ref,data_ref=IVp.IVparser(ref)

#list of [(header,data),..]
datatupel=list(map(IVp.IVparser,[myfilepath+i for i in myfilelist]))

for header,data in datatupel:
    header,data=IVp.alphacalc(header,data,phi,Vpad)

reffactor=[]#F
alphalist=[]#alpha value at respective bias voltage
for i,volt in enumerate(voltages):#get corresponding values at voltages at annealing times
#    reffactor.append(data_ref['Total/Pad'][-1*data_ref['bias [V]'] == volt])#this uses ref(tot)/ref(pad) better would be: sensor80(tot)/ref(pad)
    I80_tot_floating=datatupel[0][1]['Total Current [A]'][-1*datatupel[0][1]['bias [V]'] == volt]#sensor80(tot)/ref(pad)
    I80_pad_connected=data_ref['Pad Current [A]'][-1*data_ref['bias [V]'] == volt]#sensor80(tot)/ref(pad)
    reffactor.append(I80_tot_floating/I80_pad_connected)#sensor80(tot)/ref(pad)
    alphalist.append(datatupel[i][1]['alpha [A/cm]'][-1*datatupel[i][1]['bias [V]']==volt])
reffactor=np.array(reffactor)
print('scaling factor F')
print(reffactor)
alphalist=np.array(alphalist)
    
#old alpha calculation with scaling factor
alpha_old=alphalist/reffactor#scaling by F

##calculation of corrected alpha value with new formula
F80=reffactor[0]
corr=np.array([hp.Tscale(hp.alpha([t]),20,-20)*M80*(F80-1) for t in t_annealing])
alpha_new=alphalist-corr

alpha_theory_x=np.linspace(40,5100,1000)
alpha_theory_y=[hp.alpha([t]) for t in alpha_theory_x]
alpha_theory_y=np.array(list(map(lambda x:hp.Tscale(x,20,-20),alpha_theory_y)))#Tscale theory
alpha_theory_y=M80*alpha_theory_y#scaling by gain

fig,ax=plt.subplots(figsize=[8,8])
ax.plot(alpha_theory_x,alpha_theory_y,'k--',label='Theory x '+str(M80))
ax.plot(t_annealing,alpha_old,'k^',linestyle='',label=sensorname)
ax.plot(t_annealing,alpha_new,'rv',linestyle='',label=sensorname+' unbiased')
ax.set_xscale('log')
ax.legend(loc='upper right')
ax.set_xlabel('Annealing time at 60C [min]')
ax.set_ylabel('Current related damage rate [A/cm]')

plt.show()

