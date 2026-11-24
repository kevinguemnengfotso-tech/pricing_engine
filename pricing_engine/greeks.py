"""Greeks computation module for European options.

This module computes the price sensitivities (Greeks) of a European option
under the Black-Scholes model, as well as the associated Delta hedge.
"""

import numpy as np
from scipy.stats import norm


def compute_greeks(S, K, r, sigma, T, q=0.0, is_call=True):
    """Compute Delta, Gamma, Theta, Vega and Rho for a European option.

    Args:
        S (float): Spot price of the underlying asset.
        K (float): Strike price of the option.
        r (float): Risk-free interest rate (annualized).
        sigma (float): Volatility of the underlying (annualized).
        T (float): Time to maturity in years.
        q (float, optional): Continuous dividend yield. Defaults to 0.0.
        is_call (bool, optional): True for a call, False for a put. Defaults to True.

    Returns:
        dict: Mapping with keys 'delta', 'gamma', 'theta', 'vega', 'rho'.

    Notes:
        d1 measures the log price ratio plus drift and convexity, normalized
        by volatility. d2 equals d1 minus total volatility over the maturity.

        Delta (call) is the risk-neutral probability that the option finishes
        in the money, scaled by exp(-q*T). Delta (put) is the negative of that
        probability.

        Theta (call) is the time decay per year: -time + dividend - rate.
        Theta (put) is the symmetric of the call theta.

        Gamma is the convexity of Delta (identical for calls and puts).
        Vega is the sensitivity to volatility (identical for calls and puts).
        Rho is the sensitivity to the risk-free rate.
    """
    # d1: log price ratio + drift + convexity, normalized by volatility
    d1_val = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    # d2: d1 minus total volatility over the maturity
    d2_val = d1_val - sigma * np.sqrt(T)

    if is_call:
        # Delta call = risk-neutral probability of finishing ITM (x exp(-q*T))
        delta = np.exp(-q * T) * norm.cdf(d1_val)
        # Theta call: time decay per year = -time + dividend - rate
        theta = (-S * np.exp(-q * T) * norm.pdf(d1_val) * sigma / (2 * np.sqrt(T))
                 + q * S * np.exp(-q * T) * norm.cdf(d1_val)
                 - r * K * np.exp(-r * T) * norm.cdf(d2_val))
    else:
        # Delta put = negative risk-neutral probability of finishing ITM
        delta = -np.exp(-q * T) * norm.cdf(-d1_val)
        # Theta put: symmetric of the call theta
        theta = (-S * np.exp(-q * T) * norm.pdf(d1_val) * sigma / (2 * np.sqrt(T))
                 - q * S * np.exp(-q * T) * norm.cdf(-d1_val)
                 + r * K * np.exp(-r * T) * norm.cdf(-d2_val))

    # Gamma: convexity of Delta (same for calls and puts)
    gamma = np.exp(-q * T) * norm.pdf(d1_val) / (S * sigma * np.sqrt(T))
    # Vega: sensitivity to volatility (same for calls and puts)
    vega = S * np.exp(-q * T) * np.sqrt(T) * norm.pdf(d1_val)
    # Rho: sensitivity to the risk-free rate
    rho = (K * T * np.exp(-r * T) * norm.cdf(d2_val) if is_call
           else -K * T * np.exp(-r * T) * norm.cdf(-d2_val))

    # Return a named dict for readability on the dashboard side
    return {'delta': float(delta), 'gamma': float(gamma), 'theta': float(theta),
            'vega': float(vega), 'rho': float(rho)}


def delta_hedge(S, K, r, sigma, T, q=0.0, is_call=True, n_options=1):
    """Compute the number of shares to buy/sell to be Delta-neutral.

    Args:
        S (float): Spot price of the underlying asset.
        K (float): Strike price of the option.
        r (float): Risk-free interest rate (annualized).
        sigma (float): Volatility of the underlying (annualized).
        T (float): Time to maturity in years.
        q (float, optional): Continuous dividend yield. Defaults to 0.0.
        is_call (bool, optional): True for a call, False for a put. Defaults to True.
        n_options (int, optional): Number of options held. Defaults to 1.

    Returns:
        dict: Mapping with keys 'delta', 'shares_to_trade', 'hedge_cost'.

    Notes:
        Retrieves the Delta of the option position. To be neutral, buy
        -delta shares per option held. Hedge cost = number of shares x spot price.
    """
    # Retrieve the Delta of the option position
    g = compute_greeks(S, K, r, sigma, T, q, is_call)
    delta = g['delta']
    # To be neutral: buy -delta shares per option held
    shares_to_trade = -delta * n_options
    # Hedge cost = number of shares x spot price
    hedge_cost = shares_to_trade * S
    return {'delta': delta, 'shares_to_trade': shares_to_trade, 'hedge_cost': hedge_cost}
