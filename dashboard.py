"""Streamlit dashboard for the pricing engine."""

import streamlit as st                      # Framework web interactif
import numpy as np                          # Calcul numérique
import pandas as pd                         # Tableaux de données
import plotly.graph_objects as go           # Graphiques interactifs

from pricing_engine.black_scholes import black_scholes
from pricing_engine.monte_carlo import monte_carlo
from pricing_engine.greeks import compute_greeks

st.set_page_config(page_title="Moteur de Pricing", layout="wide")
st.title("Moteur de Pricing d'Options Européennes")

# --- Sidebar : inputs utilisateur ---
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
g = compute_greeks(S, K, r, sigma, T, q, is_call)

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
deltas = [compute_greeks(s, K, r, sigma, T, q, is_call)['delta'] for s in S_range]
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