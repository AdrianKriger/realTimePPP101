# -*- coding: utf-8 -*-
# env/geomatics01

# created on Sat Oct 16 21:23:45 2021
# author: arkriger

# basic rtklib processing


### todo:
#       - harvest igs/ngi_trignet reference coord. ~~ rms, standard deviation, etc 
#       - transform .rctm3 to .nav and .obs (rtkconv) ~~ harvest dop, gdop, etc.
#       - would it be beneficial to call an ftp and download a fresh differential code bias (.bia)?

from pyproj import Proj

import pandas as pd



def readposfile(fpos, lat0=None, lng0=None):
    for sr, l in enumerate(open(fpos)):
        if l[0] != "%":
            break
    w = pd.read_csv(fpos, skiprows=sr-1, sep="\s+")
    w.rename(columns={"latitude(deg)":"lat", "longitude(deg)":"lng", "height(m)":"alt"}, inplace=True)
      
    myProj = Proj(utm34s)
    x, y = myProj(w['lng'].values, w['lat'].values)
    #x, y = myProj(w['lng'].values, w['lat'].values)
    
    # df.insert() to add a column
    w.insert(4, "x", x, True)
    w.insert(5, "y", y, True)
        
    w["time"] = pd.to_datetime(w["%"]+" "+w["UTC"])
    w.drop(["%", "UTC"], 1, inplace=True)
    w.set_index("time", inplace=True)
    w.index.name = None
    return w


#utm34S
utm34s = "+proj=utm +zone=34 +south +a=6378249.145 +b=6356514.966398753 +towgs84=-134.73,-110.92,-292.66,0,0,0,0 +units=m +no_defs"

fpos = 'C:/rtklib_realTime_PPP/sol/cpt_20211017_1344.pos'

if __name__ == '__main__':
    df = readposfile(fpos)
    print(df.head(2))


