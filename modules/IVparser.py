#6.1.21, mw

import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np
import ROOT as rt
import SSDanalysis.modules.SSDparser as parser

#parse IV files taken at the SSD probestation with TCT software
#import as module or call with python3 -i IVparser.py filename
def IVparser(filename):
    header,data=parser.parser(filename)
    data['Total/Pad']=data['Total Current [A]']/data['Pad Current [A]']#add ratio of currents
    
    return header,data

def IVplot(header,data,pol=-1):
    #use header and data from IVparser to plot current measurements
    ## Current vs. Bias
    fig,ax=plt.subplots(2,figsize=[8,8])
    ax[0].plot(pol*data['bias [V]'],pol*data['Total Current [A]'],'k',label='Total Current')
    ax[0].plot(pol*data['bias [V]'],pol*data['Pad Current [A]'],'k--',label='Pad Current')
    ax[0].set_title(header['Sample']+' '+header['start'])
    ax[0].set_xlabel('Bias voltage [V]')
    ax[0].set_ylabel('Current [A]')
    ax[0].legend(loc='upper left')
    
    ## Ratio total to pad current
    ax[1].plot(-1*data['bias [V]'],data['Total/Pad'],'k')
    ax[1].set_xlabel('Bias voltage [V]')
    ax[1].set_ylabel('Ratio total/pad')
    ##
    return fig,ax

def IVplot_rt(header,data,pol=-1,color=1):
    g=rt.TGraph(len(data),np.array(pol*data['bias [V]']),np.array(pol*data['Pad Current [A]']))
    g.GetYaxis().SetTitle('Current [A]')
    g.GetXaxis().SetTitle('Bias voltage [V]')
    g.SetLineColor(color)
    return g

def alphacalc(header,data,phi,Vpad,pol=-1):
    #adds current related damage rate to IVdataframe
    #input of phi in neq/cm^2 and Vpad in cm^3
    data['alpha [A/cm]']=pol*data['Pad Current [A]']/(phi*Vpad)
    return header,data

if len(sys.argv)==2:
    header,data=IVparser(sys.argv[1])
    fig,ax=IVplot(header,data)
    print('\nUse header,data,fig,ax')
    print('Repeat plot with IVplot(header,data,pol=-1)')


