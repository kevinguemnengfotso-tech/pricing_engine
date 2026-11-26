"""Treasury curve from FRED public CSV (no API key)."""
import numpy as np
import pandas as pd

URL = ("https://fred.stlouisfed.org/graph/fredgraph.csv"
       "?id=DGS3MO,DGS1,DGS2,DGS5,DGS10,DGS30")
TENORS = {"DGS3MO": 0.25, "DGS1": 1.0, "DGS2": 2.0,
          "DGS5": 5.0, "DGS10": 10.0, "DGS30": 30.0}


def fetch_curve() -> pd.DataFrame:
    df = pd.read_csv(URL, na_values=["."])
    last = df.dropna(how="all").iloc[-1]
    return pd.DataFrame(
        [{"tenor": t, "rate": float(last[c]) / 100.0}
         for c, t in TENORS.items() if c in last.index and pd.notna(last[c])]
    ).sort_values("tenor")


def rate_at(curve: pd.DataFrame, T: float) -> float:
    """Linear interpolation of zero rates at maturity T."""
    return float(np.interp(T, curve["tenor"], curve["rate"]))