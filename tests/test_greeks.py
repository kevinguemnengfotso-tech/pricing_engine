"""Tests for the Greeks module."""

from pricing_engine.greeks import compute_greeks


def test_greeks_keys():
    # Verify the dict contains the 5 expected Greeks
    g = compute_greeks(S=100, K=105, r=0.05, sigma=0.2, T=1.0)
    assert set(g.keys()) == {'delta', 'gamma', 'theta', 'vega', 'rho'}


def test_delta_call_range():
    # A call has a Delta between 0 and 1
    g = compute_greeks(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=True)
    assert 0 <= g['delta'] <= 1


def test_delta_put_range():
    # A put has a Delta between -1 and 0
    g = compute_greeks(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=False)
    assert -1 <= g['delta'] <= 0


def test_gamma_positive():
    # Gamma is always positive (convexity)
    g = compute_greeks(S=100, K=105, r=0.05, sigma=0.2, T=1.0)
    assert g['gamma'] > 0


def test_vega_positive():
    # Vega is always positive (more vol = more value)
    g = compute_greeks(S=100, K=105, r=0.05, sigma=0.2, T=1.0)
    assert g['vega'] > 0


def test_delta_finite_diff():
    # Verify the analytic Delta via finite differences on the BS price
    eps = 1e-5
    from pricing_engine.black_scholes import black_scholes
    S, K, r, sigma, T = 100, 105, 0.05, 0.2, 1.0
    # Numerical approximation of Delta = dPrice/dS
    fd = (black_scholes(S+eps, K, r, sigma, T) - black_scholes(S-eps, K, r, sigma, T)) / (2*eps)
    g = compute_greeks(S, K, r, sigma, T)
    assert abs(g['delta'] - fd) < 1e-4
