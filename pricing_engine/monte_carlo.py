"""Monte Carlo pricing module for European options."""

import numpy as np

from pricing_engine.black_scholes import black_scholes


def monte_carlo(S, K, r, sigma, T, q=0.0, n_sim=100000, is_call=True, antithetic=True, seed=42):
    rng = np.random.default_rng(seed)
    n = n_sim // 2 if antithetic else n_sim

    Z = rng.standard_normal(n)
    S_T = S * np.exp((r - q - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    payoff = np.maximum(S_T - K, 0) if is_call else np.maximum(K - S_T, 0)

    if antithetic:
        S_T_anti = S * np.exp((r - q - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * (-Z))
        payoff_anti = np.maximum(S_T_anti - K, 0) if is_call else np.maximum(K - S_T_anti, 0)
        payoff = np.concatenate([payoff, payoff_anti])

    return float(np.exp(-r * T) * np.mean(payoff))


def convergence_analysis(S, K, r, sigma, T, q=0.0, is_call=True, n_sims=None):
    if n_sims is None:
        n_sims = [100, 500, 1000, 5000, 10000, 50000, 100000]

    bs_price = black_scholes(S, K, r, sigma, T, q, is_call)
    prices, errors = [], []
    for n in n_sims:
        mc_price = monte_carlo(S, K, r, sigma, T, q, n_sim=n, is_call=is_call)
        prices.append(mc_price)
        errors.append(abs(mc_price - bs_price))

    return {'n_sims': n_sims, 'prices': prices, 'errors': errors, 'bs_price': bs_price}
