"""Volatility module: historical, implied, and 3D surface."""

import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from pricing_engine.black_scholes import black_scholes
from pricing_engine.greeks import compute_greeks


def historical_volatility(ticker, start, end, window=252):
    """Compute annualized historical volatility from Yahoo Finance data.

    Uses log returns over a rolling window.

    Args:
        ticker (str): Ticker symbol to download.
        start (str): Start date (YYYY-MM-DD).
        end (str): End date (YYYY-MM-DD).
        window (int, optional): Rolling window size in trading days. Defaults to 252.

    Returns:
        float: Annualized historical volatility.
    """
    data = yf.download(ticker, start=start, end=end, progress=False)
    returns = data['Close'].pct_change().dropna()
    return float(returns.std() * np.sqrt(252))


def implied_volatility(S, K, r, T, market_price, is_call=True, tol=1e-6, max_iter=100):
    """Compute implied volatility by inverting Black-Scholes (Newton-Raphson).

    Uses the option Vega as the derivative for the Newton-Raphson update.

    Args:
        S (float): Spot price of the underlying asset.
        K (float): Strike price of the option.
        r (float): Risk-free interest rate (annualized).
        T (float): Time to maturity in years.
        market_price (float): Observed market price of the option.
        is_call (bool, optional): True for a call, False for a put. Defaults to True.
        tol (float, optional): Convergence tolerance on the price error. Defaults to 1e-6.
        max_iter (int, optional): Maximum number of iterations. Defaults to 100.

    Returns:
        float: The implied volatility.
    """
    sigma = 0.2  # initial guess
    for _ in range(max_iter):
        price = black_scholes(S, K, r, sigma, T, is_call=is_call)
        vega = compute_greeks(S, K, r, sigma, T, is_call=is_call)['vega']
        if abs(vega) < 1e-10:
            break
        sigma -= (price - market_price) / vega
        if abs(price - market_price) < tol:
            break
    return float(sigma)


def volatility_surface(S, r, sigma_base, strikes, maturities):
    """Build a 3D volatility surface: strikes x maturities x volatility.

    Applies a simple skew on top of a base volatility.

    Args:
        S (float): Spot price of the underlying asset.
        r (float): Risk-free interest rate (annualized).
        sigma_base (float): Base volatility level.
        strikes (array-like): Strike prices.
        maturities (array-like): Maturities in years.

    Returns:
        np.ndarray: 2D array of shape (len(strikes), len(maturities)).
    """
    vol = np.zeros((len(strikes), len(maturities)))
    for i, K in enumerate(strikes):
        for j, T in enumerate(maturities):
            moneyness = K / S
            skew = 0.1 * (moneyness - 1) ** 2
            vol[i, j] = sigma_base + skew
    return vol


def plot_volatility_surface(S, r, sigma_base):
    """Display the 3D volatility surface with Plotly.

    Args:
        S (float): Spot price of the underlying asset.
        r (float): Risk-free interest rate (annualized).
        sigma_base (float): Base volatility level.

    Returns:
        plotly.graph_objects.Figure: The 3D surface figure.
    """
    strikes = np.linspace(S * 0.8, S * 1.2, 20)
    maturities = np.linspace(0.1, 2.0, 20)
    vol = volatility_surface(S, r, sigma_base, strikes, maturities)

    fig = go.Figure(data=[go.Surface(x=maturities, y=strikes, z=vol)])
    fig.update_layout(
        title='Volatility Surface',
        scene=dict(xaxis_title='Maturity (T)',
                   yaxis_title='Strike (K)',
                   zaxis_title='Volatility (σ)'))
    return fig
