"""기술통계 유틸리티."""

from __future__ import annotations

from typing import Optional, Union

import pandas as pd

try:
    from scipy import stats as sp_stats
except ImportError:
    sp_stats = None


def summary_series(s: pd.Series) -> dict:
    """단일 시계열 요약 통계."""
    clean = s.dropna()

    if sp_stats is not None:
        skew_val = float(sp_stats.skew(clean))
        kurt_val = float(sp_stats.kurtosis(clean))
    else:
        skew_val = float(clean.skew())
        kurt_val = float(clean.kurt())

    return {
        "name": s.name,
        "start": s.index.min(),
        "end": s.index.max(),
        "n": len(s),
        "mean": s.mean(),
        "std": s.std(),
        "min": s.min(),
        "max": s.max(),
        "latest": s.iloc[-1] if len(s) > 0 else None,
        "skewness": skew_val,
        "kurtosis": kurt_val,
        "q25": s.quantile(0.25),
        "q50": s.quantile(0.50),
        "q75": s.quantile(0.75),
    }


def summary_df(df: pd.DataFrame) -> pd.DataFrame:
    """전체 DataFrame 요약 통계."""
    rows = [summary_series(df[col]) for col in df.columns]
    return pd.DataFrame(rows).set_index("name")


def describe_ext(df: pd.DataFrame) -> pd.DataFrame:
    """확장 describe (skewness, kurtosis 포함)."""
    base = df.describe().T
    base["skewness"] = df.skew()
    base["kurtosis"] = df.kurt()
    return base
