#!/usr/bin/env python3

#8.1.2021, mw
#compare currents from Ana
import sys
print(sys.version)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import SSDanalysis.modules.IVparser as IVp
import helper as hp
import plotsbox.filelist as fl

keys=[
    'PIN_8622_W5_E3_4_2017-12-05_1.iv',#Ana
    'MW_PIN_8622_W5_E3_4_2018-05-16_1.iv',#MW
    'LGAD_8622_W5_E3_1_2017-12-05_1.iv',#Ana
    'MW_LGAD_8622_W5_E3_1_2018-05-18_1.iv',#MW
    'LGAD_8622_W5_I3_1_2017-12-05_1.iv',#Ana
    'MW_LGAD_8622_W5_I3_1_2018-05-18_1.iv'#MW
    ]

#keys=keys[:2]
#keys=keys[2:4]
keys=keys[4:]

def getFile(key):
    info=fl.filelist[key]
    myfile=hp.replacehome(info['path_to'])+info['filename']
    header,data=IVp.IVparser(myfile)
    data=data.iloc[1:-1]
    environment=info['measby'].replace('Ana','gr connected')
    environment=environment.replace('MW','gr floating')
    return header,data,info,environment

fig,ax=plt.subplots(2,figsize=[8,8])
for ikey,key in enumerate(keys):
    header,data,info,environment=getFile(key)
    ax[0].plot(-1*data['bias [V]'],-1*data['Total Current [A]'],label=environment+' tot')
    ax[0].plot(-1*data['bias [V]'],-1*data['Pad Current [A]'],linestyle='--',label=environment+' pad')
    ax[0].set_title(info['sensorname'])
    ax[1].plot(-1*data['bias [V]'],data['Total Current [A]']/data['Pad Current [A]'],label=environment)

ax[0].set_xlabel('Bias voltage [V]')
ax[0].set_ylabel('Current [A]')
ax[0].legend(loc='upper left')
ax[1].set_xlabel('Bias voltage [V]')
ax[1].set_ylabel('Total/Pad current')
ax[1].legend(loc='upper left')

##second plot, try to scale current
fig2,ax2=plt.subplots(figsize=[8,8])

header_ref,data_ref,info_ref,environment_ref=getFile(keys[0])
header_MW,data_MW,info_MW,environment_MW=getFile(keys[1])
data_ref.set_index('bias [V]',drop=False,inplace=True)
data_MW.set_index('bias [V]',drop=False,inplace=True)
data_MW['F']=data_ref['Total/Pad']#this is what was done in the paper
data_MW['F']=data_MW['Total Current [A]']/data_ref['Pad Current [A]']#this is the better way
ax2.plot(-1*data_MW['bias [V]'],-1*data_MW['Total Current [A]'],'k',label=environment_MW+' tot')
ax2.plot(-1*data_MW['bias [V]'],-1*data_MW['Total Current [A]']/data_MW['F'],'k--',label=environment_MW+' scaled')
ax2.plot(-1*data_ref['bias [V]'],-1*data_ref['Total Current [A]'],'r',label=environment_ref+' tot')
ax2.plot(-1*data_ref['bias [V]'],-1*data_ref['Pad Current [A]'],'r--',label=environment_ref+' pad')

ax2.set_title(info_ref['sensorname'])
ax2.set_xlabel('Bias voltage [V]')
ax2.set_ylabel('Current [A]')
ax2.legend(loc='upper left')

plt.show()
