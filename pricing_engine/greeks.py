"""Greeks computation module for European options.

Ce module calcule les sensibilités (Greeks) d'une option européenne
selon le modèle Black-Scholes, ainsi que le Delta-hedge associé.
"""

import numpy as np                       # Calcul numérique vectorisé
from scipy.stats import norm             # Loi normale : cdf, pdf


def compute_greeks(S, K, r, sigma, T, q=0.0, is_call=True):
    """Calcule Delta, Gamma, Theta, Vega, Rho pour une option européenne."""
    # d1 : rapport log-prix + dérive + convexité, normalisé par la volatilité
    d1_val = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    # d2 : d1 moins la volatilité totale sur la maturité
    d2_val = d1_val - sigma * np.sqrt(T)

    if is_call:
        # Delta call = proba risk-neutral que l'option finisse ITM (× e^-qT)
        delta = np.exp(-q * T) * norm.cdf(d1_val)
        # Theta call : décroissance temporelle (par an) = -temps + dividende - taux
        theta = (-S * np.exp(-q * T) * norm.pdf(d1_val) * sigma / (2 * np.sqrt(T))
                 + q * S * np.exp(-q * T) * norm.cdf(d1_val)
                 - r * K * np.exp(-r * T) * norm.cdf(d2_val))
    else:
        # Delta put = -proba risk-neutral ITM (× e^-qT)
        delta = -np.exp(-q * T) * norm.cdf(-d1_val)
        # Theta put : symétrique du call
        theta = (-S * np.exp(-q * T) * norm.pdf(d1_val) * sigma / (2 * np.sqrt(T))
                 - q * S * np.exp(-q * T) * norm.cdf(-d1_val)
                 + r * K * np.exp(-r * T) * norm.cdf(-d2_val))

    # Gamma : convexité du Delta (même pour call et put)
    gamma = np.exp(-q * T) * norm.pdf(d1_val) / (S * sigma * np.sqrt(T))
    # Vega : sensibilité à la volatilité (même pour call et put)
    vega = S * np.exp(-q * T) * np.sqrt(T) * norm.pdf(d1_val)
    # Rho : sensibilité au taux sans risque
    rho = (K * T * np.exp(-r * T) * norm.cdf(d2_val) if is_call
           else -K * T * np.exp(-r * T) * norm.cdf(-d2_val))

    # Retourne un dict nommé pour lisibilité côté dashboard
    return {'delta': float(delta), 'gamma': float(gamma), 'theta': float(theta),
            'vega': float(vega), 'rho': float(rho)}


def delta_hedge(S, K, r, sigma, T, q=0.0, is_call=True, n_options=1):
    """Calcule le nombre d'actions à acheter/vendre pour être Delta-neutre."""
    # Récupère le Delta de la position option
    g = compute_greeks(S, K, r, sigma, T, q, is_call)
    delta = g['delta']
    # Pour être neutre : acheter -delta actions par option détenue
    shares_to_trade = -delta * n_options
    # Coût du hedge = nombre d'actions × prix spot
    hedge_cost = shares_to_trade * S
    return {'delta': delta, 'shares_to_trade': shares_to_trade, 'hedge_cost': hedge_cost}
