# -*- coding: utf-8 -*-
# env/geomatics01

# author: arkriger - https://github.com/AdrianKriger/realTimePPP101

# -- based on:
#           - Ruffin: https://github.com/ruffsl/RTKLIB-Tools
#           - Chen Chao: https://github.com/heiwa0519/PPPLib
import os, sys
import subprocess

import json

import math
import time

import numpy as np
import pandas as pd

from pyproj import Proj
from shapely.geometry import Point
import shapely.geometry

from processingUtils import UTCFromGps, d2, get_rms2d, get_mrse, distTime_std_plt, grnd_track_plt, move_debug

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

def buildDataFrame(posFile, cntr, crs, jparams):
    pd.options.mode.chained_assignment = None
    
    # build a df with the available data:
    #   - transform lat, lon to x, y in local crs
    #   - add UTC
    #   - add x, y and z difference columns [that is reference minus solution at epoch]
    #   - rms and std for x, y and z with 2d rms and mrse -> write the text
    
    skiprow = 0
    with open(posFile) as search:
        for i, line in enumerate(search):
            if "%  GPST" in line:
                skiprow = i
                break
    df = pd.read_csv(posFile, skiprows=skiprow, delim_whitespace=True, parse_dates=[[0, 1]])
    #reference = gp.point.Point(df['latitude(deg)'][0], df['longitude(deg)'][0], df['height(m)'][0])

    df['sd(m)'] = np.sqrt(df['sdn(m)']**2+df['sde(m)']**2+df['sdu(m)']**2+df['sdne(m)']**2+df['sdeu(m)']**2+df['sdun(m)']**2)
    df['dist(m)'] = 0.0
    df['deltay(m)'] = 0.0
    df['deltax(m)'] = 0.0
    df['deltaz(m)'] = 0.0
    
    myProj = Proj(crs)
    x, y = myProj(df['longitude(deg)'].values, df['latitude(deg)'].values)
    #x, y = myProj(w['lng'].values, w['lat'].values)
    
    # df.insert() to add a column
    df.insert(4, "x", x, True)
    df.insert(5, "y", y, True)
    
    #-- UTC
    df['Gw'] = df['%_GPST'].apply(lambda x: x.split(' ')[0])
    df['Gs'] = df['%_GPST'].apply(lambda x: x.split(' ')[1])
    #df['UTC'] = UTCFromGps(df['Gw'], df['Gs'], leapSecs=14):
    #print(df['Gs'])
    UTC = df.apply(lambda row: UTCFromGps(float(row['Gw']), float(row['Gs']), leapSecs=jparams['gps-leapSec']), axis = 1)
    # df.insert() to add a column
    df.insert(1, "UTC", UTC, True)
    # datetime
    df['UTC'] = pd.to_datetime(df['UTC'])
    
    cn = read_target(cntr, crs)
    reference = Point(cn['x'], cn['y'])
    
    for i in df.index :
        j = Point(df['x'][i], df['y'][i])
        k = Point(cn['x'], df['y'][i])
        l = Point(df['x'][i], cn['y'])
        
        #j = d(reference, j)#.meters
        #k = d(reference, k)#.meters#*np.sign(east)
        #l = d(reference, l)#.meters#*np.sign(north)
        #m = (df['height(m)'][i] - cn['z'])
        #q = np.core.sqrt(j**2+m**2)
        
        j = reference.distance(j)#.meters
        #k = reference.distance(k)#.meters#*np.sign(east)
        #l = reference.distance(l)#.meters#*np.sign(north)
        m = (df['height(m)'][i] - cn['z'])
        k = (df['y'][i] - cn['y'])
        l = (df['x'][i] - cn['x'])
        
        q = np.core.sqrt(j**2+m**2)
        
        df['dist(m)'][i] = q
        df['deltay(m)'][i] = k
        df['deltax(m)'][i] = l
        df['deltaz(m)'][i] = m
    
    cn['Rxyz'] = cn['x'] + cn['y'] + cn['z']
    df['xyz'] = df['x'] + df['y'] + df['height(m)']
           
    [rms_x, std_x] = d2(df.x, cn.x)
    [rms_y, std_y] = d2(df.y, cn.y)
    [rms_z, std_z] = d2(df['height(m)'], cn.z)
    [rms_3d, std_3d] = d2(df.xyz, cn['Rxyz'])
    
    #rms2d = get_2drms(df['distx(m)'], df['disty(m)'])
    rms2d = get_rms2d(rms_x, rms_y)
    #mrse = get_mrse(df['distx(m)'], df['disty(m)'], df['distz(m)'])
    mrse = get_mrse(rms_x, rms_y, rms_z)
                
    # with open(jparams['statistic_txt'], "w") as file:
    #     #file.write(str(rms_x))
    #     file.write('rms x: {}; std x: {}\nrms y: {}; std y: {}\nrms z: {}; std z: {}\
    #     \nrms 3d: {}; std 3d: {}\n\n2drms: {}\nmrse: {}'.format(rms_x, std_x, 
    #                                                             rms_y, std_y, 
    #                                                             rms_z, std_z, 
    #                                                             rms_3d, std_3d,
    #                                                             rms2d, mrse))
    # file.close()
    
    # columns = ['%_GPST', 'UTC', 'latitude(deg)', 'longitude(deg)', 'height(m)', 'x', 'y', 'Q', 'ns', 
    #        'sdn(m)', 'sde(m)', 'sdu(m)', 'sdne(m)', 'sdeu(m)', 'sdun(m)', 'age(s)', 'ratio', 
    #        'sd(m)', 'dist(m)', 'deltay(m)', 'deltax(m)', 'deltaz(m)']
    # df1 = pd.DataFrame(df, columns=columns)
    # df1.to_csv(jparams['solution_df'])
            
    return df

def convin(jparams):

    fname = jparams["input-rtkpos"]
    start = './sol/cpt_'
    end = '.pos'
    file = fname[fname.find(start)+len(start):fname.rfind(end)]
    #print(file)
    
    cnvbin = jparams["cmd_cnvin_path"]
    
    command = ([cnvbin, jparams["cmd_cnvin_dir"] + '/' + 'cpt_obs_log_' +  file + '.rtcm3', '-r', 'rtcm3',
                '-d', jparams["cmd_cnvin_dir"],
                '-o',  file + '.obs', 
                '-n',  file + '.nav'])#, 
                #'-od', '-os', '-oi', '-ot', '-ol'])
        
    #print('\nRunning ')
    #print(' '.join(command))
    subprocess.check_call(command)

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
    
    distnmin = df['deltay(m)'].min()
    distnmax = df['deltay(m)'].max()
    distemin = df['deltax(m)'].min()
    distemax = df['deltax(m)'].max()
    
    distndif = distnmax - distnmin
    distedif = distemax - distemin
    
    distnminlim = df['deltay(m)'].min() - distndif*0.1
    distnmaxlim = df['deltay(m)'].max() + distndif*0.1
    disteminlim = df['deltax(m)'].min() - distedif*0.1
    distemaxlim = df['deltax(m)'].max() + distedif*0.1
    
    distmax = df['dist(m)'].max()
    distmin = df['dist(m)'].min()
    distnorm = mpl.colors.Normalize(vmin=-distmax, vmax=0)
    
    tdate = df['UTC']-df['UTC'][0]
    # specify a date to use for the times
    zero = df['UTC'][0]
    time = [zero + t for t in tdate]
    # convert datetimes to numbers
    zero = md.date2num(zero)
    time = [t-zero for t in md.date2num(time)]
    
    sd = ['sd_y','sd_x','sd_x'] #,'sdne','sdeu','sdun']
    dd = ['Y','X','Z'] #,'distne','disteu','distun']
    dist = [df['deltay(m)'], df['deltax(m)'], df['deltaz(m)']] #,distne,disteu,distun]

    # 2 plots - i) distance vs Time ii) std dev vs Time
    distTime_std_plt(df, sd, dd, dist, time, jparams)
    # 1 plot - ground track 
    grnd_track_plt(df, distnminlim, distnmaxlim, disteminlim, distemaxlim, jparams)
    
def move_files(jparams):
    
    move_debug(jparams)
    


    
    
    
    
    
    
    
    
    