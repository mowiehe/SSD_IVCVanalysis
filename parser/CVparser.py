#10.2.21, mw

import pandas as pd
import sys
import numpy as np
import ROOT as rt
import SSDanalysis.modules.SSDparser as parser

#parse CV files, recorded with SSD CV probestation

def CVparser(filename):
    header,data=parser.parser(filename)

    return header,data

def CVplot_rt(header,data,pol=-1,color=1):
    g=rt.TGraph(len(data),np.array(pol*data['Bias [V]']),np.array(data['Capacitance [F]']))
    g.GetYaxis().SetTitle('Capacitance [F]')
    g.GetXaxis().SetTitle('Bias voltage [V]')
    g.SetLineColor(color)
    return g

