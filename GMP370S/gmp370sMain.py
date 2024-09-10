# -*- coding: utf-8 -*-
# - env/rt_ppp_env

# basic post-processing for real-time PPP analysis

# author: arkriger - https://github.com/AdrianKriger/realTimePPP101

import os
import shutil
import json, sys

from processingCode_decDeg import prepareSolDF, move_files, prepareAzimDF #convin #plot,

def main():
    try:
        jparams = json.load(open('paramsCTWN00ZAF0.json'))

    except:
        print("ERROR: something is wrong with the params.json file.")
        sys.exit()
    
    # -- move some files
    move_files(jparams)
    
    posFile = jparams['input-rtkpos']
    cntr = jparams['reference-point']
    crs = jparams['crs']
        
    df = prepareSolDF(posFile, cntr, crs, jparams)
    if jparams['write_DataFrame'] == "True":
        df.to_csv(jparams['solution_df'])

    prepareAzimDF(posFile, jparams)

if __name__ == "__main__":
    main()