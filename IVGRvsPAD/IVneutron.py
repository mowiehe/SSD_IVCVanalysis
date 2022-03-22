#!/usr/bin/env python3

#8.1.2021, mw
#check guard ring current vs. pad current for neutron irradiated LGADs
import sys
print(sys.version)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import SSDanalysis.modules.IVparser as IVp
import helper as hp

path=hp.replacehome('~/cernbox/data/IVCV/')

filelist=[
    'PIN_8622_W2_E3_4/PIN_8622_W2_E3_4_2020-12-10_1.iv',#-20C, 1e13 n
    'PIN_8622_W2_I8_1/PIN_8622_W2_I8_1_2020-12-02_1.iv',#-20C, 4e14 n
    'LGAD_8622_W5_C2_3/LGAD_8622_W5_C2_3_2020-12-10_1.iv',#-20C, 1e13 n
    'LGAD_8622_W2_I3_1/LGAD_8622_W2_I3_1_2020-12-01_1.iv',#-20C, 4e14 n
    'LGAD_8622_W5_H2_1/LGAD_8622_W5_H2_1_2020-12-07_1.iv',#-20C, 1.5e15 n
    ]
labels=['PIN 1e13 n','PIN 4e14 n','LGAD 1e13 n','LGAD 4e14 n','LGAD 1.5e15 n']
colors=['k','b','r','g','m']

filelist=[path+i for i in filelist]

fig,ax=plt.subplots(2,figsize=[8,8])

pol=-1
for imyfile,myfile in enumerate(filelist):
    header,data=IVp.IVparser(myfile)
    data=data.iloc[1:-1]
    ax[0].plot(pol*data['bias [V]'],pol*data['Total Current [A]'],colors[imyfile],label=labels[imyfile])
    ax[0].plot(pol*data['bias [V]'],pol*data['Pad Current [A]'],colors[imyfile],linestyle='--')

    ax[1].plot(-1*data['bias [V]'],data['Total/Pad'],colors[imyfile],label=labels[imyfile])

ax[1].set_xlabel('Bias voltage [V]')
ax[1].set_ylabel('Ratio total/pad')
    
ax[0].set_xlabel('Bias voltage [V]')
ax[0].set_ylabel('Current [A]')
ax[0].legend(loc='upper left')
