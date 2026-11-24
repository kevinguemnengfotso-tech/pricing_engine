"""Monte Carlo pricing module for European options."""

import numpy as np

from pricing_engine.black_scholes import black_scholes


def monte_carlo(S, K, r, sigma, T, q=0.0, n_sim=100000, is_call=True,
                 antithetic=True, seed=42):
    """Price a European option with Monte Carlo simulation.

    Simulates terminal asset prices under geometric Brownian motion and
    discounts the average payoff.

    Args:
        S (float): Spot price of the underlying asset.
        K (float): Strike price of the option.
        r (float): Risk-free interest rate (annualized).
        sigma (float): Volatility of the underlying (annualized).
        T (float): Time to maturity in years.
        q (float, optional): Continuous dividend yield. Defaults to 0.0.
        n_sim (int, optional): Number of simulated paths. Defaults to 100000.
        is_call (bool, optional): True for a call, False for a put. Defaults to True.
        antithetic (bool, optional): Use antithetic variates to reduce variance.
            Defaults to True.
        seed (int, optional): Seed for the random number generator. Defaults to 42.

    Returns:
        float: The Monte Carlo estimate of the option price.

    Notes:
        When antithetic is True, n_sim // 2 base paths are drawn and their
        negatives are used as the complementary paths, doubling the effective
        sample size while reducing variance.
    """
    rng = np.random.default_rng(seed)
    n = n_sim // 2 if antithetic else n_sim

    Z = rng.standard_normal(n)
    S_T = S * np.exp((r - q - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    payoff = np.maximum(S_T - K, 0) if is_call else np.maximum(K - S_T, 0)

    if antithetic:
        S_T_anti = S * np.exp((r - q - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * (-Z))
        payoff_anti = np.maximum(S_T_anti - K, 0) if is_call else np.maximum(K - S_T_anti, 0)
        payoff = np.concatenate([payoff, payoff_anti])

    return float(np.exp(-r * T) * np.mean(payoff))


def convergence_analysis(S, K, r, sigma, T, q=0.0, is_call=True, n_sims=None):
    """Analyze Monte Carlo convergence against the Black-Scholes price.

    Runs the Monte Carlo pricer for several sample sizes and compares each
    estimate to the closed-form Black-Scholes price.

    Args:
        S (float): Spot price of the underlying asset.
        K (float): Strike price of the option.
        r (float): Risk-free interest rate (annualized).
        sigma (float): Volatility of the underlying (annualized).
        T (float): Time to maturity in years.
        q (float, optional): Continuous dividend yield. Defaults to 0.0.
        is_call (bool, optional): True for a call, False for a put. Defaults to True.
        n_sims (list[int], optional): Sample sizes to test. Defaults to
            [100, 500, 1000, 5000, 10000, 50000, 100000].

    Returns:
        dict: Mapping with keys 'n_sims', 'prices', 'errors', 'bs_price'.
    """
    if n_sims is None:
        n_sims = [100, 500, 1000, 5000, 10000, 50000, 100000]

    bs_price = black_scholes(S, K, r, sigma, T, q, is_call)
    prices, errors = [], []
    for n in n_sims:
        mc_price = monte_carlo(S, K, r, sigma, T, q, n_sim=n, is_call=is_call)
        prices.append(mc_price)
        errors.append(abs(mc_price - bs_price))

    return {'n_sims': n_sims, 'prices': prices, 'errors': errors, 'bs_price': bs_price}
