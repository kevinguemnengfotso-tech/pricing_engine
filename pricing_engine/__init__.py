"""European option pricing engine.

Provides Black-Scholes pricing, Monte Carlo pricing, Greeks computation,
Delta hedging, and volatility utilities.
"""

__version__ = "1.0.0"
__author__ = "Kévin GUEMNENG FOTSO"

from .black_scholes import black_scholes, d1, d2
from .monte_carlo import monte_carlo, convergence_analysis
from .greeks import compute_greeks, delta_hedge

__all__ = [
    "black_scholes",
    "d1",
    "d2",
    "monte_carlo",
    "convergence_analysis",
    "compute_greeks",
    "delta_hedge",
]
