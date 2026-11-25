# Moteur de Pricing d'Options Européennes

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/kevinguemnengfotso-tech/pricing_engine/actions/workflows/ci.yml/badge.svg)](https://github.com/kevinguemnengfotso-tech/pricing_engine/actions)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red.svg)](https://pricing-engine.streamlit.app)

> Moteur de pricing d'options européennes (call/put) : Black-Scholes, Monte Carlo avec réduction de variance, Greeks analytiques, volatilité (historique, implicite, surface 3D) et dashboard Streamlit. Projet de portfolio Master Finance.

---

## Sommaire

- [Vue d'ensemble](#vue-densemble)
- [Résultats clés](#résultats-clés)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Architecture](#architecture)
- [Méthodologie](#méthodologie)
- [Validation](#validation)
- [Limites et perspectives](#limites-et-perspectives)
- [Compétences démontrées](#compétences-démontrées)

---

## Vue d'ensemble

Ce projet implémente, en Python pur, les briques fondamentales du pricing de dérivés :

- **Black-Scholes** : solution analytique fermée pour les options européennes, avec dividendes continus (`q`).
- **Monte Carlo** : simulation de chemins selon un Mouvement Brownien Géométrique, avec antithetic variates et analyse de convergence.
- **Greeks** : sensibilités analytiques (Δ, Γ, Θ, ν, ρ), vérifiées par différences finies.
- **Volatilité** : historique (Yahoo Finance), implicite (inversion par Newton-Raphson) et surface 3D avec skew.
- **Hedging** : dimensionnement d'un portefeuille Delta-neutre.
- **Dashboard Streamlit** : interface interactive pour explorer le pricing et les sensibilités en temps réel.

Le code est modulaire, testé (18 tests) et intégré dans une pipeline CI/CD (GitHub Actions).

---

## Résultats clés

| Indicateur | Valeur |
|---|---|
| Prix Black-Scholes (call, S=100, K=105, r=5%, σ=20%, T=1) | **8.02** |
| Prix Monte Carlo (100k simulations) | **8.04** (erreur ≈ 0.02) |
| Delta (call, K=105) | **0.54** |
| Gamma | **0.02** |
| Vega | **39.67** |
| Tests unitaires | **18** (100% de réussite) |

---

## Installation

### Prérequis
- Python 3.11+
- pip

### Installation locale

```bash
git clone https://github.com/kevinguemnengfotso-tech/pricing_engine.git
cd pricing_engine
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Installation avec Docker

```bash
docker-compose up --build
```

---

## Utilisation

### Dashboard Streamlit

```bash
streamlit run dashboard.py
```

Le dashboard est également déployé sur **[Streamlit Cloud](https://pricing-engine.streamlit.app)**.

### API Python

```python
from pricing_engine.black_scholes import black_scholes
from pricing_engine.monte_carlo import monte_carlo
from pricing_engine.greeks import compute_greeks

S, K, r, sigma, T, q = 100, 105, 0.05, 0.20, 1.0, 0.0

price_bs = black_scholes(S, K, r, sigma, T, q, is_call=True)
price_mc = monte_carlo(S, K, r, sigma, T, q, n_sim=100_000, is_call=True)
g = compute_greeks(S, K, r, sigma, T, q, is_call=True)

print(f"Black-Scholes : {price_bs:.4f}")
print(f"Monte Carlo   : {price_mc:.4f}")
print(f"Delta={g['delta']:.4f}  Gamma={g['gamma']:.4f}  Theta={g['theta']:.4f}")
print(f"Vega={g['vega']:.4f}   Rho={g['rho']:.4f}")
```

---

## Architecture

```
pricing_engine/
├── pricing_engine/             # Package de calcul
│   ├── __init__.py             # Exports publics
│   ├── black_scholes.py        # d1, d2, pricing analytique
│   ├── monte_carlo.py          # Simulation GBM, antithetic, convergence
│   └── greeks.py               # Greeks + dimensionnement du hedge
├── volatility.py               # Vol. historique, implicite, surface 3D
├── dashboard.py                # Interface Streamlit
├── tests/                      # 18 tests unitaires (pytest)
├── reports/report.md           # Rapport de validation technique
├── .github/workflows/ci.yml    # Pipeline CI/CD
├── Dockerfile / docker-compose.yml
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Méthodologie

### 1. Black-Scholes

Solution analytique fermée pour les options européennes (call et put), avec dividendes continus :

$$C = S_0 e^{-qT} N(d_1) - K e^{-rT} N(d_2), \quad d_1 = \frac{\ln(S_0/K)+(r-q+\sigma^2/2)T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T}$$

Hypothèses : volatilité constante, pas de sauts, marché complet, pas de coûts de transaction.

### 2. Monte Carlo

Simulation de chemins selon un Mouvement Brownien Géométrique, avec **antithetic variates** (réduction de variance) et analyse de convergence en $1/\sqrt{N}$.

### 3. Greeks

Sensibilités analytiques (Δ, Γ, Θ, ν, ρ), vérifiées par différences finies (écart < 1e-4). Utilisées pour le dimensionnement d'un hedge Delta-neutre.

### 4. Volatilité

- **Historique** : écart-type annualisé des rendements (`std × √252`) via Yahoo Finance.
- **Implicite** : inversion de Black-Scholes par Newton-Raphson (via Vega).
- **Surface 3D** : strike × maturité × volatilité, avec skew simple.

---

## Validation

| Vérification | Résultat |
|---|---|
| Put-call parity | Écart < 1e-6 |
| Greeks vs différences finies | Écart < 1e-4 |
| Convergence Monte Carlo | Erreur ∝ 1/√N (conforme à la théorie) |
| Tests unitaires | 18 / 18 passent |

---

## Limites et perspectives

**Limites assumées** (conscience des hypothèses du modèle) :
- Volatilité constante (pas de smile/skew capturé par Black-Scholes).
- Pas de sauts de prix (modèle GBM).
- Pas de CVA, pas de volatilité stochastique (Heston), pas de produits exotiques.
- Taux sans risque constant (pas de fetch FRED).
- Couverture de tests non mesurée (pas de `pytest-cov`).

**Perspectives** : Heston, modèles à sauts (Merton), calibration de la surface de volatilité implicite, CVA, produits exotiques, optimisation C++ (pybind11).

---

## Tests

```bash
pytest tests/ -v                              # 18 tests
flake8 pricing_engine/ tests/ --max-line-length=120
black --check pricing_engine/ tests/ dashboard.py volatility.py
```

| Fichier | Tests |
|---|---|
| `test_black_scholes.py` | 5 |
| `test_monte_carlo.py` | 4 |
| `test_greeks.py` | 6 |
| `test_volatility.py` | 3 |

---

## CI/CD

Pipeline GitHub Actions : lint (flake8) + tests (pytest), déclenchée sur `push`/`pull_request` vers `main` et `dev`.

---

## Compétences démontrées

| Domaine | Détail |
|---|---|
| **Finance quantitative** | Black-Scholes, Monte Carlo, Greeks, hedging, volatilité |
| **Python** | Architecture modulaire, type hints, docstrings (Google style) |
| **Tests & qualité** | 18 tests unitaires, validation numérique, CI/CD |
| **Data / viz** | Dashboard Streamlit, graphiques Plotly (surface 3D) |
| **DevOps** | Docker, GitHub Actions |

---

## Auteur

**Kévin Guemneng Fotso** — Projet de portfolio, Master en finance.

## License

MIT License — voir [LICENSE](LICENSE).