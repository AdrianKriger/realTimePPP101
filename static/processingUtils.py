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
#from matplotlib import pyplot
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import matplotlib.dates as md
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import (inset_axes, InsetPosition, mark_inset)


import seaborn as sns

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

    start = './sol/*_'
    end = '.pos'
    f = fname[fname.find(start)+len(start):fname.rfind(end)]
    
    if os.path.exists("./RTKLIB_2.4.3_b34/bin/rtknavi_" + f + ".stat"):
        shutil.move("./RTKLIB_2.4.3_b34/bin/rtknavi_" + f + ".stat", "./trace_stats/rtknavi_" + f + ".stat")
        shutil.move("./RTKLIB_2.4.3_b34/bin/rtknavi_" + f + ".trace", "./trace_stats/rtknavi_" + f + ".trace")
 
def decimalDegree(degree, minute, second, hemisphere):
    #https://stackoverflow.com/questions/27415327/using-pandas-convert-deg-min-sec-to-decimal-degrees-without-explicitly-iterating
    if hemisphere.lower() in ["w", "s", "west", "south"]:
        factor = -1.0
    elif hemisphere.lower() in ["n", "e", "north", "east"]:
        factor = 1.0
    else:
        raise ValueError("invalid hemisphere")

    # check the order of operations in your code
    return factor * (degree + (minute + second/60.)/60.)

def distTime_std_plt(df, time, jparams):
    
    colors = pl.cm.viridis(np.linspace(0,1,3))
    
    # Create a new figure of size 10x6 points, using 80 dots per inch
    fig1 = plt.figure(figsize=(18,12), dpi=80)
    fig1.suptitle(jparams['stn_name'] + ' location error / Time', fontsize=14, fontweight='bold')
    ax = fig1.add_subplot(2,1,1)
    names = ['delta y','delta x','delta z']
      
    # Make plots
    for i in range(len(names)):
        ax.plot(time, df.iloc[:, 19+i], label=names[i], color=colors[i]) #tdate
    
    # ax.plot(tdate,dist, label='dist')
    ax.grid(True)
    ax.set_ylabel('Absolute Error (m)')
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
    ax.set_xlabel('Time (h:m)')
      
    # Make legend
    plt.legend(loc='upper right')
    
    ax = fig1.add_subplot(2,1,2)
    names = ['std y','std x','std z'] 
    # Make plots
    for i in range(len(names)):
        #sdx = df[i+8]
        #sdx = df.iloc[:, 9+i]
        ax.plot(time, df.iloc[:, 9+i], label=names[i], color=colors[i]) #tdate
    
    # ax.plot(tdate,dist, label='dist')
    ax.grid(True)
    ax.set_ylabel('Standard Deviation (m)')
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
    ax.set_xlabel('Time (h:m)')
      
    # Make legend
    plt.legend(loc='upper right')
    
    # Save figure using 72 dots per inch
    plt.savefig(jparams['distanceTime_std_fig'],dpi=72)
    
def pos_Convg(df, time, jparams):
    
    colors = pl.cm.viridis(np.linspace(0,1,3))
    
    # Create a new figure of size 10x6 points, using 80 dots per inch
    fig1 = plt.figure(figsize=(18, 12))#, dpi=80)
    fig1.suptitle(jparams['stn_name'] + ' location error / Time', fontsize=14, fontweight='bold',
                  horizontalalignment='center', x=0.5, y=0.92, verticalalignment='top')
    ax = fig1.add_subplot(2,1,1)
    names = ['delta y','delta x','delta z']
      
    # Make plots
    for i in range(len(names)):
        ax.plot(time, df.iloc[:, 19+i], label=names[i], color=colors[i]) #tdate
      
    # Make legend
    plt.legend(loc='upper right')
    
    ax.grid(False)#axis='y', linestyle='-', linewidth=0.3)
    ax.set_ylabel('Absolute Error (m)', fontweight='bold')
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
    ax.set_xlabel('Time (h:m)', fontweight='bold')
          
    # Make legend
    plt.legend(loc='upper right')
    
    # Create a set of inset Axes
    ax2 = plt.axes([0.1, 0.1, 1.1, 1.1])
    # Manually set the position and relative size of the inset axes within ax1
    ip = InsetPosition(ax, [0.35, 0.35, 0.45, 0.45])
    ax2.set_axes_locator(ip)
    
    # do the time for the inset
    t1 = time[1799:3600]
    indate = df[(df.index >= 1800) & (df.index <= 3600)]
    
    # plot the inset
    for i in range(len(names)):
        ax2.plot(t1, indate.iloc[:, 19+i], color=colors[i])#label=names[i]) #tdate

    # -- https://stackoverflow.com/questions/44715968/matplotlib-change-style-of-inset-elements-singularly
    plt.setp(list(ax2.spines.values()), linewidth=0.5, linestyle="--")
    box, c1, c2 = mark_inset(ax, ax2, loc1=3, loc2=4, fc="none",  lw=0.3, ec='0.5')#,
                             #ec=color[0], 
                             #zorder=200)
    #plt.setp(box, linewidth=3, color="grey")
    plt.setp([c1,c2], linestyle=":")
    
    ax2.grid(axis='y', linestyle='-', linewidth=0.3) #True
    ax2.xaxis_date()
    ax2.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
    
    #plt.show()
    # Save figure
    plt.savefig(jparams['distanceTime_conv'])#, dpi=72)
    
# def std_errorDist(df, sd, dist, jparams):
    
#     fig5 = plt.figure(figsize=(12, 6), dpi=80)
#     fig5.suptitle('Standard Deviation Distribution', fontsize=14, fontweight='bold')
#     #formatter = FuncFormatter(to_percent)
#     for i in range(len(sd)):
#         #sdx = data[i+6]
#         sdx = df.iloc[:, 9+i]
#         ax = fig5.add_subplot(1, 3, i+1)
#         #weights = np.ones_like(abs(sdx))/len(sdx)
#         #p = ax.hist(abs(sdx), bins=50, weights=weights)
#         p = ax.hist(sdx, bins=50)#, weights=weights)
#         #ax.yaxis.set_major_formatter(formatter)
#         ax.set_title(sd[i]) 
#         ax.set_ylabel('')
#         ax.set_xlabel('Value')
#         ax.grid(True)
#     #pyplot.show()
#     # Save figure using 72 dots per inch
#     plt.savefig(jparams['std_dist_fig'], dpi=80)
 
def std_errorDist(df,  jparams):    
    
    names = ['std y', 'std x', 'std z']
    
    f, axs = plt.subplots(1, 3, figsize=(9, 6), sharey=True)
    for i in range(len(names)):
        #sdx = df.iloc[:, 9+i]
        #plt.subplot(1, 3, i+1)
        sns.histplot(df.iloc[:, 9+i], bins=50, ax=axs[i]) #kde=True,
        axs[i].set_xlabel(names[i])
    f.suptitle('Standard Deviation Distribution', fontsize=14, fontweight='bold')
    #plt.show()
    # save
    plt.savefig(jparams['std_dist_fig'], dpi=80)
    
def pos_errorDist(df, jparams):
    
    names = ['delta y', 'delta x', 'delta z']
    
    f, axs = plt.subplots(1, 3, figsize=(9, 6), sharey=True)
    for i in range(len(names)):
        #sdx = df.iloc[:, 9+i]
        #plt.subplot(1, 3, i+1)
        sns.histplot(df.iloc[:, 19+i], bins=50, ax=axs[i]) 
                     #kde=True, #stat="probalility", line_kws={'color':'r'})
        #sns.kdeplot(df.iloc[:, 19+i], color="r", stat="probability")
        axs[i].set_xlabel(names[i])
    f.suptitle('Absolute Error', fontsize=14, fontweight='bold')
    #plt.show()
    # save
    plt.savefig(jparams['err_dist_fig'], dpi=80)

# def pos_errorDist(df, sd, dist, jparams):
     
#     fig6 = plt.figure(figsize=(12, 6), dpi=80)
#     fig6.suptitle('Position Error Distribution', fontsize=14, fontweight='bold')
#     #formatter = FuncFormatter(to_percent)
#     for i in range(len(sd)):
#         #sdx = data[i+6]
#         sdx = df.iloc[:, 19+i]
#         ax = fig6.add_subplot(1, 3, i+1)
#         #weights = np.ones_like(abs(sdx))/len(sdx)
#         #p = ax.hist(abs(sdx), bins=50, weights=weights)
#         p = ax.hist(dist[i], bins=50)#, weights=weights)
#         #ax.yaxis.set_major_formatter(formatter)
#         ax.set_title(sd[i]) 
#         ax.set_ylabel('')
#         ax.set_xlabel('Value')
#         ax.grid(True)
#     #pyplot.show()
#     # Save figure using 72 dots per inch
#     plt.savefig(jparams['err_dist_fig'], dpi=80)

def grnd_track_plt(df, jparams):
    
    fig4 = plt.figure(figsize=(12,12))#, dpi=80)
    #plt.title('Center Title')
    fig4.suptitle(jparams['stn_name'] + ' Ground Track and Standard Distribution', fontsize=16, fontweight='bold', 
                  horizontalalignment='center', x=0.46, y=0.90,
                  verticalalignment='top')
    #ax = fig4.add_subplot(111)
    ax = fig4.add_subplot(111, aspect='equal')
    p = ax.scatter(df['x'], df['y'], c=-df['dist(m)'], alpha=0.5, cmap='jet')
    
    #divider = make_axes_locatable(ax)
    #cax = divider.append_axes("right")#, size="5%", pad=0.09)
    fig4.colorbar(p, shrink=0.9)# cax=cax)
    plt.xlim(df['x'].min() - 0.25, df['x'].max() + 0.25)
    plt.ylim(df['y'].min() - 0.25, df['y'].max() + 0.25)
    #ax.xaxis.set_major_locator(MultipleLocator(100))
    #ax.yaxis.set_major_locator(MultipleLocator(100))
    ax.set_xlabel('x (meters)')
    ax.set_ylabel('y (meters)')
    ax.grid(True)
    
    # Save figure using 72 dots per inch
    plt.savefig(jparams['xyz_ground_track_fig'], dpi=72)