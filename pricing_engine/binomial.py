"""Cox-Ross-Rubinstein binomial tree for European and American options."""
import numpy as np


def binomial_price(S, K, r, sigma, T, n=500, is_call=True,
                   american=False, q=0.0) -> float:
    """Price an option by backward induction on a CRR tree."""
    dt = T / n
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    j = np.arange(n + 1)
    ST = S * (u ** j) * (d ** (n - j))
    values = np.maximum(ST - K, 0) if is_call else np.maximum(K - ST, 0)

    for i in range(n - 1, -1, -1):
        values = disc * (p * values[1:] + (1 - p) * values[:-1])
        if american:
            ji = np.arange(i + 1)
            ST_i = S * (u ** ji) * (d ** (i - ji))
            intrinsic = (np.maximum(ST_i - K, 0) if is_call
                         else np.maximum(K - ST_i, 0))
            values = np.maximum(values, intrinsic)
    return float(values[0])