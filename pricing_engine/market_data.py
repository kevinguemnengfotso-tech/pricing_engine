"""Fetch real SPY spot and option chain from yfinance."""
from datetime import date
import numpy as np
import yfinance as yf


def fetch_spy():
    """Return spot, filtered call chain, realized vol and time to maturity."""
    t = yf.Ticker("SPY")
    spot = float(t.fast_info["last_price"])
    exp = str(t.options[0])

    chain = t.option_chain(exp).calls.copy()
    chain = chain[
        (chain["bid"] > 0) & (chain["ask"] > chain["bid"]) &
        (chain["impliedVolatility"] > 0) & (chain["openInterest"] > 0)
    ].copy()
    chain["mid"] = (chain["bid"] + chain["ask"]) / 2.0
    chain["T"] = (date.fromisoformat(exp) - date.today()).days / 365.0

    px = t.history(period="3mo")["Close"]
    ret = np.log(px / px.shift(1)).dropna()
    rv = float(ret.tail(30).std() * np.sqrt(252))

    return {"spot": spot, "expiration": exp, "chain": chain,
            "realized_vol": rv, "source": "yfinance"}