"""Option pricing engine: European and American options.

Provides Black-Scholes, Monte Carlo, CRR binomial trees, Greeks,
market data (yfinance) and Treasury curves (FRED).
"""

__version__ = "1.0.0"
__author__ = "Kévin GUEMNENG FOTSO"

from .black_scholes import black_scholes, d1, d2
from .monte_carlo import monte_carlo, convergence_analysis
from .greeks import compute_greeks, delta_hedge
from .binomial import binomial_price
from .market_data import fetch_spy
from .curve import fetch_curve, rate_at

__all__ = [
    "black_scholes", "d1", "d2", "monte_carlo", "convergence_analysis",
    "compute_greeks", "delta_hedge", "binomial_price",
    "fetch_spy", "fetch_curve", "rate_at",
]
