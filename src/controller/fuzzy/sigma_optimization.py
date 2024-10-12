import os
import sys
from scipy.optimize import minimize
import skfuzzy as fuzz
import numpy as np
import pandas as pd


SEGMENTATION_SIZE = 7
BASE = os.path.abspath(os.path.dirname(__file__))

def __get_boundaries(df):
    min_arrival_rate = df['arrival_rate'].min()
    max_arrival_rate = df['arrival_rate'].max()
    
    max_error = max_arrival_rate - min_arrival_rate
    boundaries = np.linspace(-max_error, max_error, SEGMENTATION_SIZE)

    return boundaries


def __get_target_data_and_error_range(df):
    min_arrival_rate = df['arrival_rate'].min()
    max_arrival_rate = df['arrival_rate'].max()

    max_error = max_arrival_rate - min_arrival_rate
    error_range = np.arange(-max_error, max_error)
    target_data = np.exp(-error_range**2 / (2 * 150**2))  # Gaussian profile
    
    return error_range, target_data


def __error_function(params):
    full_csv_path = os.path.join(BASE, "first_check.csv") 
    df = pd.read_csv(full_csv_path)
    error_range, target_data = __get_target_data_and_error_range(df)
    mu, sigma = params
    gauss_mf = fuzz.gaussmf(error_range, mu, sigma)
    error = np.sum((gauss_mf - target_data) ** 2)  # Mean squared error
    return error


def estimate_best_sigma():
    response = []
    full_csv_path = os.path.join(BASE, "first_check.csv") 
    df = pd.read_csv(full_csv_path)
    boundaries = __get_boundaries(df)
    for boundary in boundaries:
        initial_guess = [boundary, 1]
        result = minimize(__error_function, initial_guess, method='Powell')
        optimized_mean, optimized_sigma = result.x
        response.append([optimized_mean, optimized_sigma])
        
    return response