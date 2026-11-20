"""Tests for the Monte Carlo pricing module."""

from pricing_engine.monte_carlo import monte_carlo, convergence_analysis
from pricing_engine.black_scholes import black_scholes


def test_monte_carlo_close_to_bs():
    price = monte_carlo(S=100, K=105, r=0.05, sigma=0.2, T=1.0, n_sim=200000, seed=1)
    bs = black_scholes(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=True)
    assert abs(price - bs) < 0.05


def test_antithetic_reduces_variance():
    p_anti = monte_carlo(S=100, K=105, r=0.05, sigma=0.2, T=1.0, n_sim=50000, antithetic=True, seed=7)
    p_plain = monte_carlo(S=100, K=105, r=0.05, sigma=0.2, T=1.0, n_sim=50000, antithetic=False, seed=7)
    bs = black_scholes(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=True)
    assert abs(p_anti - bs) <= abs(p_plain - bs) + 1e-3


def test_monte_carlo_put():
    price = monte_carlo(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=False, n_sim=100000, seed=2)
    assert price > 0


def test_convergence_analysis():
    res = convergence_analysis(S=100, K=105, r=0.05, sigma=0.2, T=1.0)
    assert 'bs_price' in res
    assert len(res['prices']) == len(res['n_sims'])
    assert res['errors'][-1] <= res['errors'][0] + 1e-3
