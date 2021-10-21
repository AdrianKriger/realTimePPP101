# -*- coding: utf-8 -*-
# - env/geomatics01

# author: arkriger - https://github.com/AdrianKriger/realTimePPP101

import math
from sklearn.metrics import mean_squared_error

import numpy as np

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
    # - this function might not be necessary given the one above can do the necessary
    #
    
    mse = get_mse(measured, target)
    if mse:
        return math.sqrt(mse)
    else:
        return None
    
def d2(df, target):
    
    rmse = get_rmse(df, target)
    std = get_standard_deviation(df)
    
    return rmse, std

def get_rms2d(std_x, std_y):
    
    # Twice the DRMS of the horizontal position errors, defining the radius of a circle centered at the 
    # true position, containing the horizontal position estimate with a probability of 95 %.
    # - https://gnss-sdr.org/design-forces/accuracy/
    
    drms2 = round(2 * math.sqrt(std_x**2 + std_y**2), 4)

    return drms2

def get_mrse(std_x, std_y, std_z):
    
    # The radius of a sphere centered at the true position, containing the position estimate in 3D with a 
    # probability of 61 %.
    # - https://gnss-sdr.org/design-forces/accuracy/
    
    mrse = round(math.sqrt(std_x**2 + std_y**2 + std_z**2), 4)

    return mrse

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
        sdx = df.iloc[:, 8+i]
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
    
def grnd_track_ply(df, distnminlim, distnmaxlim, disteminlim, distemaxlim, jparams):
    
    fig4 = pyplot.figure(figsize=(18,12), dpi=80)
    fig4.suptitle('Position and Standard Distribution', fontsize=14, fontweight='bold')
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