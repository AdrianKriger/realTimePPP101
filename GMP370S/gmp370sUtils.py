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


def get_standard_deviation(records):
    """
    """
    std = records.std()  
    return std


def get_rmse(measured, target):

    rmse = mean_squared_error(target, measured, squared=False)

    return rmse
    
def d2(df, target):
    
    rmse = get_rmse(df, target)
    std = get_standard_deviation(df)
    
    return round(rmse, 4), round(std, 4)


def get_rms2d(rms_x, rms_y):
    
    # traditional distance root mean squared error - axis specific
    
    drms2 = round(2 * math.sqrt(rms_x**2 + rms_y**2), 4)

    return drms2

def get_mrse(rms_x, rms_y, rms_z):
    
    # traditional 3D root mean squared error - axis specific
    
    mrse = round(math.sqrt(rms_x**2 + rms_y**2 + rms_z**2), 4)

    return mrse

def get_rms2d2(measured_x, target_x, measured_y, target_y):

    # technically more rigorous
    
    # Twice the DRMS of the horizontal position errors, defining the radius of a circle centered at the 
    # true position, containing the horizontal position estimate with a probability of 95 %.
    # - https://gnss-sdr.org/design-forces/accuracy/ | https://gssc.esa.int/navipedia/index.php/Positioning_Error
        
    # Squaring the sum of differences between columns without looping
    squared_sum = [(measured_x - target_x)**2 + 
                   (measured_y - target_y)**2]
    
    # Summing across all rows
    rms2d2 = math.sqrt(1/len(measured_x) * (np.asarray(squared_sum).sum()))
    
    return rms2d2

def get_mrse2(measured_x, target_x, measured_y, target_y, measured_z, target_z):
    
    # technically more rigorous

    # The radius of a sphere centered at the true position, containing the position estimate in 3D with a 
    # probability of 61 %.
    # - https://gnss-sdr.org/design-forces/accuracy/ | https://gssc.esa.int/navipedia/index.php/Positioning_Error
        
    #mrse = mean_squared_error(measured, [target for _ in measured], squared=False)
    # Squaring the sum of differences between columns without looping
    squared_sum = [(measured_x - target_x)**2 + 
                   (measured_y - target_y)**2 +
                   (measured_z - target_z)**2]
    
    # Summing across all rows
    mrse = math.sqrt(1/len(measured_x) * (np.asarray(squared_sum).sum()))

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
    
    sourcepath = jparams['rtklib_bin']
    sourcefiles = os.listdir(sourcepath)
    #destinationpath = './trace_stats'
    destinationpath =  "/Users/adriankriger/Library/Containers/com.isaacmarovitz.Whisky/Bottles/64DB6BA1-1E03-4FD8-8995-3BD39038654F/drive_c/rtklib_realTime_PPP/trace_stats/"
    
    for file in sourcefiles:
        if file.endswith('.trace'):
            shutil.move(os.path.join(sourcepath, file), os.path.join(destinationpath, file))
        if file.endswith('.stat'):
            shutil.move(os.path.join(sourcepath, file), os.path.join(destinationpath, file))
 
def decimalDegree(degree, minute, second, hemisphere):
    #https://stackoverflow.com/questions/27415327/using-pandas-convert-deg-min-sec-to-decimal-degrees-without-explicitly-iterating
    if hemisphere.lower() in ["w", "s", "west", "south"]:
        factor = -1.0
    elif hemisphere.lower() in ["n", "e", "north", "east"]:
        factor = 1.0
    else:
        raise ValueError("invalid hemisphere")

    # check the order of operations in your code
    #return factor * (degree + (minute + second/60.)/60.)
    return factor * (degree + ((minute / 60) + (second / 3600)))

