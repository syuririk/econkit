"""기술통계 분석 함수."""

from __future__ import annotations

from typing import Optional, Tuple

import pandas as pd

from econkit.accessor._change import yoy as _yoy


def cumulative(df: pd.DataFrame, base_period: Optional[str] = None) -> pd.DataFrame:
    """기준 시점 대비 누적 변화율 (%)."""
    base = df.loc[base_period] if base_period else df.iloc[0]
    return (df / base - 1) * 100


def correlation(df: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """지표 간 상관계수 행렬."""
    return df.corr(method=method)


def correlation_with(df: pd.DataFrame, target: str, lag: int = 0) -> pd.Series:
    """특정 지표와 나머지 지표 간 상관계수."""
    return df.shift(lag).corrwith(df[target]).drop(target)


def rank_by_change(df: pd.DataFrame, periods: int = 4, ascending: bool = False) -> pd.DataFrame:
    """최근 YoY 변화율 기준 순위."""
    latest = df.pct_change(periods).iloc[-1] * 100
    return latest.sort_values(ascending=ascending).to_frame("yoy_change_%")


def contribution(
    df: pd.DataFrame,
    weights: Optional[dict] = None,
    periods: int = 4,
) -> pd.DataFrame:
    """가중치 기반 기여도."""
    cols = list(df.columns)
    w = weights or {c: 1 / len(cols) for c in cols}
    yoy_df = df.pct_change(periods) * 100
    return yoy_df.apply(
        lambda row: pd.Series({c: row[c] * w.get(c, 0) for c in cols}),
        axis=1,
    )


def period_compare(
    df: pd.DataFrame,
    period_a: Tuple[str, str],
    period_b: Tuple[str, str],
    stat: str = "mean",
) -> pd.DataFrame:
    """두 기간의 통계량 비교."""
    a = getattr(df.loc[period_a[0]:period_a[1]], stat)()
    b = getattr(df.loc[period_b[0]:period_b[1]], stat)()
    return pd.DataFrame({
        "period_a": a,
        "period_b": b,
        "diff": b - a,
        "pct_diff": (b / a - 1) * 100,
    })
