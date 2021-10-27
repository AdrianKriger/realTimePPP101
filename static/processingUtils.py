# -*- coding: utf-8 -*-
# - env/geomatics01

# author: arkriger - https://github.com/AdrianKriger/realTimePPP101

import os
import shutil

import math
from sklearn.metrics import mean_squared_error

import numpy as np

import time
from datetime import datetime

import matplotlib as mpl
from matplotlib import pyplot
import matplotlib.pylab as pl
import matplotlib.dates as md
#from datetime import *

import matplotlib as mpl

def get_average(records):
    """
    """
    return sum(records)/len(records)


def get_variance(records):
    """
    """
    average = get_average(records)
    return sum([(x-average) ** 2 for x in records])/len(records)


def get_standard_deviation(records):
    """
    """
    variance = get_variance(records)
    return math.sqrt(variance)


def get_mse(measured, target):
    """
    """
    mse = mean_squared_error(measured, [target for _ in measured], squared=False)
    return mse


def get_rmse(measured, target):
    
    #
    # - this function might not be necessary given the one above
    #
    
    mse = get_mse(measured, target)
    if mse:
        return math.sqrt(mse)
    else:
        return None
    
def d2(df, target):
    
    rmse = get_rmse(df, target)
    std = get_standard_deviation(df)
    
    return round(rmse, 4), round(std, 4)

def get_rms2d(rms_x, rms_y):
    
    # Twice the DRMS of the horizontal position errors, defining the radius of a circle centered at the 
    # true position, containing the horizontal position estimate with a probability of 95 %.
    # - https://gnss-sdr.org/design-forces/accuracy/
    
    drms2 = round(2 * math.sqrt(rms_x**2 + rms_y**2), 4)

    return drms2

def get_mrse(rms_x, rms_y, rms_z):
    
    # The radius of a sphere centered at the true position, containing the position estimate in 3D with a 
    # probability of 61 %.
    # - https://gnss-sdr.org/design-forces/accuracy/
    
    mrse = round(math.sqrt(rms_x**2 + rms_y**2 + rms_z**2), 4)

    return mrse

def UTCFromGps(gpsWeek, SOW, leapSecs):
    
    #-- A Python implementation of GPS related time conversions.
    #-- Copyright 2002 by Bud P. Bruegger, Sistema, Italy
    #-- mailto:bud@sistema.it
    #-- http://www.sistema.it
    
    secsInWeek = 604800
    secsInDay = 86400
    gpsEpoch = (1980, 1, 6, 0, 0, 0)
    
    # converts gps week and seconds to UTC
    # SOW = seconds of week
    # gpsWeek is the full number (not modulo 1024)
    
    secFract = SOW % 1
    epochTuple = gpsEpoch + (-1, -1, 0) 
    t0 = time.mktime(epochTuple) - time.timezone  #mktime is localtime, correct for UTC
    tdiff = (gpsWeek * secsInWeek) + SOW - leapSecs
    t = t0 + tdiff
    year, month, day, hh, mm, ss, dayOfWeek, julianDay, daylightsaving = time.gmtime(t)
    #use gmtime since localtime does not allow to switch off daylighsavings correction!!!
    
    time_tuple = (year, month, day, hh, mm, int(ss + secFract))
    d = datetime(*time_tuple[0:6])
    
    return d

def move_debug(jparams):
    fname = jparams['input-rtkpos']

    start = './sol/cpt_'
    end = '.pos'
    f = fname[fname.find(start)+len(start):fname.rfind(end)]
    
    if os.path.exists("./RTKLIB_2.4.3_b34/bin/rtknavi_" + f + ".stat"):
        shutil.move("./RTKLIB_2.4.3_b34/bin/rtknavi_" + f + ".stat", "./trace_stats/rtknavi_" + f + ".stat")
        shutil.move("./RTKLIB_2.4.3_b34/bin/rtknavi_" + f + ".trace", "./trace_stats/rtknavi_" + f + ".trace")
 

def distTime_std_plt(df, sd, dd, dist, time, jparams):
    
    colors = pl.cm.viridis(np.linspace(0,1,3))
    
    # Create a new figure of size 10x6 points, using 80 dots per inch
    fig1 = pyplot.figure(figsize=(18,12), dpi=80)
    fig1.suptitle('Position / Time', fontsize=14, fontweight='bold')
    ax = fig1.add_subplot(2,1,1)
      
    # Make plots
    for i in range(len(sd)):
        ax.plot(time, dist[i], label=dd[i], color=colors[i]) #tdate
    
    # ax.plot(tdate,dist, label='dist')
    ax.grid(True)
    ax.set_ylabel('Absolute Error (m)')
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
    ax.set_xlabel('Time (h:m)')
      
    # Make legend
    pyplot.legend(loc='upper left')
    
    ax = fig1.add_subplot(2,1,2)
      
    # Make plots
    for i in range(len(sd)):
        #sdx = df[i+8]
        sdx = df.iloc[:, 9+i]
        ax.plot(time, sdx, label=sd[i], color=colors[i]) #tdate
    
    # ax.plot(tdate,dist, label='dist')
    ax.grid(True)
    ax.set_ylabel('Standard Deviation (m)')
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
    ax.set_xlabel('Time (h:m)')
      
    # Make legend
    pyplot.legend(loc='upper left')
    
    # Save figure using 72 dots per inch
    pyplot.savefig(jparams['distanceTime_std_fig'],dpi=72)
    
def grnd_track_plt(df, distnminlim, distnmaxlim, disteminlim, distemaxlim, jparams):
    
    fig4 = pyplot.figure(figsize=(18,12), dpi=80)
    fig4.suptitle('Position and Standard Distribution', fontsize=14, fontweight='bold',
                  horizontalalignment='right', x=0.71, y=0.93,
                  verticalalignment='top')
    #ax = fig4.add_subplot(111)
    ax = fig4.add_subplot(111,aspect='equal')
    p = ax.scatter(df['disty(m)'], df['distx(m)'], c=-df['dist(m)'], alpha=.5, cmap='jet')
    fig4.colorbar(p)
    pyplot.xlim(distnminlim, distnmaxlim)
    pyplot.ylim(disteminlim, distemaxlim)
    #ax.xaxis.set_major_locator(MultipleLocator(100))
    #ax.yaxis.set_major_locator(MultipleLocator(100))
    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.grid(True)
    
    # Save figure using 72 dots per inch
    pyplot.savefig(jparams['xyz_ground_track_fig'], dpi=72)