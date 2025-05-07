import numpy as np
import pandas as pd
import yfinance as yf

#NOTES
    # keep "weights" instantiation as row vector

R_f = 0.02
R_m = 0.07
tau = 0.025

#HOW IS MY FRONT END GOING TO HANDLE INVESTOR VIEWS?
#   [
#       0: view type (relative/absolute)
#       1: ticker A
#       2: ticker B
#       3: view value (positive difference of stock A over B)
#  ]    K X N

def black_litterman_posterior_expected_returns(
    pi, omega, P, Q, tau, sigma):
    term_one = np.linalg.inv(np.linalg.inv(tau * sigma) + (P.T @ np.linalg.inv(omega) @ P))
    term_two = (np.linalg.inv(tau * sigma) @ pi) + (P.T @ np.linalg.inv(omega) @ Q)
    return term_one @ term_two

def picking_matrix(views_dataframe):
    """
    Creates the picking matrix P for Black-Litterman model
    
    Parameters:
    views_dataframe: DataFrame with columns [type, ticker_a, ticker_b, value]
    where type is 'Relative'/'Absolute', ticker_a/b are stock tickers
    
    Returns:
    P: numpy array of shape (num_views, num_assets)
    """
    # Get unique assets and create mapping
    all_tickers = np.unique(views_dataframe.iloc[:, [1,2]].values.ravel())
    ticker_to_idx = {ticker: idx for idx, ticker in enumerate(all_tickers)}
    
    num_views = len(views_dataframe)
    num_assets = len(all_tickers)
    P = np.zeros((num_views, num_assets))
    
    for i, row in views_dataframe.iterrows():
        view_type = row[0]
        ticker_a = row[1]
        ticker_b = row[2]
        
        if view_type == 'Relative':
            # For relative views: stock A will outperform stock B by X%
            # Set 1 for first stock, -1 for second stock
            P[i, ticker_to_idx[ticker_a]] = 1
            P[i, ticker_to_idx[ticker_b]] = -1
        else:  # Absolute view
            # For absolute views: stock A will return X%
            # Set 1 for the stock
            P[i, ticker_to_idx[ticker_a]] = 1
    
    return P, all_tickers

def views_vector(views_dataframe):
    """
    Creates the views vector Q for Black-Litterman model
    
    Parameters:
    views_dataframe: DataFrame with columns [type, ticker_a, ticker_b, value]
    where type is 'Relative'/'Absolute', ticker_a/b are stock tickers
    """
    return np.array(views_dataframe.iloc[:, 3] / 100) # row vector of views

#tau, maybe can use some other uncertainty views coefficient ? 
def uncertainty_views_matrix(P, sigma):
    return tau * (P @ sigma @ P.T)

def covariance_matrix(tickers):
    data = yf.download(tickers, period="1y", interval="1d")['Close']
    data = data.pct_change().dropna()
    return data.cov() * 252

def delta(weights, sigma):
    return (R_m - R_f) / (weights.T @ sigma @ weights)

# COV NxN, weights Nx1
def PI(delta, sigma, weights):
    return delta * np.dot(sigma, weights)

def market_caps(tickers):
    caps = np.array([0] * len(tickers))
    for i, ticker in enumerate(tickers):
        try:
            data = yf.Ticker(ticker).info
            caps[i] = data.get('marketCap', 0)  # Use get() with default value of 0
        except Exception as e:
            print(f"Error getting market cap for {ticker}: {e}")
            caps[i] = 0
    return caps

def calculate(df):
    P, unique_tickers = picking_matrix(df)
    Q = views_vector(df)
    sigma = covariance_matrix(list(unique_tickers))
    omega = uncertainty_views_matrix(P, sigma)
    caps = market_caps(unique_tickers)
    weights = caps / np.sum(caps)
    delta_val = delta(weights, sigma)
    pi = PI(delta_val, sigma, weights)
    posterior_expected_returns = black_litterman_posterior_expected_returns(pi, omega, P, Q, tau, sigma)
    
    # Create a pandas Series with tickers as index and expected returns as values
    expected_returns_mapped = pd.Series(
        posterior_expected_returns, 
        index=unique_tickers,
        name='Expected Returns'
    )
    
    # Sort by expected returns in descending order
    return expected_returns_mapped.sort_values(ascending=False)