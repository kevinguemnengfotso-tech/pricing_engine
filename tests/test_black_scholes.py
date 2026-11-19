"""Tests for the Black-Scholes pricing module."""

import numpy as np
from pricing_engine.black_scholes import black_scholes


def test_black_scholes_call():
    """Test Black-Scholes call price against known value."""
    price = black_scholes(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=True)
    assert abs(price - 8.021) < 0.01


def test_black_scholes_put():
    """Test Black-Scholes put price against known value."""
    price = black_scholes(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=False)
    assert abs(price - 7.900) < 0.01


def test_black_scholes_at_the_money():
    """Test at-the-money option (S=K)."""
    price = black_scholes(S=100, K=100, r=0.05, sigma=0.2, T=1.0, is_call=True)
    assert price > 0


def test_black_scholes_zero_maturity():
    """Test near maturity (T~0): price ~ max(S-K, 0)."""
    price = black_scholes(S=110, K=105, r=0.05, sigma=0.2, T=0.0001, is_call=True)
    assert abs(price - 5.0) < 0.5


def test_put_call_parity():
    """Verify put-call parity: C - P = S - K*exp(-rT)."""
    S, K, r, sigma, T = 100, 105, 0.05, 0.2, 1.0
    call = black_scholes(S, K, r, sigma, T, is_call=True)
    put = black_scholes(S, K, r, sigma, T, is_call=False)
    assert abs((call - put) - (S - K * np.exp(-r * T))) < 1e-6