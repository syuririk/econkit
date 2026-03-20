"""비교 분석 함수."""

from __future__ import annotations

from typing import Optional, Tuple

import pandas as pd


def lead_lag(
    df: pd.DataFrame,
    indicator_a: str,
    indicator_b: str,
    max_lag: int = 4,
) -> pd.Series:
    """리드-래그 상관계수.

    양수 lag → a가 b를 선행, 음수 → b가 a를 선행.
    """
    a, b = df[indicator_a], df[indicator_b]
    results = {}
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            results[lag] = a.corr(b.shift(-lag))
        else:
            results[lag] = a.shift(lag).corr(b)
    return pd.Series(results, name=f"{indicator_a}_lag_{indicator_b}")


def relative_performance(
    df: pd.DataFrame,
    base_period: Optional[str] = None,
) -> pd.DataFrame:
    """기준 시점 대비 상대 성과 (%)."""
    base = df.loc[base_period] if base_period else df.iloc[0]
    return (df / base - 1) * 100


def dispersion(df: pd.DataFrame) -> pd.DataFrame:
    """시점별 지표 간 분산도 (std, range, cv)."""
    result = pd.DataFrame(index=df.index)
    result["std"] = df.std(axis=1)
    result["range"] = df.max(axis=1) - df.min(axis=1)
    result["cv"] = result["std"] / df.mean(axis=1) * 100
    return result


def rolling_correlation(
    df: pd.DataFrame,
    indicator_a: str,
    indicator_b: str,
    window: int = 4,
) -> pd.Series:
    """두 지표 간 이동 상관계수."""
    return df[indicator_a].rolling(window).corr(df[indicator_b])


def pairwise_corr(
    df: pd.DataFrame,
    period: Optional[Tuple[str, str]] = None,
    method: str = "pearson",
) -> pd.DataFrame:
    """전체 / 특정 기간의 지표 간 상관행렬."""
    sub = df.loc[period[0]:period[1]] if period else df
    return sub.corr(method=method)
