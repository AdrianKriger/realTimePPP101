# -*- coding: utf-8 -*-
# - env/geomatics01

# basic post-processing for real-time PPP analysis

# author: arkriger - https://github.com/AdrianKriger/realTimePPP101

import os
import shutil
import json, sys

from processingCode import buildDataFrame, plot, move_files, convin

def main():
    try:
        jparams = json.load(open('params.json'))
    except:
        print("ERROR: something is wrong with the params.json file.")
        sys.exit()
    
    posFile = jparams['input-rtkpos']
    cntr = jparams['reference-point']
    crs = jparams['crs']
    
    # -- move some files
    move_files(jparams)
        
    # read the .pos to df
    df = buildDataFrame(posFile, cntr, crs, jparams)
    
    #convin(jparams)
    
    if jparams['plots'] == 'True':
        plot(df, jparams)

if __name__ == "__main__":
    main()