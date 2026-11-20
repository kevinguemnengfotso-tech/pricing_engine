"""Black-Scholes pricing module for European options."""

import numpy as np
from scipy.stats import norm


def d1(S: float, K: float, r: float, sigma: float, T: float, q: float = 0.0) -> float:
    """Compute d1 in the Black-Scholes formula."""
    return (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))


def d2(S: float, K: float, r: float, sigma: float, T: float, q: float = 0.0) -> float:
    """Compute d2 in the Black-Scholes formula."""
    return d1(S, K, r, sigma, T, q) - sigma * np.sqrt(T)


def black_scholes(S: float, K: float, r: float, sigma: float, T: float,
                  q: float = 0.0, is_call: bool = True) -> float:
    """Compute the Black-Scholes price of a European option."""
    d1_val = d1(S, K, r, sigma, T, q)
    d2_val = d2(S, K, r, sigma, T, q)

    if is_call:
        return S * np.exp(-q * T) * norm.cdf(d1_val) - K * np.exp(-r * T) * norm.cdf(d2_val)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2_val) - S * np.exp(-q * T) * norm.cdf(-d1_val)
    