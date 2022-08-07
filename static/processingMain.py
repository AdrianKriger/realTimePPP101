# -*- coding: utf-8 -*-
# - env/rt_ppp_env

# basic post-processing for real-time PPP analysis

# author: arkriger - https://github.com/AdrianKriger/realTimePPP101

import os
import shutil
import json, sys

from processingCode import prepareSolDF, move_files, prepareAzimDF #convin #plot,

def main():
    try:
        jparams = json.load(open('paramsPret-SB.json'))
    except:
        print("ERROR: something is wrong with the params.json file.")
        sys.exit()
    
    # -- move some files
    move_files(jparams)
    
    posFile = jparams['input-rtkpos']
    cntr = jparams['reference-point']
    crs = jparams['crs']
        
    prepareSolDF(posFile, cntr, crs, jparams)
    # read the .pos to df
    #df = buildDataFrame(posFile, cntr, crs, jparams)
    prepareAzimDF(posFile)
    
    #convin(jparams)
    
    #if jparams['plots'] == 'True':
        #plot(df, jparams)

if __name__ == "__main__":
    main()