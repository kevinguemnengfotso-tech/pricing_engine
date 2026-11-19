# Plan détaillé — Projet P9 : Moteur de Pricing Python (Options, Greeks, Monte Carlo)

> **Objectif** : construire un moteur de pricing d'options européennes en Python pur (sans C++) qui implémente Black-Scholes (exact), Monte Carlo (simulation GBM), les Greeks (Delta, Gamma, Theta, Vega, Rho), et un dashboard interactif (Streamlit) pour visualiser les prix et les sensibilités. Le projet démontre la maîtrise de la finance quantitative (pricing de dérivés, Greeks, hedging) et de la programmation (Python, CI/CD, Docker).

---

## Phase 0 — Setup (Jour 1, ~2h)

### 0.1 Créer le repo GitHub

```bash
gh repo create pricing-engine --public --description "Moteur de pricing d'options - Python, Black-Scholes, Monte Carlo, Greeks, Streamlit" --clone
cd pricing-engine
```

**Pourquoi** : repo public pour que les recruteurs puissent voir le code. Description claire pour le référencement GitHub.

### 0.2 Créer la structure

```bash
mkdir -p pricing_engine python/notebooks tests reports/figures .github/workflows
```

**Pourquoi cette structure** :
- `pricing_engine/` : le moteur de calcul (noyau Python). C'est le cœur du projet.
- `python/` : interface Python + dashboard + notebooks. Sépare le moteur de l'interface.
- `tests/` : tests unitaires (pytest). Prouve la qualité.
- `reports/` : rapport + figures. Livrable final.
- `.github/workflows/` : CI/CD. Automatisation.

### 0.3 Environnement Python

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

cat > requirements.txt << 'EOF'
numpy>=1.24
scipy>=1.11
pandas>=2.0
plotly>=5.15
streamlit>=1.28
matplotlib>=3.7
seaborn>=0.12
yfinance>=0.2.28
pytest>=7.4
flake8>=6.0
black>=23.0
joblib>=1.3
EOF
pip install -r requirements.txt
```

**Pourquoi ces librairies** :
- `numpy` : calcul vectorisé (Monte Carlo en une ligne).
- `scipy` : `norm.cdf`, `norm.pdf` pour Black-Scholes.
- `pandas` : manipulation de données (volatilité historique).
- `plotly` : graphiques interactifs (surface de volatilité, Greeks).
- `streamlit` : dashboard public.
- `yfinance` : données historiques pour la volatilité.
- `pytest`, `flake8`, `black` : tests et qualité de code.

### 0.4 .gitignore

```text
.venv/
__pycache__/
*.pyc
*.pkl
.ipynb_checkpoints/
.DS_Store
```

### 0.5 Git initial

```bash
git add . && git commit -m "chore: initial project structure" && git push
```

### 0.6 OpenCode — prompt initial

> *"Crée la structure complète du projet pricing-engine avec les dossiers pricing_engine, python, python/notebooks, tests, reports/figures, .github/workflows. Crée un README.md avec le titre 'Moteur de Pricing d'Options', une description courte, les badges (Python, License, CI), et les sections Installation, Usage, Résultats, Structure, Compétences démontrées. Crée un .gitignore standard Python. Crée un requirements.txt avec numpy, scipy, pandas, plotly, streamlit, matplotlib, seaborn, yfinance, pytest, flake8, black, joblib."*

**Ce que tu dois apprendre** : rien de nouveau (outillage standard).
**Temps** : ~2h (dont 1h OpenCode, 1h vérification).

---

## Phase 1 — Noyau de calcul : Black-Scholes (S1-S2, ~4h)

### 1.1 Implémentation Black-Scholes

**Fichier** : `pricing_engine/black_scholes.py`

```python
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
    """
    Compute the Black-Scholes price of a European option.

    Args:
        S: Spot price of the underlying.
        K: Strike price.
        r: Risk-free rate (annualized).
        sigma: Volatility (annualized).
        T: Time to maturity (in years).
        q: Dividend yield (continuous, annualized).
        is_call: True for call, False for put.

    Returns:
        Option price.
    """
    d1_val = d1(S, K, r, sigma, T, q)
    d2_val = d2(S, K, r, sigma, T, q)

    if is_call:
        return S * np.exp(-q * T) * norm.cdf(d1_val) - K * np.exp(-r * T) * norm.cdf(d2_val)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2_val) - S * np.exp(-q * T) * norm.cdf(-d1_val)
```

**OpenCode prompt** :
> *"Crée le module pricing_engine/black_scholes.py avec les fonctions d1, d2, black_scholes (call et put européens). Ajoute des docstrings Google format. Crée tests/test_black_scholes.py avec pytest : test prix call/put, cas limites (S=K, T=0, sigma=0), comparaison avec valeurs connues. Crée un notebook notebooks/01_black_scholes.ipynb qui calcule le prix pour différentes options et affiche la courbe de prix vs S."*

**Ce que tu dois apprendre** :
- La formule Black-Scholes (d1, d2, N(d1), N(d2)).
- Les hypothèses (volatilité constante, pas de sauts, marché complet).
- `scipy.stats.norm` (cdf, pdf).
- Temps estimé : ~3h de lecture (Hull chapitres 13-15, StatQuest YouTube).

**Livrable** : module Black-Scholes fonctionnel, tests passants, notebook de visualisation.

### 1.2 Vérification numérique (différences finies)

```python
# tests/test_black_scholes.py
import numpy as np
from pricing_engine.black_scholes import black_scholes

def test_black_scholes_call():
    """Test Black-Scholes call price against known value."""
    price = black_scholes(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=True)
    assert abs(price - 8.021) < 0.01  # valeur connue

def test_black_scholes_put():
    """Test Black-Scholes put price against known value."""
    price = black_scholes(S=100, K=105, r=0.05, sigma=0.2, T=1.0, is_call=False)
    assert abs(price - 6.981) < 0.01  # valeur connue

def test_black_scholes_at_the_money():
    """Test at-the-money option (S=K)."""
    price = black_scholes(S=100, K=100, r=0.05, sigma=0.2, T=1.0, is_call=True)
    assert price > 0

def test_black_scholes_zero_maturity():
    """Test at maturity (T=0): price = max(S-K, 0)."""
    price = black_scholes(S=110, K=105, r=0.05, sigma=0.2, T=0.0001, is_call=True)
    assert abs(price - 5.0) < 0.5
```

**Pourquoi des tests** : vérifier que le pricing est correct (comparaison avec des valeurs connues), que les cas limites sont gérés, et que les régressions sont détectées.

### 1.3 Git commit
```bash
git add pricing_engine/black_scholes.py tests/test_black_scholes.py notebooks/01_black_scholes.ipynb
git commit -m "feat: Black-Scholes pricing module with tests and notebook"
git push
```

---

## Phase 2 — Monte Carlo (S2-S3, ~3h)

### 2.1 Implémentation Monte Carlo

**Fichier** : `pricing_engine/monte_carlo.py`

```python
"""Monte Carlo pricing module for European options."""

import numpy as np


def monte_carlo(S: float, K: float, r: float, sigma: float, T: float,
                q: float = 0.0, n_sim: int = 100000,
                is_call: bool = True, antithetic: bool = True,
                seed: int = 42) -> float:
    """
    Compute the Monte Carlo price of a European option.

    Simulates GBM paths and averages the discounted payoffs.

    Args:
        S: Spot price of the underlying.
        K: Strike price.
        r: Risk-free rate (annualized).
        sigma: Volatility (annualized).
        T: Time to maturity (in years).
        q: Dividend yield (continuous, annualized).
        n_sim: Number of simulations.
        is_call: True for call, False for put.
        antithetic: Use antithetic variates for variance reduction.
        seed: Random seed for reproducibility.

    Returns:
        Option price.
    """
    rng = np.random.default_rng(seed)
    n = n_sim // 2 if antithetic else n_sim

    Z = rng.standard_normal(n)
    S_T = S * np.exp((r - q - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
    payoff = np.maximum(S_T - K, 0) if is_call else np.maximum(K - S_T, 0)

    if antithetic:
        S_T_anti = S * np.exp((r - q - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * (-Z))
        payoff_anti = np.maximum(S_T_anti - K, 0) if is_call else np.maximum(K - S_T_anti, 0)
        payoff = np.concatenate([payoff, payoff_anti])

    return np.exp(-r * T) * np.mean(payoff)


def convergence_analysis(S: float, K: float, r: float, sigma: float, T: float,
                        q: float = 0.0, is_call: bool = True,
                        n_sims: list = None) -> dict:
    """
    Analyze Monte Carlo convergence: price and error vs number of simulations.

    Args:
        S, K, r, sigma, T, q: Option parameters.
        is_call: True for call, False for put.
        n_sims: List of simulation counts to test.

    Returns:
        Dictionary with n_sims, prices, errors.
    """
    if n_sims is None:
        n_sims = [100, 500, 1000, 5000, 10000, 50000, 100000]

    bs_price = black_scholes(S, K, r, sigma, T, q, is_call)
    prices = []
    errors = []

    for n in n_sims:
        mc_price = monte_carlo(S, K, r, sigma, T, q, n_sim=n, is_call=is_call)
        prices.append(mc_price)
        errors.append(abs(mc_price - bs_price))

    return {'n_sims': n_sims, 'prices': prices, 'errors': errors, 'bs_price': bs_price}
```

**OpenCode prompt** :
> *"Crée le module pricing_engine/monte_carlo.py avec les fonctions monte_carlo (GBM, antithetic variates, seed fixe) et convergence_analysis (prix et erreur vs nombre de simulations). Crée tests/test_monte_carlo.py (test convergence, test antithetic, test cas limites). Crée un notebook notebooks/02_monte_carlo.ipynb qui compare Black-Scholes vs Monte Carlo pour différentes options et montre la convergence (graphique erreur vs N)."*

**Ce que tu dois apprendre** :
- Simulation Monte Carlo (GBM, payoff, actualisation).
- Variance reduction (antithetic variates) : réduire l'erreur statistique en simulant des chemins corrélés négativement.
- Convergence : l'erreur statistique décroit en 1/√N.
- Temps estimé : ~3h.

**Livrable** : module Monte Carlo fonctionnel, notebook de comparaison, tests.

### 2.2 Git commit
```bash
git add pricing_engine/monte_carlo.py tests/test_monte_carlo.py notebooks/02_monte_carlo.ipynb
git commit -m "feat: Monte Carlo pricing with antithetic variates and convergence analysis"
git push
```

---

## Phase 3 — Greeks (S3-S4, ~3h)

### 3.1 Implémentation des Greeks

**Fichier** : `pricing_engine/greeks.py`

```python
"""Greeks computation module for European options."""

import numpy as np
from scipy.stats import norm


def compute_greeks(S: float, K: float, r: float, sigma: float, T: float,
                   q: float = 0.0, is_call: bool = True) -> dict:
    """
    Compute the Greeks (Delta, Gamma, Theta, Vega, Rho) for a European option.

    Args:
        S: Spot price of the underlying.
        K: Strike price.
        r: Risk-free rate (annualized).
        sigma: Volatility (annualized).
        T: Time to maturity (in years).
        q: Dividend yield (continuous, annualized).
        is_call: True for call, False for put.

    Returns:
        Dictionary with keys: delta, gamma, theta, vega, rho.
    """
    d1_val = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2_val = d1_val - sigma * np.sqrt(T)

    if is_call:
        delta = np.exp(-q * T) * norm.cdf(d1_val)
        theta = (-S * np.exp(-q * T) * norm.pdf(d1_val) * sigma / (2 * np.sqrt(T))
                 + q * S * np.exp(-q * T) * norm.cdf(d1_val)
                 - r * K * np.exp(-r * T) * norm.cdf(d2_val))
    else:
        delta = -np.exp(-q * T) * norm.cdf(-d1_val)
        theta = (-S * np.exp(-q * T) * norm.pdf(d1_val) * sigma / (2 * np.sqrt(T))
                 - q * S * np.exp(-q * T) * norm.cdf(-d1_val)
                 + r * K * np.exp(-r * T) * norm.cdf(-d2_val))

    gamma = np.exp(-q * T) * norm.pdf(d1_val) / (S * sigma * np.sqrt(T))
    vega = S * np.exp(-q * T) * np.sqrt(T) * norm.pdf(d1_val)
    rho = (K * T * np.exp(-r * T) * norm.cdf(d2_val) if is_call
           else -K * T * np.exp(-r * T) * norm.cdf(-d2_val))

    return {
        'delta': delta,
        'gamma': gamma,
        'theta': theta,
        'vega': vega,
        'rho': rho
    }


def delta_hedge(S: float, K: float, r: float, sigma: float, T: float,
                q: float = 0.0, is_call: bool = True,
                n_options: int = 1) -> dict:
    """
    Compute the Delta hedge: how many shares to buy/sell to be Delta-neutral.

    Args:
        S, K, r, sigma, T, q: Option parameters.
        is_call: True for call, False for put.
        n_options: Number of options held.

    Returns:
        Dictionary with delta, shares_to_trade, hedge_cost.
    """
    g = compute_greeks(S, K, r, sigma, T, q, is_call)
    delta = g['delta']

    shares_to_trade = -delta * n_options
    hedge_cost = shares_to_trade * S

    return {
        'delta': delta,
        'shares_to_trade': shares_to_trade,
        'hedge_cost': hedge_cost
    }
```

**OpenCode prompt** :
> *"Crée le module pricing_engine/greeks.py avec les fonctions compute_greeks (Delta, Gamma, Theta, Vega, Rho pour call et put) et delta_hedge (calcul du Delta hedge). Crée tests/test_greeks.py (test Greeks analytiques vs différences finies, test cas limites). Crée un notebook notebooks/03_greeks.ipynb qui calcule les Greeks pour différentes options, affiche les surfaces de sensibilité (Delta vs S et T, Vega vs S et σ), et montre comment hedger une position (Delta hedging)."*

**Ce que tu dois apprendre** :
- Les Greeks et leur interprétation (Delta = sensibilité au prix, Gamma = convexité, Theta = décroissance temporelle, Vega = sensibilité à la volatilité, Rho = sensibilité au taux).
- Hedging : combien d'actions acheter/vendre pour être neutre au risque.
- Surfaces de sensibilité (3D).
- Temps estimé : ~3h.

**Livrable** : module Greeks fonctionnel, notebook de visualisation, tests.

### 3.2 Git commit
```bash
git add pricing_engine/greeks.py tests/test_greeks.py notebooks/03_greeks.ipynb
git commit -m "feat: Greeks computation (Delta, Gamma, Theta, Vega, Rho) with hedging"
git push
```

---

## Phase 4 — Volatilité historique + surface (S4-S5, ~2h)

### 4.1 Calcul de volatilité

**Fichier** : `python/volatility.py`

```python
"""Volatility computation module: historical and implied volatility."""

import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go


def historical_volatility(ticker: str, start: str, end: str,
                          window: int = 252) -> float:
    """
    Compute annualized historical volatility from Yahoo Finance data.

    Args:
        ticker: Stock ticker (e.g., 'AAPL', '^GSPC').
        start: Start date (YYYY-MM-DD).
        end: End date (YYYY-MM-DD).
        window: Rolling window in days (default 252 = 1 year).

    Returns:
        Annualized volatility.
    """
    data = yf.download(ticker, start=start, end=end)
    returns = data['Close'].pct_change().dropna()
    sigma = returns.std() * np.sqrt(252)
    return sigma


def implied_volatility(S: float, K: float, r: float, T: float,
                       market_price: float, is_call: bool = True,
                       tol: float = 1e-6, max_iter: int = 100) -> float:
    """
    Compute implied volatility by inverting Black-Scholes.

    Uses Newton-Raphson method.

    Args:
        S, K, r, T: Option parameters.
        market_price: Observed market price of the option.
        is_call: True for call, False for put.
        tol: Tolerance for convergence.
        max_iter: Maximum iterations.

    Returns:
        Implied volatility.
    """
    from pricing_engine.black_scholes import black_scholes
    from pricing_engine.greeks import compute_greeks

    sigma = 0.2  # initial guess
    for _ in range(max_iter):
        price = black_scholes(S, K, r, sigma, T, is_call=is_call)
        vega = compute_greeks(S, K, r, sigma, T, is_call=is_call)['vega']
        if abs(vega) < 1e-10:
            break
        sigma -= (price - market_price) / vega
        if abs(price - market_price) < tol:
            break
    return sigma


def volatility_surface(S: float, r: float, sigma_base: float,
                       strikes: np.ndarray, maturities: np.ndarray) -> np.ndarray:
    """
    Compute a volatility surface (3D: strike × maturity × vol).

    For simplicity, uses a flat vol with a skew adjustment.

    Args:
        S: Spot price.
        r: Risk-free rate.
        sigma_base: Base volatility.
        strikes: Array of strike prices.
        maturities: Array of maturities.

    Returns:
        2D array of volatilities (strikes × maturities).
    """
    vol_surface = np.zeros((len(strikes), len(maturities)))
    for i, K in enumerate(strikes):
        for j, T in enumerate(maturities):
            # Simple skew: vol increases for deep ITM/OTM
            moneyness = K / S
            skew = 0.1 * (moneyness - 1)**2
            vol_surface[i, j] = sigma_base + skew
    return vol_surface


def plot_volatility_surface(S: float, r: float, sigma_base: float):
    """Plot the 3D volatility surface."""
    strikes = np.linspace(S * 0.8, S * 1.2, 20)
    maturities = np.linspace(0.1, 2.0, 20)
    vol = volatility_surface(S, r, sigma_base, strikes, maturities)

    fig = go.Figure(data=[go.Surface(x=maturities, y=strikes, z=vol)])
    fig.update_layout(
        title='Surface de volatilité',
        scene=dict(
            xaxis_title='Maturité (T)',
            yaxis_title='Strike (K)',
            zaxis_title='Volatilité (σ)'
        )
    )
    fig.show()
    return fig
```

**OpenCode prompt** :
> *"Crée le module python/volatility.py avec : 1) historical_volatility(ticker, start, end) qui télécharge les prix via yfinance et calcule la volatilité annualisée. 2) implied_volatility(S, K, r, T, market_price) qui inverse Black-Scholes par Newton-Raphson. 3) volatility_surface(S, r, sigma_base, strikes, maturities) qui calcule une surface de volatilité 3D. 4) plot_volatility_surface(S, r, sigma_base) qui affiche la surface 3D avec Plotly. Crée un notebook notebooks/04_volatility_surface.ipynb."*

**Ce que tu dois apprendre** :
- Volatilité historique vs implicite.
- Smile de volatilité (pourquoi Black-Scholes est limité).
- Surface de volatilité (3D).
- Temps estimé : ~2h.

**Livrable** : module de volatilité, notebook de visualisation.

### 4.2 Git commit
```bash
git add python/volatility.py notebooks/04_volatility_surface.ipynb
git commit -m "feat: historical/implied volatility and 3D volatility surface"
git push
```

---

## Phase 5 — Dashboard Streamlit (S5-S6, ~2h)

### 5.1 Dashboard Streamlit

**Fichier** : `python/dashboard.py`

```python
"""Streamlit dashboard for the pricing engine."""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from pricing_engine.pricing import black_scholes, monte_carlo, greeks

st.set_page_config(page_title="Moteur de Pricing", layout="wide")
st.title("Moteur de Pricing d'Options Européennes")

# --- Sidebar : inputs ---
st.sidebar.header("Paramètres")
S = st.sidebar.slider("Prix du sous-jacent (S)", 50, 200, 100)
K = st.sidebar.slider("Strike (K)", 50, 200, 105)
r = st.sidebar.slider("Taux sans risque (r)", 0.0, 0.10, 0.05, step=0.001)
sigma = st.sidebar.slider("Volatilité (σ)", 0.05, 0.50, 0.20, step=0.01)
T = st.sidebar.slider("Maturité (T en années)", 0.1, 3.0, 1.0, step=0.1)
q = st.sidebar.slider("Dividende (q)", 0.0, 0.10, 0.0, step=0.001)
option_type = st.sidebar.selectbox("Type d'option", ["Call", "Put"])
is_call = option_type == "Call"
n_sim = st.sidebar.slider("Simulations Monte Carlo", 1000, 200000, 100000, step=1000)

# --- Calculs ---
price_bs = black_scholes(S, K, r, sigma, T, q, is_call)
price_mc = monte_carlo(S, K, r, sigma, T, q, n_sim, is_call, antithetic=True)
g = greeks(S, K, r, sigma, T, q, is_call)

# --- Affichage des prix ---
col1, col2 = st.columns(2)
col1.metric("Prix Black-Scholes", f"{price_bs:.4f}")
col2.metric("Prix Monte Carlo", f"{price_mc:.4f}", delta=f"{price_mc - price_bs:.4f}")

# --- Greeks ---
st.subheader("Greeks")
greeks_df = pd.DataFrame({
    "Greek": ["Delta", "Gamma", "Theta", "Vega", "Rho"],
    "Valeur": [g['delta'], g['gamma'], g['theta'], g['vega'], g['rho']],
    "Interprétation": [
        "Sensibilité au prix du sous-jacent",
        "Sensibilité du Delta au prix",
        "Décroissance temporelle (par jour)",
        "Sensibilité à la volatilité",
        "Sensibilité au taux sans risque"
    ]
})
st.dataframe(greeks_df, use_container_width=True)

# --- Graphique : prix vs S ---
st.subheader("Prix de l'option vs Prix du sous-jacent")
S_range = np.linspace(S * 0.5, S * 1.5, 100)
prices_bs = [black_scholes(s, K, r, sigma, T, q, is_call) for s in S_range]
prices_mc = [monte_carlo(s, K, r, sigma, T, q, 10000, is_call) for s in S_range]

fig = go.Figure()
fig.add_trace(go.Scatter(x=S_range, y=prices_bs, name="Black-Scholes", line=dict(color='blue')))
fig.add_trace(go.Scatter(x=S_range, y=prices_mc, name="Monte Carlo", line=dict(color='red', dash='dash')))
fig.add_vline(x=S, line_dash="dot", annotation_text="S actuel")
fig.add_vline(x=K, line_dash="dot", annotation_text="Strike")
fig.update_layout(xaxis_title="Prix du sous-jacent (S)", yaxis_title="Prix de l'option")
st.plotly_chart(fig, use_container_width=True)

# --- Graphique : Delta vs S ---
st.subheader("Delta vs Prix du sous-jacent")
deltas = [greeks(s, K, r, sigma, T, q, is_call)['delta'] for s in S_range]
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=S_range, y=deltas, name="Delta", line=dict(color='green')))
fig2.add_vline(x=S, line_dash="dot", annotation_text="S actuel")
fig2.add_vline(x=K, line_dash="dot", annotation_text="Strike")
fig2.update_layout(xaxis_title="Prix du sous-jacent (S)", yaxis_title="Delta")
st.plotly_chart(fig2, use_container_width=True)

# --- Hedging ---
st.subheader("Hedging (Delta-neutral)")
delta_val = g['delta']
st.write(f"Pour être **Delta-neutre**, acheter/vendre **{delta_val:.4f}** actions du sous-jacent par option.")
st.write(f"Coût du hedge : **{delta_val * S:.2f}** (pour 1 option).")

# --- Convergence Monte Carlo ---
st.subheader("Convergence Monte Carlo")
n_sims = [100, 500, 1000, 5000, 10000, 50000, 100000]
mc_prices = [monte_carlo(S, K, r, sigma, T, q, n, is_call) for n in n_sims]
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=n_sims, y=mc_prices, name="Monte Carlo", mode='lines+markers'))
fig3.add_hline(y=price_bs, line_dash="dash", annotation_text="Black-Scholes")
fig3.update_layout(xaxis_title="Nombre de simulations", yaxis_title="Prix", xaxis_type="log")
st.plotly_chart(fig3, use_container_width=True)
```

**OpenCode prompt** :
> *"Crée un dashboard Streamlit (python/dashboard.py) avec : 1) Inputs : S, K, r, σ, T, q, type d'option (call/put). 2) Outputs : prix Black-Scholes, prix Monte Carlo, Greeks (Delta, Gamma, Theta, Vega, Rho). 3) Graphiques : courbe de prix vs S, courbe de Delta vs S, surface de volatilité 3D. 4) Comparaison Black-Scholes vs Monte Carlo (convergence). 5) Section 'Hedging' : combien d'actions acheter/vendre pour être Delta-neutre."*

**Ce que tu dois apprendre** :
- Streamlit (inputs, outputs, graphiques).
- Plotly (graphiques interactifs).
- Temps estimé : ~2h.

**Livrable** : dashboard Streamlit fonctionnel, déployable sur Streamlit Cloud.

### 5.2 Git commit
```bash
git add python/dashboard.py
git commit -m "feat: Streamlit dashboard with pricing, Greeks, hedging, convergence"
git push
```

---

## Phase 6 — Rapport + README + CI + Docker (S6-S7, ~2h)

### 6.1 Rapport

**OpenCode prompt** :
> *"Crée un rapport reports/report.md avec : 1) Introduction (pricing de dérivés, Black-Scholes, Monte Carlo). 2) Implémentation (noyau Python, interface, dashboard). 3) Résultats (comparaison Black-Scholes vs Monte Carlo, Greeks, surface de volatilité). 4) Limites (volatilité constante, pas de sauts, pas de CVA). 5) Perspectives (volatilité stochastique, modèles à sauts, xVA). Crée un README.md avec badges, installation, usage, résultats, structure, compétences démontrées. Crée .github/workflows/ci.yml (tests Python, lint). Crée un Dockerfile."*

### 6.2 Ce que tu dois apprendre
- GitHub Actions pour Python (tests, lint).
- Docker pour Python.
- Temps estimé : ~2h.

### 6.3 Git commit final
```bash
git add reports/report.md README.md .github/workflows/ci.yml Dockerfile docker-compose.yml
git commit -m "chore: README, CI/CD, Docker, final polish"
git push

# Tag la release
git tag -a v1.0 -m "Release v1.0 - Moteur de Pricing Python"
git push --tags
```

---

## 7. Métriques d'évaluation

| Métrique | Objectif | Seuil "bon" |
|---|---|---|
| **Erreur Black-Scholes vs Monte Carlo** | Vérifier que le MC converge vers le BS | < 0.01 (pour 100k simulations) |
| **Convergence Monte Carlo** | Erreur statistique en fonction de N | Erreur ∝ 1/√N |
| **Greeks numériques vs analytiques** | Vérifier les Greeks par différences finies | Écart < 1e-4 |
| **Tests unitaires** | Couverture de code | > 90 % |

## 8. Ce que le projet démontre sur le CV

| Compétence demandée (niveau) | Où dans le projet |
|---|---|
| **Python** (5) | Interface Python, dashboard Streamlit, notebooks |
| **Mathématiques financières** (4) | Black-Scholes, Monte Carlo, Greeks, volatilité |
| **Finance de marché / dérivés** (4) | Pricing d'options, hedging, Greeks |
| **Data viz / BI** (3) | Dashboard Streamlit, graphiques Plotly (surface de volatilité, Greeks) |
| **MLOps / CI-CD** (3) | GitHub Actions (tests, lint), Docker |
| **Rédaction / documentation** (2) | Rapport Markdown avec résultats, limites, perspectives |
| **Performance / optimisation** (2) | Comparaison Python vs C++ (si bonus), vectorisation NumPy |

## 9. Offres ciblées

| Offre | Ce que le projet démontre |
|---|---|
| **Natixis IT Quant Equity Pricing** (C++, IA pour automatiser flux XML, Sophis) | Pricing, automatisation, performance |
| **Natixis Valuation Group** (P&L, IPV, FairVA, IA/ML pour analyse) | Pricing de dérivés, valorisation, Greeks |
| **Natixis Développeur Python Finance** (Python, dérivés, valorisation) | Python, pricing, dérivés |
| **Forvis Mazars Finance Quantitative** (dérivés complexes, xVA, ML/DL, C++, Python, R) | Pricing, dérivés, Python, xVA (perspective) |
| **EY Quantitative Advisory Services** (pricing dérivés, xVAs, FRTB, SA-CCR) | Pricing, dérivés, xVA (perspective), validation de modèles |
| **HSBC produits structurés banque privée** | Pricing de produits structurés, dérivés |
| **Orange Lease** (modélisation financière, Excel) | Modélisation financière, pricing |
| **Amundi** (structuration ETF & Indiciel) | Structuration de produits, pricing |
| **SCOR** (réassurance, IFRS 17, Solvency II) | Modélisation, pricing, risque |

## 10. Résultat attendu sur le CV

> **"Projet personnel — Moteur de pricing d'options (Python, Black-Scholes, Monte Carlo, Greeks, Streamlit)"**
> - Moteur de pricing d'options européennes (Black-Scholes exact, Monte Carlo GBM) en Python
> - Calcul des Greeks (Delta, Gamma, Theta, Vega, Rho) et hedging (Delta-neutral)
> - Dashboard Streamlit interactif : prix, Greeks, surface de volatilité, comparaison BS vs MC
> - Tests unitaires (pytest), CI GitHub Actions, Docker
> - **Compétences démontrées** : Python, mathématiques financières, pricing de dérivés, Greeks, hedging, MLOps
> - **Lien GitHub** : github.com/[user]/pricing-engine

---

## 11. Résumé : le workflow professionnel

```
Jour 1  : Setup (repo, structure, venv, git)          → Phase 0
Jour 2-3: Black-Scholes + tests + notebook            → Phase 1  (commit 1)
Jour 4  : Monte Carlo + convergence + notebook        → Phase 2  (commit 2)
Jour 5-6: Greeks + surfaces + hedging + notebook      → Phase 3  (commit 3)
Jour 7  : Volatilité + surface 3D + notebook         → Phase 4  (commit 4)
Jour 8-9: Dashboard Streamlit + hedging + convergence  → Phase 5  (commit 5)
Jour 10 : Rapport + README + CI + Docker + Tag v1.0   → Phase 6  (commit 6)
```

### Principes pro appliqués

| Principe | Comment |
|---|---|
| **Git workflow** | 1 commit par phase, messages conventionnels (feat:, chore:, fix:) |
| **Tests** | pytest pour chaque module (black_scholes, monte_carlo, greeks, volatility) |
| **CI/CD** | GitHub Actions : tests + lint (flake8) + format (black) |
| **Documentation** | README.md + rapport Markdown + docstrings dans le code |
| **Reproductibilité** | Dockerfile + requirements.txt + données versionnées |
| **Revue de code** | Relire le code généré par OpenCode avant de committer |
| **Versionnage** | Tag v1.0 pour la release finale |

### Ce que tu dois apprendre (minimum)

| Sujet | Temps | Ressource |
|---|---|---|
| Black-Scholes (formule, hypothèses, limites) | ~2h | Hull chapitres 13-15, StatQuest YouTube |
| Monte Carlo (GBM, payoff, actualisation, variance reduction) | ~2h | Glasserman chapitres 1-4, StatQuest YouTube |
| Greeks (Delta, Gamma, Theta, Vega, Rho) | ~2h | Hull chapitre 17, StatQuest YouTube |
| Hedging (Delta-neutral, Gamma hedging) | ~1h | Hull chapitre 18 |
| Volatilité (historique vs implicite, smile) | ~1h | Gatheral "The Volatility Surface" chapitres 1-3 |
| Streamlit (inputs, outputs, graphiques) | ~1h | Streamlit docs |
| Plotly (graphiques interactifs) | ~1h | Plotly docs |
| **Total** | **~10h** | Réparti sur 10 jours |

### Prompts OpenCode par phase

| Phase | Prompt OpenCode |
|---|---|
| 0 | *"Crée la structure du projet avec les dossiers... Crée README, .gitignore, requirements.txt"* |
| 1 | *"Crée le module pricing_engine/black_scholes.py avec les fonctions d1, d2, black_scholes (call et put). Crée tests/test_black_scholes.py. Crée un notebook 01_black_scholes.ipynb."* |
| 2 | *"Crée le module pricing_engine/monte_carlo.py avec monte_carlo (GBM, antithetic) et convergence_analysis. Crée tests/test_monte_carlo.py. Crée un notebook 02_monte_carlo.ipynb."* |
| 3 | *"Crée le module pricing_engine/greeks.py avec compute_greeks (Delta, Gamma, Theta, Vega, Rho) et delta_hedge. Crée tests/test_greeks.py. Crée un notebook 03_greeks.ipynb."* |
| 4 | *"Crée le module python/volatility.py avec historical_volatility, implied_volatility, volatility_surface, plot_volatility_surface. Crée un notebook 04_volatility_surface.ipynb."* |
| 5 | *"Crée un dashboard Streamlit (python/dashboard.py) avec inputs (S, K, r, σ, T, q, type), outputs (prix BS, prix MC, Greeks), graphiques (prix vs S, Delta vs S, surface 3D), comparaison BS vs MC, section hedging."* |
| 6 | *"Crée un rapport reports/report.md, un README.md, .github/workflows/ci.yml, et un Dockerfile. Tag la release v1.0."* |

> **Principe clé** : OpenCode génère le code, tu relis, tu comprends, tu testes, tu committes. Tu ne copies pas aveuglément. Chaque module a des tests — si les tests passent, le code est correct. Si les tests échouent, OpenCode corrige.

---

*Plan pour le projet P9 — Moteur de Pricing Python (Options, Greeks, Monte Carlo). Durée : 7 semaines (S1-S7). Apprentissage : ~10h. Utilisation d'OpenCode pour accélérer le développement. 100 % Python, pas de C++.*