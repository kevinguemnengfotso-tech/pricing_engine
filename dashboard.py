"""Streamlit dashboard for the European option pricing engine."""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from pricing_engine.black_scholes import black_scholes
from pricing_engine.monte_carlo import monte_carlo
from pricing_engine.greeks import compute_greeks

st.set_page_config(page_title="Option Pricing Engine", layout="wide")
st.title("European Option Pricing Engine")

# --- Sidebar: user inputs ---
st.sidebar.header("Parameters")
S = st.sidebar.slider("Underlying price (S)", 50, 200, 100)
K = st.sidebar.slider("Strike (K)", 50, 200, 105)
r = st.sidebar.slider("Risk-free rate (r)", 0.0, 0.10, 0.05, step=0.001)
sigma = st.sidebar.slider("Volatility (σ)", 0.05, 0.50, 0.20, step=0.01)
T = st.sidebar.slider("Maturity (T in years)", 0.1, 3.0, 1.0, step=0.1)
q = st.sidebar.slider("Dividend yield (q)", 0.0, 0.10, 0.0, step=0.001)
option_type = st.sidebar.selectbox("Option type", ["Call", "Put"])
is_call = option_type == "Call"
n_sim = st.sidebar.slider("Monte Carlo simulations", 1000, 200000, 100000, step=1000)

# --- Calculations ---
price_bs = black_scholes(S, K, r, sigma, T, q, is_call)
price_mc = monte_carlo(S, K, r, sigma, T, q, n_sim, is_call, antithetic=True)
g = compute_greeks(S, K, r, sigma, T, q, is_call)

# --- Price display ---
col1, col2 = st.columns(2)
col1.metric("Black-Scholes price", f"{price_bs:.4f}")
col2.metric("Monte Carlo price", f"{price_mc:.4f}", delta=f"{price_mc - price_bs:.4f}")

# --- Greeks ---
st.subheader("Greeks")
greeks_df = pd.DataFrame({
    "Greek": ["Delta", "Gamma", "Theta", "Vega", "Rho"],
    "Value": [g['delta'], g['gamma'], g['theta'], g['vega'], g['rho']],
    "Interpretation": [
        "Sensitivity to the underlying price",
        "Sensitivity of Delta to the price",
        "Time decay (per day)",
        "Sensitivity to volatility",
        "Sensitivity to the risk-free rate"
    ]
})
st.dataframe(greeks_df, use_container_width=True)

# --- Chart: price vs underlying ---
st.subheader("Option price vs Underlying price")
S_range = np.linspace(S * 0.5, S * 1.5, 100)
prices_bs = [black_scholes(s, K, r, sigma, T, q, is_call) for s in S_range]
prices_mc = [monte_carlo(s, K, r, sigma, T, q, 10000, is_call) for s in S_range]

fig = go.Figure()
fig.add_trace(go.Scatter(x=S_range, y=prices_bs, name="Black-Scholes", line=dict(color='blue')))
fig.add_trace(go.Scatter(x=S_range, y=prices_mc, name="Monte Carlo", line=dict(color='red', dash='dash')))
fig.add_vline(x=S, line_dash="dot", annotation_text="Current S")
fig.add_vline(x=K, line_dash="dot", annotation_text="Strike")
fig.update_layout(xaxis_title="Underlying price (S)", yaxis_title="Option price")
st.plotly_chart(fig, use_container_width=True)

# --- Chart: Delta vs underlying ---
st.subheader("Delta vs Underlying price")
deltas = [compute_greeks(s, K, r, sigma, T, q, is_call)['delta'] for s in S_range]
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=S_range, y=deltas, name="Delta", line=dict(color='green')))
fig2.add_vline(x=S, line_dash="dot", annotation_text="Current S")
fig2.add_vline(x=K, line_dash="dot", annotation_text="Strike")
fig2.update_layout(xaxis_title="Underlying price (S)", yaxis_title="Delta")
st.plotly_chart(fig2, use_container_width=True)

# --- Hedging (Delta-neutral) ---
st.subheader("Hedging (Delta-neutral)")
delta_val = g['delta']
st.write(f"To be **Delta-neutral**, buy/sell **{delta_val:.4f}** shares of the underlying per option.")
st.write(f"Hedge cost: **{delta_val * S:.2f}** (for 1 option).")

# --- Monte Carlo convergence ---
st.subheader("Monte Carlo convergence")
n_sims = [100, 500, 1000, 5000, 10000, 50000, 100000]
mc_prices = [monte_carlo(S, K, r, sigma, T, q, n, is_call) for n in n_sims]
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=n_sims, y=mc_prices, name="Monte Carlo", mode='lines+markers'))
fig3.add_hline(y=price_bs, line_dash="dash", annotation_text="Black-Scholes")
fig3.update_layout(xaxis_title="Number of simulations", yaxis_title="Price", xaxis_type="log")
st.plotly_chart(fig3, use_container_width=True)
