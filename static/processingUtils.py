# -*- coding: utf-8 -*-
# - env/geomatics01

# author: arkriger - https://github.com/AdrianKriger/realTimePPP101

import numpy as np

import matplotlib as mpl
from matplotlib import pyplot
import matplotlib.pylab as pl
import matplotlib.dates as md
#from datetime import *

import matplotlib as mpl

def distTime_std_plt(df, sd, dd, dist, time, jparams):
    
    colors = pl.cm.viridis(np.linspace(0,1,3))
    
    # Create a new figure of size 10x6 points, using 80 dots per inch
    fig1 = pyplot.figure(figsize=(18,12), dpi=80)
    fig1.suptitle('Rover error', fontsize=14, fontweight='bold')
    ax = fig1.add_subplot(2,1,1)
      
    # Make plots
    for i in range(len(sd)):
        ax.plot(time, dist[i], label=dd[i], color=colors[i]) #tdate
    
    # ax.plot(tdate,dist, label='dist')
    ax.grid(True)
    ax.set_ylabel('Absolute Error (m)')
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))
    ax.set_xlabel('Time (s)')
      
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
    ax.set_xlabel('Time (s)')
      
    # Make legend
    pyplot.legend(loc='upper left')
    
    # Save figure using 72 dots per inch
    pyplot.savefig(jparams['distanceTime_std_fig'],dpi=72)