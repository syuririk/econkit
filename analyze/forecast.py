"""예측 모델 — 선형 추세, ARIMA, 이동평균 연장."""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from econkit.analyze._results import ForecastResult


def _infer_freq(df: pd.DataFrame) -> Optional[str]:
    """DataFrame 인덱스에서 빈도 추론."""
    if isinstance(df.index, pd.DatetimeIndex):
        return pd.infer_freq(df.index)
    return None


def linear_trend(
    df: pd.DataFrame,
    indicator: str,
    steps: int = 4,
    window: Optional[int] = None,
    confidence: float = 0.95,
) -> ForecastResult:
    """선형 회귀 추세선 연장 예측.

    Parameters
    ----------
    indicator : str
        예측할 지표명.
    steps : int
        예측 기간 수.
    window : int, optional
        최근 N 포인트만 사용. None이면 전체.
    confidence : float
        신뢰구간 수준.
    """
    s = df[indicator].dropna()
    if window:
        s = s.iloc[-window:]

    x = np.arange(len(s))
    slope, intercept = np.polyfit(x, s.values, 1)

    freq = _infer_freq(df) or "D"
    future_idx = pd.date_range(s.index[-1], periods=steps + 1, freq=freq)[1:]
    x_future = np.arange(len(s), len(s) + steps)
    forecast_vals = slope * x_future + intercept

    residuals = s.values - (slope * x + intercept)
    se = residuals.std()

    from scipy.stats import t as t_dist
    t_val = t_dist.ppf((1 + confidence) / 2, df=len(s) - 2)
    margin = t_val * se * np.sqrt(1 + 1 / len(s))

    forecast = pd.Series(forecast_vals, index=future_idx, name=f"{indicator}_forecast")
    return ForecastResult(
        indicator=indicator,
        forecast=forecast,
        lower=forecast - margin,
        upper=forecast + margin,
        method="linear_trend",
        confidence=confidence,
    )


def arima(
    df: pd.DataFrame,
    indicator: str,
    steps: int = 4,
    order: tuple = (1, 1, 1),
    confidence: float = 0.95,
) -> ForecastResult:
    """ARIMA 예측."""
    try:
        from statsmodels.tsa.arima.model import ARIMA
    except ImportError:
        raise ImportError("pip install statsmodels 를 먼저 실행하세요.")

    s = df[indicator].dropna()
    pred = ARIMA(s, order=order).fit().get_forecast(steps=steps)
    ci = pred.conf_int(alpha=1 - confidence)

    freq = _infer_freq(df) or "D"
    future_idx = pd.date_range(s.index[-1], periods=steps + 1, freq=freq)[1:]

    return ForecastResult(
        indicator=indicator,
        forecast=pd.Series(pred.predicted_mean.values, index=future_idx),
        lower=pd.Series(ci.iloc[:, 0].values, index=future_idx),
        upper=pd.Series(ci.iloc[:, 1].values, index=future_idx),
        method="arima",
        confidence=confidence,
    )


def ma_extension(
    df: pd.DataFrame,
    indicator: str,
    window: int = 4,
    steps: int = 4,
) -> ForecastResult:
    """마지막 이동평균값 수평 연장."""
    s = df[indicator].dropna()
    last_ma = s.rolling(window).mean().iloc[-1]
    roll_std = s.rolling(window).std().iloc[-1]

    freq = _infer_freq(df) or "D"
    future_idx = pd.date_range(s.index[-1], periods=steps + 1, freq=freq)[1:]
    forecast = pd.Series([last_ma] * steps, index=future_idx)

    return ForecastResult(
        indicator=indicator,
        forecast=forecast,
        lower=forecast - 2 * roll_std,
        upper=forecast + 2 * roll_std,
        method="ma_extension",
    )
