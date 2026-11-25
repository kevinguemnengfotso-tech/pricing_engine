# Rapport de validation — Moteur de pricing d'options européennes

**Projet de portfolio** · Master Finance · Kévin Guemneng Fotso

---

## 1. Introduction

### Contexte

Le pricing de dérivés est au cœur de l'activité des salles de marché. Dans une banque d'investissement, les équipes Quant / Valuation Group développent et maintiennent des moteurs de pricing pour les options, swaps et autres produits dérivés. Ce projet vise à construire, de zéro, un moteur de pricing d'options européennes en Python, en implémentant les modèles fondamentaux de la finance quantitative et en les validant numériquement.

L'objectif n'est pas de rivaliser avec les outils industriels (Bloomberg, Murex), mais de démontrer la maîtrise de la chaîne complète : modélisation, implémentation, tests, visualisation et documentation.

### Objectif

Construire un moteur qui :
- price une option européenne par la formule fermée de Black-Scholes ;
- price la même option par simulation Monte Carlo (GBM) avec réduction de variance ;
- calcule les Greeks (Δ, Γ, Θ, ν, ρ) de manière analytique ;
- propose un dashboard interactif (Streamlit) pour explorer les sensibilités ;
- est accompagné de tests unitaires, d'une CI/CD et d'un rapport technique.

### Périmètre

- Options européennes (call et put) sur une action unique.
- Pas de CVA, pas de volatilité stochastique, pas de produits exotiques.
- Données gratuites (Yahoo Finance), pas de feed temps réel.

---

## 2. Données et paramètres

### Source

- **Yahoo Finance** (`yfinance`) pour les prix historiques des actions.
- Taux sans risque : constante par défaut (`r = 5%`). Pas de fetch FRED implémenté à ce stade.

### Paramètres par défaut

| Paramètre | Symbole | Valeur par défaut |
|---|---|---|
| Prix du sous-jacent | S | 100 |
| Strike | K | 105 |
| Taux sans risque | r | 0.05 |
| Volatilité | σ | 0.20 |
| Maturité | T | 1.0 an |
| Dividende continu | q | 0.0 |

### Volatilité historique

Calculée à partir des rendements quotidiens :

$$\sigma = \text{std}(\text{returns}) \times \sqrt{252}$$

Pour AAPL sur 2023, on obtient environ 27% — valeur indicative, dépendante de la période choisie.

---

## 3. Méthodologie

### 3.1 Black-Scholes

Formule fermée pour le prix d'une option européenne :

$$C = S_0 e^{-qT} N(d_1) - K e^{-rT} N(d_2)$$

avec

$$d_1 = \frac{\ln(S_0/K) + (r - q + \sigma^2/2)T}{\sigma\sqrt{T}}, \qquad d_2 = d_1 - \sigma\sqrt{T}$$

**Hypothèses** : sous-jacent en Mouvement Brownien Géométrique, marché complet, pas de coûts de transaction, volatilité et taux constants, dividendes continus.

**Limites connues** : volatilité constante (le smile de volatilité n'est pas capturé), pas de sauts, pas de risque de crédit.

### 3.2 Monte Carlo

On simule des chemins du sous-jacent selon un GBM :

$$S_T = S_0 \exp\left((r - q - \frac{\sigma^2}{2})T + \sigma\sqrt{T} \cdot Z\right), \quad Z \sim \mathcal{N}(0,1)$$

Le prix est la moyenne actualisée des payoffs : $e^{-rT} \cdot \frac{1}{N}\sum \text{payoff}(S_T^i)$.

**Réduction de variance** : antithetic variates — on tire des chemins corrélés négativement pour réduire l'erreur statistique. La convergence théorique est en $1/\sqrt{N}$.

### 3.3 Greeks

Les sensibilités sont calculées analytiquement. Les formules ci-dessous sont données pour le cas sans dividende ($q = 0$) ; avec un dividende continu, les termes en $S$ sont multipliés par $e^{-qT}$ (voir `pricing_engine/greeks.py` pour les formules complètes).

| Greek | Formule (call, q=0) | Interprétation |
|---|---|---|
| Delta (Δ) | $N(d_1)$ | Sensibilité au prix du sous-jacent |
| Gamma (Γ) | $N'(d_1)/(S\sigma\sqrt{T})$ | Sensibilité du Delta au prix |
| Theta (Θ) | $-S N'(d_1)\sigma/(2\sqrt{T}) - rK e^{-rT}N(d_2)$ | Décroissance temporelle |
| Vega (ν) | $S\sqrt{T}\,N'(d_1)$ | Sensibilité à la volatilité |
| Rho (ρ) | $K T e^{-rT} N(d_2)$ | Sensibilité au taux sans risque |

Ces valeurs sont ensuite utilisées pour dimensionner un hedge Delta-neutre : $\text{shares} = -\Delta \times n_{\text{options}}$, $\text{coût} = \text{shares} \times S$.

### 3.4 Volatilité

- **Historique** : écart-type annualisé des rendements via Yahoo Finance.
- **Implicite** : inversion de Black-Scholes par Newton-Raphson, en utilisant la Vega comme dérivée.
- **Surface 3D** : grille strike × maturité × volatilité, avec un skew simple ($0.1 \times (\text{moneyness}-1)^2$).

---

## 4. Résultats

### 4.1 Comparaison Black-Scholes vs Monte Carlo

| Option | Prix BS | Prix MC (100k sim) | Erreur |
|---|---|---|---|
| Call ATM (S=100, K=100, T=1) | 10.45 | 10.47 | 0.02 |
| Call OTM (S=100, K=105, T=1) | 8.02 | 8.04 | 0.02 |
| Put OTM (S=100, K=95, T=1) | 3.71 | 3.72 | 0.01 |

Monte Carlo converge bien vers Black-Scholes pour les options européennes, avec une erreur de l'ordre de 10⁻² pour 100k simulations.

### 4.2 Convergence Monte Carlo

L'erreur statistique décroît en $1/\sqrt{N}$ (valeurs indicatives, run unique) :

| Simulations (N) | Erreur vs BS |
|---|---|
| 100 | ~0.50 |
| 1 000 | ~0.16 |
| 10 000 | ~0.05 |
| 100 000 | ~0.016 |

L'antithetic variates réduit l'erreur d'environ 30% par rapport à la simulation brute.

### 4.3 Greeks (S=100, K=105, r=5%, σ=20%, T=1)

| Greek | Call | Put |
|---|---|---|
| Delta | 0.54 | -0.46 |
| Gamma | 0.02 | 0.02 |
| Theta | -6.28 | -1.28 |
| Vega | 39.67 | 39.67 |
| Rho | 46.20 | -53.68 |

Les valeurs sont cohérentes avec la théorie : Delta call ∈ [0,1], Delta put ∈ [-1,0], Gamma > 0, Vega > 0.

### 4.4 Vérifications numériques

- **Greeks** : vérifiés par différences finies, écart < 1e-4.
- **Put-call parity** : $C - P = S - K e^{-rT}$, écart < 1e-6.
- **Implied volatility** : roundtrip (BS → IV → BS) à moins de 1e-4.

---

## 5. Validation

| Fichier de test | Nb tests | Ce qui est testé |
|---|---|---|
| `test_black_scholes.py` | 5 | Prix call/put, ATM, T≈0, put-call parity |
| `test_monte_carlo.py` | 4 | Convergence, antithetic, put, convergence analysis |
| `test_greeks.py` | 6 | Keys, Delta call/put, Gamma, Vega, différences finies |
| `test_volatility.py` | 3 | Implied vol roundtrip, forme de la surface, base |

**Total : 18 tests, tous passent.** La couverture n'est pas mesurée (pas de `pytest-cov` configuré).

---

## 6. Limites et perspectives

### Limites assumées

1. **Volatilité constante** — Black-Scholes ne capture pas le smile/skew de volatilité.
2. **Pas de sauts** — le GBM ne modélise pas les crashs ou les annonces.
3. **Marché complet** — hypothèse irréaliste pour certains risques.
4. **Pas de CVA** — le risque de crédit de la contrepartie n'est pas pris en compte.
5. **Pas de volatilité stochastique** — pas de Heston ni de SABR.
6. **Données gratuites** — yfinance, retardé, pas de temps réel.
7. **Taux sans risque constant** — pas de fetch FRED.

### Perspectives

- Implémenter Heston (volatilité stochastique) et Merton (sauts).
- Calibrer la surface de volatilité implicite sur les prix de marché.
- Ajouter le CVA (Monte Carlo + modèle de défaut).
- Étendre aux produits exotiques (barrières, asiatiques).
- Optimiser le noyau de calcul en C++ (pybind11).

---

## 7. Compétences démontrées

| Compétence | Où dans le projet |
|---|---|
| Finance quantitative | Black-Scholes, Monte Carlo, Greeks, hedging, volatilité |
| Python | Architecture modulaire, type hints, docstrings Google style |
| Tests & qualité | 18 tests unitaires, validation numérique, CI/CD |
| Data / visualisation | Dashboard Streamlit, graphiques Plotly (surface 3D) |
| DevOps | Docker, GitHub Actions |

---

## 8. Conclusion

Ce projet implémente les briques fondamentales du pricing de dérivés — Black-Scholes, Monte Carlo, Greeks, hedging — dans un code modulaire, testé et documenté. Les résultats sont cohérents avec la théorie (erreur MC de l'ordre de 10⁻² pour 100k simulations, Greeks vérifiés par différences finies, put-call parity à 1e-6 près). Les hypothèses et limites sont clairement identifiées, ce qui est essentiel pour tout travail quantitatif sérieux.

Les perspectives (Heston, sauts, CVA) sont naturelles pour un projet plus avancé, mais l'ensemble actuel est suffisant pour démontrer une maîtrise solide des fondamentaux du pricing de dérivés et de la programmation.

---

*Rapport de validation — Moteur de pricing d'options européennes (Python).*
*Kévin Guemneng Fotso — Master Finance.*