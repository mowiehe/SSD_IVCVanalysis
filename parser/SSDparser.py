#10.2.2021, mw
#functions common to all parsing modules

import pandas as pd

def parser(filename):
    print('Parsing file',filename)
    header={}
    filecontent=[]
    data=pd.DataFrame()
    readData=False
    with open(filename,'r') as reader:
        filecontent=reader.readlines()
    for i,line in enumerate(filecontent):
        if line[0]==':':
            header[line[1:-1]]=filecontent[i+1][:-1]#bug: only reads first line of each header entry
        if 'BEGIN' in line:
            header['legend']=header['legend'].split('\t')#this defines the DF columns
            readData=True
            continue
        if 'END' in line:
            readData=False
            break
        if readData:
            line=line[:-1].split('\t')#delete end of line and split in tab
            if len(line)!=len(header['legend']): print('Error in number of columns!'); break
            row={header['legend'][col]:float(line[col]) for col in range(len(line))}
            data=data.append(row,ignore_index=True)
    ##
    ##adfjust for older versions
    if header['Program Version'].split(',')[-1] == ' 6.2011 Gabrysch':
        header['Sample']=header.pop('device')
    return header,data
