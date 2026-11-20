"""Volatility module: historical, implied, and 3D surface."""

import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

from pricing_engine.black_scholes import black_scholes
from pricing_engine.greeks import compute_greeks


def historical_volatility(ticker, start, end, window=252):
    """Vol annualisée depuis Yahoo Finance (rendements log, fenêtre glissante)."""
    data = yf.download(ticker, start=start, end=end, progress=False)
    returns = data['Close'].pct_change().dropna()
    return float(returns.std() * np.sqrt(252))


def implied_volatility(S, K, r, T, market_price, is_call=True, tol=1e-6, max_iter=100):
    """Vol implicite par inversion BS (Newton-Raphson via Vega)."""
    sigma = 0.2  # guess initial
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
    """Surface 3D : strikes × maturités × vol (avec skew simple)."""
    vol = np.zeros((len(strikes), len(maturities)))
    for i, K in enumerate(strikes):
        for j, T in enumerate(maturities):
            moneyness = K / S
            skew = 0.1 * (moneyness - 1) ** 2
            vol[i, j] = sigma_base + skew
    return vol


def plot_volatility_surface(S, r, sigma_base):
    """Affiche la surface 3D avec Plotly."""
    strikes = np.linspace(S * 0.8, S * 1.2, 20)
    maturities = np.linspace(0.1, 2.0, 20)
    vol = volatility_surface(S, r, sigma_base, strikes, maturities)

    fig = go.Figure(data=[go.Surface(x=maturities, y=strikes, z=vol)])
    fig.update_layout(
        title='Surface de volatilité',
        scene=dict(xaxis_title='Maturité (T)',
                   yaxis_title='Strike (K)',
                   zaxis_title='Volatilité (σ)'))
    return fig
