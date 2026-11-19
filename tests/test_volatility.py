"""Tests for the volatility module."""

import numpy as np
from volatility import implied_volatility, volatility_surface


def test_implied_volatility_roundtrip():
    # IV doit retrouver sigma à partir d'un prix BS
    from pricing_engine.black_scholes import black_scholes
    S, K, r, T, sigma = 100, 105, 0.05, 1.0, 0.2
    price = black_scholes(S, K, r, sigma, T, is_call=True)
    iv = implied_volatility(S, K, r, T, price, is_call=True)
    assert abs(iv - sigma) < 1e-4


def test_volatility_surface_shape():
    strikes = np.linspace(80, 120, 5)
    maturities = np.linspace(0.1, 2.0, 4)
    vol = volatility_surface(S=100, r=0.05, sigma_base=0.2, strikes=strikes, maturities=maturities)
    assert vol.shape == (5, 4)


def test_volatility_surface_base():
    # Au strike ATM (K=S), le skew est nul → vol = sigma_base
    strikes = np.array([100.0])
    maturities = np.array([1.0])
    vol = volatility_surface(S=100, r=0.05, sigma_base=0.2, strikes=strikes, maturities=maturities)
    assert abs(vol[0, 0] - 0.2) < 1e-9