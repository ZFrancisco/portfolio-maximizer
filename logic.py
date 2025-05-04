import numpy as np
import pandas as pd
import yfinance as yf

#NOTES
    # keep "weights" instantiation as row vector

R_f = 0.02
R_m = 0.07
tau = 0.025

#HOW IS MY FRONT END GOING TO HANDLE INVESTOR VIEWS?
def picking_matrix(views):
    return 

#tau, maybe can use some other uncertainty views coefficient ? 
def uncertainty_views_matrix(P, sigma):
    return tau * (P @ sigma @ P.T)

def covariance_matrix(tickers):
    data = yf.download(tickers, period="1y", interval="1d")['Adj Close'].dropna().pct_change()
    return pd.cov(data)

def delta(weights, sigma):
    return (R_m - R_f) / (weights @ sigma @ weights.T)

# COV NxN, weights Nx1
def PI(delta, sigma, weights):
    if weights.shape[1] > 1:
        raise TypeError("PASS IN WEIGHTS AS A COLUMN")
    return delta * np.dot(sigma, weights)