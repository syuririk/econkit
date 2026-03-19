"""시계열 분석 함수."""

from __future__ import annotations

from typing import Optional

import pandas as pd
import numpy as np

from econkit.analyze._results import DecompositionResult


def _infer_period(df: pd.DataFrame) -> int:
    """계절 주기 추론."""
    if not isinstance(df.index, pd.DatetimeIndex):
        return 4
    freq = pd.infer_freq(df.index) or ""
    if "Q" in freq:
        return 4
    if "M" in freq:
        return 12
    return 4


def decompose(
    df: pd.DataFrame,
    indicator: str,
    model: str = "additive",
    period: Optional[int] = None,
) -> DecompositionResult:
    """시계열 분해.

    Parameters
    ----------
    indicator : str
        분해할 지표명.
    model : str
        'additive' | 'multiplicative'
    period : int, optional
        계절 주기. 미지정 시 자동 추론.
    """
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose
    except ImportError:
        raise ImportError("pip install statsmodels 를 먼저 실행하세요.")

    s = df[indicator].dropna()
    p = period or _infer_period(df)
    r = seasonal_decompose(s, model=model, period=p, extrapolate_trend="freq")

    return DecompositionResult(
        indicator=indicator,
        observed=r.observed,
        trend=r.trend,
        seasonal=r.seasonal,
        residual=r.resid,
    )


def decompose_all(
    df: pd.DataFrame, **kwargs,
) -> dict[str, DecompositionResult]:
    """전체 지표 일괄 분해."""
    return {col: decompose(df, col, **kwargs) for col in df.columns}


def detect_outliers(
    df: pd.DataFrame,
    indicator: str,
    method: str = "zscore",
    threshold: float = 2.5,
) -> pd.Series:
    """이상값 탐지.

    method: 'zscore' | 'iqr' | 'rolling_zscore'
    """
    s = df[indicator].dropna()

    if method == "zscore":
        mask = ((s - s.mean()) / s.std()).abs() > threshold
    elif method == "iqr":
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        mask = (s < q1 - threshold * iqr) | (s > q3 + threshold * iqr)
    elif method == "rolling_zscore":
        rm = s.rolling(4).mean()
        rs = s.rolling(4).std()
        mask = ((s - rm) / rs).abs() > threshold
    else:
        raise ValueError(f"지원하지 않는 method: {method}")

    return s[mask]


def changepoints(
    df: pd.DataFrame,
    indicator: str,
    window: int = 4,
    threshold_std: float = 1.5,
) -> pd.DatetimeIndex:
    """Rolling std 기준 급변 시점 탐지."""
    s = df[indicator].dropna()
    d = s.diff(1)
    rs = d.rolling(window).std()
    mask = rs.abs() > threshold_std * d.std()
    return s.index[mask.fillna(False)]


def seasonal_pattern(df: pd.DataFrame, indicator: str) -> pd.DataFrame:
    """분기(또는 월)별 평균·표준편차·최솟값·최댓값 패턴."""
    s = df[indicator].dropna()
    freq = pd.infer_freq(df.index) or ""
    freq_unit = "quarter" if "Q" in freq else "month"
    tmp = pd.DataFrame({"value": s, "period": getattr(s.index, freq_unit)})
    return tmp.groupby("period")["value"].agg(["mean", "std", "min", "max"])


def seasonal_adjustment(df: pd.DataFrame, indicator: str) -> pd.Series:
    """계절 조정 시계열 (trend + residual)."""
    dec = decompose(df, indicator)
    return dec.trend + dec.residual


def rolling_volatility(df: pd.DataFrame, indicator: str, window: int = 4) -> pd.Series:
    """이동 표준편차 기반 변동성."""
    return df[indicator].rolling(window).std()


def volatility_table(df: pd.DataFrame, window: int = 4) -> pd.DataFrame:
    """전체 지표 이동 변동성 테이블."""
    return df.rolling(window).std()
