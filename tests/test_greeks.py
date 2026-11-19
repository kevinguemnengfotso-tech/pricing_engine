"""Tests for the Greeks module."""

import numpy as np
from pricing_engine.greeks import compute_greeks


def test_greeks_keys():
    # Vérifie que le dict contient bien les 5 Greeks attendus
    g = compute_greeks(S=100, K=105, r=0.05, sigma=0.2, T=1.0)
    assert set(g.keys()) == {'delta', 'gamma', 'theta', 'vega', 'rho'}


def test_delta_call_range():
    # Un call a un Delta entre 0 et 1
    g = compute_greeks(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=True)
    assert 0 <= g['delta'] <= 1


def test_delta_put_range():
    # Un put a un Delta entre -1 et 0
    g = compute_greeks(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=False)
    assert -1 <= g['delta'] <= 0


def test_gamma_positive():
    # Le Gamma est toujours positif (convexité)
    g = compute_greeks(S=100, K=105, r=0.05, sigma=0.2, T=1.0)
    assert g['gamma'] > 0


def test_vega_positive():
    # La Vega est toujours positive (plus de vol = plus de valeur)
    g = compute_greeks(S=100, K=105, r=0.05, sigma=0.2, T=1.0)
    assert g['vega'] > 0


def test_delta_finite_diff():
    # Vérifie le Delta analytique par différence finie sur le prix BS
    eps = 1e-5
    from pricing_engine.black_scholes import black_scholes
    S, K, r, sigma, T = 100, 105, 0.05, 0.2, 1.0
    # Approximation numérique du Delta = dPrix/dS
    fd = (black_scholes(S+eps, K, r, sigma, T) - black_scholes(S-eps, K, r, sigma, T)) / (2*eps)
    g = compute_greeks(S, K, r, sigma, T)
    assert abs(g['delta'] - fd) < 1e-4