# -*- coding: utf-8 -*-
# env/geomatics01

# created on Sat Oct 16 21:23:45 2021
# author: arkriger

# basic rtklib processing

### !!!! --- it might be better to output in decimal degrees !!! --- ####

### todo:
#       - harvest igs/ngi_trignet reference coord. ~~ rms, standard deviation, etc 
#       - transform .rctm3 to .nav and .obs (rtkconv) ~~ harvest dop, gdop, etc.
#       - would it be beneficial to call an ftp and download a fresh differential code bias (.bia)?

import pandas as pd

fpos = 'C:/rtklib_realTime_PPP/sol/Cpt_sol_20211016_19.pos'

def readposfile(fpos, lat0=None, lng0=None):
    for sr, l in enumerate(open(fpos)):
        if l[0] != "%":
            break
    w = pd.read_csv(fpos, skiprows=sr-1, sep="\s+")
    w = w.reset_index().rename(columns={'index':'%'})
    w['latitude'] = w.level_2.astype(str) + ' ' + w.level_3.astype(str) + ' ' + w['%'].astype(str)
    w['longitude'] = w.GPST.astype(str) + ' ' + w['latitude(deg)'].astype(str) + ' ' + w['longitude(deg)'].astype(str)

    w.drop(['level_2', 'level_3', '%'], axis=1, inplace=True)
    w.drop(['GPST', 'latitude(deg)', 'longitude(deg)'], axis=1, inplace=True)
    w.rename(columns={"level_0":"date", "level_1":"time"}, inplace=True)

    column_names = ["date", "time", "latitude", 'longitude', 'height(m)',
                    'Q', 'ns', 'sdn(m)', 'sde(m)', 'sdu(m)', 'sdne(m)', 'sdeu(m)', 'sdue(m)']

    df = w[column_names]

    return df

df = readposfile(fpos)

