# -*- coding: utf-8 -*-
# env/geomatics01

# author: arkriger

# based on: Chen Chao ~~ https://github.com/heiwa0519/PPPLib/tree/master/tools

# statistical calculations for gnss processing
# mse, rmse, 2drms, mrse and standard deviation

import math
from sklearn.metrics import mean_squared_error


def get_Rollingverage(records):
    
    # ~~ it might be better to have a rolling mean for the standard deviation
    #    - https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rolling.html
    #    
    #    - with an observation per second for :60 minutes = 60 000 window size
    #                                         :30 minutes = 
    #
    #   or pass only the necessary time period [feed the datetime index (120, 60, 45) to the std. dev?
    
    return sum(records)/len(records)


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
    mse = mean_squared_error(measured['x'], [target['x'] for _ in measured['x']], squared=False)
    return mse


def get_rmse(measured, target):
    """
    """
    mse = get_mse(measured, target)
    if mse:
        return math.sqrt(mse)
    else:
        return None
    
def get_2drms(x, y):
    """
    Twice the DRMS of the horizontal position errors, defining the radius of a circle centered at the 
    true position, containing the horizontal position estimate with a probability of 95 %.
    """
    drms2 = 2 * math.sqrt(x**2 + y**2)
    return drms2

def get_mrse(x, y, z):
    """
    The radius of a sphere centered at the true position, containing the position estimate in 3D with a 
    probability of 61 %.
    """
    mrse = math.sqrt(x**2 + y**2 + z**2)
    return mrse   
    
def d2(df, target):
    
    rmse = get_rmse(df, target)
    std = get_standard_deviation(df)
    
    return rmse, std

    
    
    
    
