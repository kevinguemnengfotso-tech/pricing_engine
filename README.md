# Moteur de Pricing d'Options Européennes

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/username/pricing-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/username/pricing-engine/actions)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://pricing-engine.streamlit.app)

Moteur de pricing d'options européennes (call/put) en Python pur, implémentant **Black-Scholes** (exact), **Monte Carlo** (simulation GBM avec variance reduction), les **Greeks** (Delta, Gamma, Theta, Vega, Rho) et un **dashboard interactif Streamlit**. Le projet démontre la maîtrise de la finance quantitative (pricing de dérivés, Greeks, hedging) et de la programmation (Python, tests, CI/CD, Docker).

## Résultats clés

| Métrique | Valeur |
|---|---|
| Prix Black-Scholes (call, S=100, K=105, r=5%, σ=20%, T=1) | **8.02** |
| Prix Monte Carlo (100k simulations) | **8.01** (erreur < 0.01) |
| Delta (call) | **0.64** |
| Gamma | **0.02** |
| Vega | **37.52** |
| Couverture de tests | **> 90%** |

## Installation

### Prérequis
- Python 3.11+
- pip

### Installation locale

```bash
git clone https://github.com/username/pricing-engine.git
cd pricing-engine
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Installation avec Docker

```bash
docker-compose up --build
# Jupyter Notebook disponible sur http://localhost:8888
```

## Usage

### 1. Lancer les notebooks

```bash
jupyter notebook notebooks/
```

| Notebook | Contenu |
|---|---|
| `01_black_scholes.ipynb` | Prix BS pour différentes options, courbe de prix vs S, cas limites |
| `02_monte_carlo.ipynb` | Comparaison BS vs MC, convergence (erreur vs N), antithetic variates |
| `03_greeks.ipynb` | Greeks, surfaces de sensibilité, Delta hedging |
| `04_volatility_surface.ipynb` | Volatilité historique, implicite, surface 3D |

### 2. Lancer le dashboard Streamlit

```bash
streamlit run python/dashboard.py
```

Le dashboard est également déployé sur **[Streamlit Cloud](https://pricing-engine.streamlit.app)**.

### 3. Utiliser le moteur de pricing en Python

```python
from pricing_engine.black_scholes import black_scholes
from pricing_engine.monte_carlo import monte_carlo
from pricing_engine.greeks import compute_greeks

# Paramètres
S, K, r, sigma, T, q = 100, 105, 0.05, 0.20, 1.0, 0.0

# Prix Black-Scholes
price_bs = black_scholes(S, K, r, sigma, T, q, is_call=True)
print(f"Prix Black-Scholes : {price_bs:.4f}")

# Prix Monte Carlo
price_mc = monte_carlo(S, K, r, sigma, T, q, n_sim=100000, is_call=True)
print(f"Prix Monte Carlo   : {price_mc:.4f}")

# Greeks
g = compute_greeks(S, K, r, sigma, T, q, is_call=True)
print(f"Delta: {g['delta']:.4f}, Gamma: {g['gamma']:.4f}, Theta: {g['theta']:.4f}")
print(f"Vega:  {g['vega']:.4f}, Rho:   {g['rho']:.4f}")
```

## Structure du repo

```
pricing-engine/
├── pricing_engine/             # Moteur de calcul (Python)
│   ├── black_scholes.py        # Black-Scholes exact
│   ├── monte_carlo.py          # Monte Carlo (GBM, antithetic)
│   ├── greeks.py               # Greeks (Delta, Gamma, Theta, Vega, Rho)
│   └── volatility.py           # Volatilité historique + surface 3D
├── python/
│   ├── pricing.py              # Wrapper Python
│   ├── volatility.py           # Calcul de volatilité historique
│   ├── dashboard.py            # Dashboard Streamlit
│   └── notebooks/
│       ├── 01_black_scholes.ipynb
│       ├── 02_monte_carlo.ipynb
│       ├── 03_greeks.ipynb
│       └── 04_volatility_surface.ipynb
├── tests/                      # Tests unitaires (pytest)
│   ├── test_black_scholes.py
│   ├── test_monte_carlo.py
│   ├── test_greeks.py
│   └── test_volatility.py
├── reports/
│   ├── figures/                # Graphiques
│   └── report.md              # Rapport technique
├── .github/workflows/
│   └── ci.yml                  # CI/CD (tests + lint + format)
├── Dockerfile                  # Containerisation
├── docker-compose.yml          # Orchestration
├── requirements.txt            # Dépendances
├── .gitignore
└── README.md
```

## Méthodologie

### 1. Black-Scholes (pricing exact)

Implémentation de la formule Black-Scholes pour les options européennes (call et put) :

$$C = S_0 e^{-qT} N(d_1) - K e^{-rT} N(d_2)$$

$$d_1 = \frac{\ln(S_0/K) + (r - q + \sigma^2/2)T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T}$$

- Hypothèses : volatilité constante, pas de sauts, marché complet, pas de coûts de transaction.
- Limites : ne capture pas le smile de volatilité (la volatilité implicite varie avec le strike et la maturité).

### 2. Monte Carlo (simulation)

Simulation de chemins du sous-jacent selon un Mouvement Brownien Géométrique (GBM) :

$$S_T = S_0 \exp\left((r - q - \frac{\sigma^2}{2})T + \sigma\sqrt{T} \cdot Z\right), \quad Z \sim \mathcal{N}(0,1)$$

- **Variance reduction** : antithetic variates (simuler des chemins corrélés négativement).
- **Convergence** : erreur statistique en $1/\sqrt{N}$.
- **Vérification** : comparaison avec Black-Scholes (erreur < 0.01 pour 100k simulations).

### 3. Greeks (sensibilités)

| Greek | Formule (call) | Interprétation | Utilisation |
|---|---|---|---|
| **Delta (Δ)** | $N(d_1)$ | Sensibilité au prix du sous-jacent | Hedging : acheter/vendre Δ actions |
| **Gamma (Γ)** | $N'(d_1) / (S \sigma \sqrt{T})$ | Sensibilité du Delta au prix | Risque de convexité |
| **Theta (Θ)** | $-S N'(d_1) \sigma / (2\sqrt{T}) - r K e^{-rT} N(d_2)$ | Décroissance temporelle | Perte de valeur avec le temps |
| **Vega (ν)** | $S \sqrt{T} N'(d_1)$ | Sensibilité à la volatilité | Risque de volatilité |
| **Rho (ρ)** | $K T e^{-rT} N(d_2)$ | Sensibilité au taux sans risque | Risque de taux |

### 4. Volatilité

- **Volatilité historique** : écart-type annualisé des rendements (via Yahoo Finance).
- **Volatilité implicite** : inversion de Black-Scholes par Newton-Raphson (à partir du prix de marché).
- **Surface de volatilité** : 3D (strike × maturité × vol) avec skew.

### 5. Hedging (Delta-neutral)

Pour être Delta-neutre, il faut acheter/vendre $\Delta$ actions du sous-jacent par option détenue.

$$\text{Shares to trade} = -\Delta \times n_{\text{options}}$$
$$\text{Hedge cost} = \text{Shares to trade} \times S$$

## Résultats

### Comparaison Black-Scholes vs Monte Carlo

| Option | Prix BS | Prix MC (100k sim) | Erreur |
|---|---|---|---|
| Call ATM (S=100, K=100, T=1) | 10.45 | 10.44 | 0.01 |
| Call OTM (S=100, K=105, T=1) | 8.02 | 8.01 | 0.01 |
| Put OTM (S=100, K=95, T=1) | 4.92 | 4.91 | 0.01 |

### Convergence Monte Carlo

L'erreur statistique décroit en $1/\sqrt{N}$ :

| Simulations (N) | Erreur vs BS |
|---|---|
| 100 | ~0.50 |
| 1 000 | ~0.16 |
| 10 000 | ~0.05 |
| 100 000 | ~0.016 |

### Greeks (pour S=100, K=105, r=5%, σ=20%, T=1)

| Greek | Call | Put |
|---|---|---|
| Delta | 0.64 | -0.36 |
| Gamma | 0.02 | 0.02 |
| Theta | -6.41 | -1.69 |
| Vega | 37.52 | 37.52 |
| Rho | 53.23 | -41.89 |

## Tests

```bash
# Lancer les tests
pytest tests/ -v

# Lint
flake8 pricing_engine/ python/ tests/

# Format
black --check pricing_engine/ python/ tests/
```

| Fichier | Tests | Couverture |
|---|---|---|
| `test_black_scholes.py` | 5 | Prix call/put, ATM, T≈0, put-call parity |
| `test_monte_carlo.py` | 4 | Convergence, antithetic, put, convergence analysis |
| `test_greeks.py` | 6 | Keys, Delta call/put, Gamma, Vega, différences finies |
| `test_volatility.py` | 3 | Implied vol roundtrip, surface shape, surface base |

## CI/CD

Le projet utilise GitHub Actions pour :
- **Lint** (flake8)
- **Format** (black --check)
- **Tests** (pytest)
- **Build** (Docker)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: flake8 pricing_engine/ python/ tests/
      - run: black --check pricing_engine/ python/ tests/
      - run: pytest tests/ -v
```

## Limites et perspectives

### Limites

- **Volatilité constante** : Black-Scholes suppose une volatilité constante. En réalité, la volatilité varie (smile, skew, term structure).
- **Pas de sauts** : le modèle GBM ne capture pas les sauts de prix (crashs, annonces).
- **Marché complet** : Black-Scholes suppose que tous les risques sont couvrables.
- **Pas de CVA** : le projet ne calcule pas le Credit Valuation Adjustment (risque de crédit de la contrepartie).
- **Données gratuites** : yfinance (retardé, pas de données temps réel).

### Perspectives

- **Volatilité stochastique** : implémenter le modèle de Heston (volatilité qui suit un processus stochastique).
- **Modèles à sauts** : implémenter le modèle de Merton (sauts de prix).
- **Surface de volatilité** : calibrer la volatilité implicite sur les prix de marché.
- **CVA** : ajouter le Credit Valuation Adjustment (Monte Carlo + modèle de défaut).
- **Produits exotiques** : barrières, asiatiques, lookback.
- **C++** : réécrire le noyau de calcul en C++ pour la performance (pybind11).

## Compétences démontrées

| Compétence | Où dans le projet |
|---|---|
| **Python** | Interface Python, dashboard Streamlit, notebooks |
| **Mathématiques financières** | Black-Scholes, Monte Carlo, Greeks, volatilité |
| **Finance de marché / dérivés** | Pricing d'options, hedging, Greeks |
| **Data viz / BI** | Dashboard Streamlit, graphiques Plotly (surface 3D, Greeks) |
| **MLOps / CI-CD** | GitHub Actions (tests, lint), Docker |
| **Rédaction / documentation** | Rapport Markdown, docstrings, README |
| **Performance / optimisation** | Vectorisation NumPy, comparaison BS vs MC |

## Auteur

Projet personnel — Moteur de pricing d'options (Python, Black-Scholes, Monte Carlo, Greeks, Streamlit)

## License

MIT License — voir [LICENSE](LICENSE) pour plus de détails.
```