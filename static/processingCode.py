# -*- coding: utf-8 -*-
# env/geomatics01

# author: arkriger - https://github.com/AdrianKriger/realTimePPP101

# -- based on:
#           - Ruffin: https://github.com/ruffsl/RTKLIB-Tools
#           - Chen Chao: https://github.com/heiwa0519/PPPLib


import math
import time
from sklearn.metrics import mean_squared_error

import numpy as np
import pandas as pd

from pyproj import Proj
from shapely.geometry import Point
import shapely.geometry

from processingUtils import distTime_std_plt

def read_target(cntr, crs):
    
    # the reference point
    
    c = pd.read_csv(cntr, sep='\t+', skiprows=4,  usecols=[1, 2, 3], engine='python',
                    names=['lat', 'long', 'z'])
    c = c.iloc[1]
    c = pd.to_numeric(c)#, downcast="float")
    
    myProj = Proj(crs)
    x, y = myProj(c['long'], c['lat'])
    # adding lists as new column to dataframe df
    c['y'] = y
    c['x'] = x
    
    return c

def buildDataFrame(posFile, cntr, crs):
    pd.options.mode.chained_assignment = None
    
    # build a df with the available data:
    #   - add x, y and z difference columns [that is reference minus solution at epoch]
    
    skiprow = 0
    with open(posFile) as search:
        for i, line in enumerate(search):
            if "%  UTC" in line:
                skiprow = i
                break
    df = pd.read_csv(posFile, skiprows=skiprow, delim_whitespace=True, parse_dates=[[0, 1]])
    #reference = gp.point.Point(df['latitude(deg)'][0], df['longitude(deg)'][0], df['height(m)'][0])

    df['sd(m)'] = np.sqrt(df['sdn(m)']**2+df['sde(m)']**2+df['sdu(m)']**2+df['sdne(m)']**2+df['sdeu(m)']**2+df['sdun(m)']**2)
    df['dist(m)'] = 0.0
    df['disty(m)'] = 0.0
    df['distx(m)'] = 0.0
    df['distz(m)'] = 0.0
    
    myProj = Proj(crs)
    x, y = myProj(df['longitude(deg)'].values, df['latitude(deg)'].values)
    #x, y = myProj(w['lng'].values, w['lat'].values)
    
    # df.insert() to add a column
    df.insert(4, "x", x, True)
    df.insert(5, "y", y, True)
    
    #df['UTC'] = UTCFromGps(df['%_GPST'].apply(lambda x: x.split(' ')[0]),
    #                       df['%_GPST'].apply(lambda x: x.split(' ')[1]))
    
    #df['UTC'] = df.apply(lambda row: UTCFromGps(row['%_GPST'][:4],
                                                #row['%_GPST'][4:]), axis = 1)
    
    cn = read_target(cntr, crs)
    reference = Point(cn['x'], cn['y'])
    
    for i in df.index :
        j = Point(df['x'][i], df['y'][i])
        k = Point(cn['x'], df['y'][i])
        l = Point(df['x'][i], cn['y'])
                
        j = reference.distance(j)#.meters
        k = reference.distance(k)#.meters#*np.sign(east)
        l = reference.distance(l)#.meters#*np.sign(north)
        m = (df['height(m)'][i] - cn['z'])
        q = np.core.sqrt(j**2+m**2)
        
        df['dist(m)'][i] = q
        df['disty(m)'][i] = k
        df['distx(m)'][i] = l
        df['distz(m)'][i] = m
        
    # en = np.empty(1)
    # enu = np.empty(1)
    # for i in range(1, df.x.__len__()):
    #     #enu.append(math.sqrt(df.x[i]*df.x[i]+df.y[i]*df.y[i]+df['height(m)'][i]*df['height(m)'][i]))
    #     np.append(enu, math.sqrt(df.x[i]*df.x[i]+df.y[i]*df.y[i]+df['height(m)'][i]*df['height(m)'][i]))
    #     #en.append(math.sqrt(df.x[i]*df.x[i]+df.y[i]*df.y[i]))
    #     np.append(en, math.sqrt(df.x[i]*df.x[i]+df.y[i]*df.y[i]))
            
    # [rms_x, std_x] = d2(df.x, cn.x)
    # [rms_y, std_y] = d2(df.y, cn.y)
    # [rms_z, std_z] = d2(df['height(m)'], cn.z)
    # [rms2d, std_rms2d] = get_2drms(en)
    # [mrse, std_mrse] = get_mrse(enu)
        
    # #wr = [rms_x, std_x, rms_y, std_y, rms_z, std_z, rms2d, std_rms2d, mrse, std_mrse]
        
    # with open(rmstxt, "w") as file:
    #     #file.write(str(rms_x))
    #     file.write('rms x: {}; std x: {}\nrms y: {}; std y: {}\nrms z: {}; std z: {}\n\n\2drms: {}; std_2drms: {}\nmrse: {}, std_mrse" {}'.format(rms_x, std_x,rms_y, std_y, rms_z, 
    #                                                              std_z, rms2d, std_rms2d,
    #                                                              mrse, std_mrse))
    # file.close()
            
    return df

def plot(df, jparams):
    
    import matplotlib as mpl
    #from matplotlib import pyplot
    #import matplotlib.pylab as pl
    import matplotlib.dates as md
    #from datetime import *
    
    #import matplotlib as mpl

    ymin = df.y.min()
    ymax = df.y.max()
    xmin = df.x.min()
    xmax = df.x.max()
    
    ydif = ymax - ymin
    xdif = xmax - xmin
    
    yminlim = df.y.min() - ydif*0.1
    ymaxlim = df.y.max() + ydif*0.1
    xminlim = df.x.min() - xdif*0.1
    xmaxlim = df.x.max() + xdif*0.1
    
    distnmin = df['disty(m)'].min()
    distnmax = df['disty(m)'].max()
    distemin = df['distx(m)'].min()
    distemax = df['distx(m)'].max()
    
    distndif = distnmax - distnmin
    distedif = distemax - distemin
    
    distnminlim = df['disty(m)'].min() - distndif*0.1
    distnmaxlim = df['disty(m)'].max() + distndif*0.1
    disteminlim = df['distx(m)'].min() - distedif*0.1
    distemaxlim = df['distx(m)'].max() + distedif*0.1
    
    distmax = df['dist(m)'].max()
    distmin = df['dist(m)'].min()
    distnorm = mpl.colors.Normalize(vmin=-distmax, vmax=0)
    
    tdate = df['%_UTC']-df['%_UTC'][0]
    # specify a date to use for the times
    zero = df['%_UTC'][0]
    time = [zero + t for t in tdate]
    # convert datetimes to numbers
    zero = md.date2num(zero)
    time = [t-zero for t in md.date2num(time)]
    
    sd = ['sd_y','sd_x','sd_x'] #,'sdne','sdeu','sdun']
    dd = ['Y','X','Z'] #,'distne','disteu','distun']
    dist = [df['disty(m)'], df['distx(m)'], df['distz(m)']] #,distne,disteu,distun]

    # 2 plots i) distance vs Time ii) std dev vs Time
    distTime_std_plt(df, sd, dd, dist, time, jparams)
    

    
    
    
    
    
    
    
    
    