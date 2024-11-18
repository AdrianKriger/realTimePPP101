# -*- coding: utf-8 -*-
# env/geomatics01

# created on Sept. 2024
# author: arkriger

# basic rtklib processing

import os, sys
import subprocess

import json

import math
import time
import datetime as dt

import numpy as np
import pandas as pd

import pyproj
from pyproj import Proj
from shapely.geometry import Point
import shapely.geometry

import matplotlib.dates as md

from gmp370sUtils import UTCFromGps, d2, get_rms2d, get_mrse, get_rms2d2, get_mrse2, move_debug, std_errorDist, pos_errorDist, pos_Convg, decimalDegree


def readTarget(cntr, crs, jparams):
    c = pd.read_csv(cntr, sep='\t+', 
                    #skiprows=4,  
                    comment ='#', usecols=[0, 1, 2, 3], engine='python',
                    names=['Name', 'lat', 'long', 'z'])
    #- harvest only the necessary

    myProj = Proj(crs)
    x, y = myProj(c['long'], c['lat'])
    # adding lists as new column to dataframe df
    c['y'] = y
    c['x'] = x
    
    print('c:', c)
    
    return c

def prepareSolDF(posFile, cntr, crs, jparams):
    pd.options.mode.chained_assignment = None
    
    skiprow = 0
    with open(posFile) as search:
        for i, line in enumerate(search):
            if "%  GPST" in line:
                skiprow = i
                break
    df = pd.read_csv(posFile, skiprows=skiprow, delim_whitespace=True, parse_dates=[[0, 1]])

    df['sd(m)'] = np.sqrt(df['sdn(m)']**2+df['sde(m)']**2+df['sdu(m)']**2+df['sdne(m)']**2+df['sdeu(m)']**2+df['sdun(m)']**2)
    df['dist(m)'] = 0.0
    df['deltay(m)'] = 0.0
    df['deltax(m)'] = 0.0
    df['deltaz(m)'] = 0.0
    
    myProj = Proj(crs)
    x, y = myProj(df['longitude(deg)'].values, df['latitude(deg)'].values)
    
    # df.insert() to add a column
    df.insert(4, "x", x, True)
    df.insert(5, "y", y, True)
    
    df['Gw'] = df['%_GPST'].apply(lambda x: x.split(' ')[0])
    df['Gs'] = df['%_GPST'].apply(lambda x: x.split(' ')[1])

    UTC = df.apply(lambda row: UTCFromGps(float(row['Gw']), float(row['Gs']), 
                                          leapSecs=jparams['gps-leapSec']), axis = 1)

    df.insert(1, "UTC", UTC, True)
    # datetime
    df['UTC'] = pd.to_datetime(df['UTC'])
    
    cn = readTarget(cntr, crs, jparams)
    reference = Point(cn['x'], cn['y'])
    
    for i in df.index :
        j = Point(df['x'][i], df['y'][i])
        k = Point(cn['x'][0], df['y'][i])
        l = Point(df['x'][i], cn['y'][0])
        
        j = reference.distance(j)    #.meters

        m = ( cn['z'][0] - df['height(m)'][i])
        k = (cn['y'] - df['y'][i])
        l = (cn['x'] - df['x'][i])
        
        q = np.core.sqrt(j**2+m**2)
        
        df['dist(m)'][i] = q
        df['deltay(m)'][i] = k
        df['deltax(m)'][i] = l
        df['deltaz(m)'][i] = m
    
    df.loc[:,'cx'] = cn['x'][0]#cn.loc[1].x #
    df.loc[:,'cy'] = cn['y'][0]#cn.loc[1].y #
    df.loc[:,'cz'] =  cn['z'][0]#cn.loc[1].z #
    #cn['Rxyz'] = cn['x'] + cn['y'] + cn['z']
    df['Rxyz'] = df['cx'] + df['cy'] + df['cz']
    df['xyz'] = df['x'] + df['y'] + df['height(m)']
    
    timeD = (df['UTC'].iat[-1] - df['UTC'].iat[0])#.dt.minutes
       
    [rms_x, std_x] = d2(df.x, df.cx)
    [rms_y, std_y] = d2(df.y, df.cy)
    [rms_z, std_z] = d2(df['height(m)'], df.cz)
    [rms_3d, std_3d] = d2(df.xyz, df['Rxyz'])

    
    #rms2d = get_rms2d(rms_x, rms_y)
    #mrse = get_mrse(rms_x, rms_y, rms_z)
    
    rms2d2 = get_rms2d2(df.x, df.cx, df.y, df.cy)
    mrse2 = get_mrse2(df.x, df.cx, df.y, df.cy, df['height(m)'], df.cz)
    
    if jparams['write_rms'] == "True":
        with open(jparams['statistic_txt'], "w") as file:
                #file.write(str(rms_x))
                file.write('rms x: {}; std x: {}\nrms y: {}; std y: {}\nrms z: {}; std z: {}\
                \nrms 3d: {}; std 3d: {}\n\n2drms: {}\nmrse: {}\
                    \n\nconvergence: deltay deltax deltaz\
                    \n30 min (1800): {} {} {}\n45 min (2700): {} {} {}\n60 min (3600): {} {} {}\
                    \n\nfinal error after {} observation:\
                    \n {} {} {}'.format(rms_x, std_x, 
                                                                        rms_y, std_y, 
                                                                        rms_z, std_z, 
                                                                        rms_3d, std_3d,
                                                                        rms2d2, mrse2,
                                                                        round(df.at[1800,'deltay(m)'], 4), round(df.at[1800,'deltax(m)'], 4), round(df.at[1800,'deltaz(m)'], 4),
                                                                        round(df.at[2700,'deltay(m)'], 4), round(df.at[2700,'deltax(m)'], 4), round(df.at[2700,'deltaz(m)'], 4),
                                                                        #round(df.at[3600,'deltay(m)'], 4), round(df.at[3600,'deltax(m)'], 4), round(df.at[3600,'deltaz(m)'], 4),
                                                                        round(df.at[3600,'deltay(m)'], 4), round(df.at[3600,'deltax(m)'], 4), round(df.at[3600,'deltaz(m)'], 4),
                                                                        timeD, 
                                                                        round(df['deltay(m)'].iat[-1], 4), round(df['deltax(m)'].iat[-1], 4), round(df['deltaz(m)'].iat[-1], 4)))
        file.close()
        
    #wr = [rms_x, std_x, rms_y, std_y, rms_z, std_z, rms2d, std_rms2d, mrse, std_mrse]

    columns = ['%_GPST', 'UTC', 'latitude(deg)', 'longitude(deg)', 'height(m)', 'x', 'y', 'Q', 'ns', 
               'sdn(m)', 'sde(m)', 'sdu(m)', 'sdne(m)', 'sdeu(m)', 'sdun(m)', 'age(s)', 'ratio', 
               'sd(m)', 'dist(m)', 'deltay(m)', 'deltax(m)', 'deltaz(m)']
    df1 = pd.DataFrame(df, columns=columns)
    
    return df1

def prepareAzimDF(posFile, jparams):
    
    inFile2 = posFile.split('_')[-1].split('.')[0]
    inFile2 = './trace_stats/rtknavi_' + inFile2 + '.stat'
 
    ### Loop the data lines
    with open(inFile2, 'r') as temp_f:
        # get No of columns in each line
        col_count = [ len(l.split(",")) for l in temp_f.readlines() ]
    
    ### Generate column names  (names will be 0, 1, 2, ..., maximum columns - 1)
    column_names = [i for i in range(0, max(col_count))]
    
    ### Read csv
    df = pd.read_csv(inFile2, header=None, delimiter=",", names=column_names, parse_dates=[[1, 2]])
    df.drop(df[df[0] != '$SAT'].index, inplace=True)
    df.drop([0, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], axis=1, inplace=True)
    df.columns = ['GPS_time', 'SV', 'freq', 'Azim', 'Elev']
    df.reset_index(drop=True, inplace=True)
    
    #-- UTC
    df['Gw'] = df['GPS_time'].apply(lambda x: x.split(' ')[0])
    df['Gs'] = df['GPS_time'].apply(lambda x: x.split(' ')[1])
    #df['UTC'] = UTCFromGps(df['Gw'], df['Gs'], leapSecs=14):
    #print(df['Gs'])
    UTC = df.apply(lambda row: UTCFromGps(float(row['Gw']), float(row['Gs']), leapSecs=jparams['gps-leapSec']), axis = 1)
    # df.insert() to add a column
    df.insert(1, "UTC", UTC, True)
    # datetime
    df['UTC'] = pd.to_datetime(df['UTC'])
    
    outFile = posFile.split('/')[-1].split('.')[0]
    #-- write df
    df.to_csv('./sol_azim-elev/' + outFile + '.csv', sep=',', index=True, header=True)

    
def move_files(jparams):
    
    move_debug(jparams)

