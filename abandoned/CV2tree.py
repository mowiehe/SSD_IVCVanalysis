#! /usr/bin/env python

# 3.12.2020
# converts SSD CV measurement (.cv) to ROOT file

# argument 1: full filename

import ROOT as rt
from array import array
import sys
import csv

filename=sys.argv[1]

## create output tree and file
outfile=rt.TFile(filename[:-3]+'.root','RECREATE')
outtree=rt.TTree('outtree','outtree')

#open csv file and read data
with open(filename) as csvfile:
    for line in csvfile:
        if 'BEGIN' in line: break
        
    data=csv.DictReader(csvfile,fieldnames=['V_detector','Capacitance','Conductivity','Bias','CurrentPowerSupply'],delimiter='\t')

    for i,row in enumerate(data):
        print row
#        if i>10: break
            if 'END' in  entry['Vdetector']:
                print str(i)+' lines processed'
                break
